import os
import json
import re
import time
import asyncio
import hashlib
from typing import Optional, Dict, Any, List
from google import genai
from google import genai
from groq import AsyncGroq
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

import logging
from backend.config import settings
from backend.src.shared.compression import compressor
from backend.src.shared.configuration import config
from backend.src.shared.schemas import validate_visuals, VisualIntelligence

logger = logging.getLogger("documind.broker")

class AIBroker:
    """
    ULTRA-SONIC PERFORMANCE ENGINE
    - Core Synthesis routed to Groq (Sub-500ms TTL).
    - Gemini reserved for 'Deep' RAG reasoning (1s+ TTL).
    - Fix: Proactive Concurrency Control (Semaphore).
    - Fix: Semantic Caching Layer (Memory + Disk).
    """
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        # PROACTIVE CONCURRENCY CONTROL (Fix 3)
        self.gemini_semaphore = asyncio.Semaphore(3)
        
        # SEMANTIC CACHING LAYER (Memory First, Disk Fallback)
        self.memory_cache = {}
        self.cache_dir = settings.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.models = {
            "core": config.core_model,
            "fast": config.fast_model,
            "grounding": config.grounding_model,
            "research": config.research_model,
            "chat": config.chat_model
        }
        
        # TAVILY HYBRID DISCOVERY (Fix 4)
        self.tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY) if settings.TAVILY_API_KEY else None

    def _get_cache_key(self, task: str, context: str, ticker: Optional[str] = None) -> str:
        """Generate a stable hash for caching."""
        payload = f"{ticker or ''}|{task}|{context[:5000]}" # Cache based on task and first 5k context
        return hashlib.sha256(payload.encode()).hexdigest()

    def _get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        # Layer 1: Memory
        if key in self.memory_cache:
            return self.memory_cache[key]
            
        # Layer 2: Disk
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                    self.memory_cache[key] = data # Pop back to memory
                    return data
            except: return None
        return None

    def _save_to_cache(self, key: str, data: Dict[str, Any]):
        self.memory_cache[key] = data
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f)
        except: pass

    async def compress_context(self, context: str) -> str:
        """Compress large context into a semantic digest using the SemanticCompressor."""
        return await compressor.compress_async(context)

    async def execute_task(self, task: str, provider_mode: str = "core", raw_context: str = "", ticker: Optional[str] = None, retries: int = 2, custom_system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Hyper-Fast Orchestration with Caching, Compression, and Resilience."""
        
        # 1. CACHE CHECK
        cache_key = self._get_cache_key(task, raw_context, ticker)
        cached = self._get_cached_response(cache_key)
        if cached and not custom_system_prompt:
            logger.info(f"Cache Hit for {ticker or 'Task'}")
            return cached

        # 2. ADAPTIVE CONTEXT COMPRESSION (Fast Path for Small Context)
        processed_context = raw_context
        if len(raw_context) > 2000:
            processed_context = await self.compress_context(raw_context)

        # 3. HYBRID RESEARCH / GROUNDING (Tavily Speed Path)
        search_context = ""
        if provider_mode in ["grounding", "research"] and self.tavily_client:
            try:
                logger.info(f"Precision Search Initiation via Tavily for {provider_mode}")
                search_query = f"{ticker if ticker else ''} {task}"
                search_response = await asyncio.to_thread(self.tavily_client.search, query=search_query, search_depth="advanced" if provider_mode == "research" else "basic", max_results=5)
                
                for r in search_response.get('results', []):
                    search_context += f"\nSource: {r['url']}\nContent: {r['content']}\n"
            except Exception as e:
                logger.warning(f"Tavily Retrieval Failed: {e}")

        # 3. ROUTING
        if provider_mode == "core":
            res = await self._call_groq(task, context=processed_context, model=self.models["core"], system_prompt=custom_system_prompt)
        elif provider_mode == "fast":
            res = await self._call_groq(task, context=processed_context, model=self.models["fast"], system_prompt=custom_system_prompt)
        elif provider_mode == "grounding":
            full_ctx = f"{search_context}\n\n{processed_context}"
            res = await self._throttle_gemini(task, full_ctx, retries, model=self.models["grounding"], use_grounding=False, system_prompt=custom_system_prompt)
        elif provider_mode == "research":
            full_ctx = f"{search_context}\n\n{processed_context}"
            res = await self._throttle_gemini(task, full_ctx, retries, model=self.models["research"], use_grounding=False, system_prompt=custom_system_prompt)
        elif provider_mode == "chat":
            res = await self._throttle_gemini(task, processed_context, retries, model=self.models["chat"], use_grounding=False, system_prompt=custom_system_prompt)
        else:
            # Default
            res = await self._call_groq(task, context=processed_context, model=self.models["core"], system_prompt=custom_system_prompt)

        # 4. VALIDATION & PERSIST
        if "error" not in res:
            res = validate_visuals(res)
            self._save_to_cache(cache_key, res)
        
        return res

    async def _throttle_gemini(self, task: str, context: str, retries: int, model: str, use_grounding: bool = False, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        async with self.gemini_semaphore:
            for attempt in range(retries + 1):
                try:
                    res = await self._call_gemini_consolidated(task, context=context, model=model, use_grounding=use_grounding, system_prompt=system_prompt)
                    if "error" in res and "429" in str(res["error"]): raise Exception("429")
                    return res
                except Exception:
                    if attempt < retries: 
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
                        continue
                    # Hard Fallback to Groq if Gemini is pinned
                    return await self._call_groq(task, context=context, model=self.models["fast"], system_prompt=system_prompt)

    async def _call_gemini_consolidated(self, task: str, context: str = "", model: str = None, use_grounding: bool = False, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        # Truncate context to safe bounds to avoid Request Too Large errors
        model_name = model or self.models["research"]
        prompt = f"CONTEXT:\n{context[:200000]}\n\nTASK: {task}"
        generation_config = {'system_instruction': system_prompt or self._get_consolidated_prompt()}
        if use_grounding and "pro" not in model_name.lower():
            generation_config['tools'] = [{'google_search': {}}]
        try:
            response = await asyncio.to_thread(self.gemini_client.models.generate_content, model=model_name, config=generation_config, contents=prompt)
            raw_text = response.text.strip()
            
            # Resilience: Handle empty responses
            if not raw_text: return {"summary": "Gemini returned empty response.", "error": "empty_response"}

            if not raw_text.startswith('{'):
                json_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
                return json.loads(json_match.group(1)) if json_match else {"summary": raw_text}
            return json.loads(raw_text)
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate_limit" in error_str:
                return {"error": "rate_limit", "message": str(e)}
            if "400" in error_str or "token" in error_str:
                 return {"error": "bad_request_or_tokens", "message": str(e)}
            return {"error": f"gemini_failed: {str(e)}"}

    async def _call_groq(self, task: str, context: str = "", model: str = None, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Sub-200ms Async Synthesis Layer."""
        model_name = model or self.models["core"]
        prompt = f"CONTEXT:\n{context[:20000]}\n\nTASK: {task}"
        sys_p = (system_prompt or self._get_consolidated_prompt()) + ". JSON ONLY."
        try:
            chat_completion = await self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(chat_completion.choices[0].message.content)
            # Normalization
            if "summary" not in data: data["summary"] = data.get("report", "Analysis ready.")
            if "sentiment" not in data: data["sentiment"] = {"score": 0.5, "label": "Neutral"}
            return data
        except Exception as e:
             logger.error(f"Groq Synthesis Layer failed: {str(e)}")
             return {"summary": "Synthesis failed (Engine Delay).", "sentiment": {"score": 0, "label": "N/A"}}

    async def targeted_extraction(self, ticker: str, raw_dom: str) -> Dict[str, Any]:
        """Fix 1: Targeted Extraction (JSON Schema Compression)"""
        extraction_prompt = f"""
        Extract only the structured financial data from this DOM for {ticker}.
        Focus strictly on: profit_and_loss, balance_sheet, cash_flow.
        Output as a MINIFIED JSON object with clean numeric arrays and label keys.
        If any section is missing, set it to an empty object.
        """
        return await self._call_groq(extraction_prompt, context=raw_dom[:40000], model=self.models["fast"])

    def _get_consolidated_prompt(self) -> str:
        return """
        Act as the 'Documind Pulse Engine' (High-Fidelity Financial Intelligence).
        
        STRICT OPERATIONAL RULES:
        1. GROUND TRUTH ONLY: Extract information strictly from the provided CONTEXT. If context is missing data, explicitly state "Information not present in sources."
        2. MANDATORY CITATIONS: Every analytical claim MUST be followed by a citation in [Source Title/URL] format.
        3. ACCURACY: Do not synthesize external knowledge unless it is common industry standard (e.g. standard accounting definitions).
        
        Return JSON matching this schema:
        {
          "summary": "Professional analysis markdown. MUST use citations like [Ref: Annual Report 2024]. No emojis.",
          "sentiment": { "score": 1.0 to 0.0, "label": "Bullish|Bearish|Neutral" },
          "visuals": { 
              "type": "line|bar|pie|area|radar|none", 
              "chart_data": [{"label": "string", "value": number}], 
              "insight_cards": [{"title": "string", "content": "string", "sentiment": "positive|negative|neutral"}]
          },
          "sources_verified": ["List all unique sources used for this analysis"]
        }
        """

    async def stream_task(self, task: str, raw_context: str = ""):
        prompt = f"CONTEXT:\n{raw_context[:15000]}\n\nQUERY: {task}"
        stream = await self.groq_client.chat.completions.create(
            model=self.models["fast"],
            messages=[{"role": "system", "content": "You are Documind Elite. Direct fact-only summary. No emojis."}, {"role": "user", "content": prompt}],
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
