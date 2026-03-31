import os
import json
import re
import time
import asyncio
import hashlib
from typing import Optional, Dict, Any, List
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIBroker:
    """
    ULTRA-SONIC PERFORMANCE ENGINE
    - Core Synthesis routed to Groq (Sub-500ms TTL).
    - Gemini reserved for 'Deep' RAG reasoning (1s+ TTL).
    - Fix: Proactive Concurrency Control (Semaphore).
    - Fix: Semantic Caching Layer.
    """
    def __init__(self):
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # PROACTIVE CONCURRENCY CONTROL (Fix 3)
        self.gemini_semaphore = asyncio.Semaphore(3)
        
        # SEMANTIC CACHING LAYER (Fix 2)
        self.cache_dir = ".ai_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.models = {
            "core": "llama-3.3-70b-versatile",
            "fast": "llama-3.1-8b-instant",
            "grounding": "gemini-2.5-flash-lite",
            "research": "gemini-3.1-flash-lite-preview"
        }

    def _get_cache_key(self, task: str, context: str, ticker: Optional[str] = None) -> str:
        """Generate a stable hash for caching."""
        payload = f"{ticker or ''}|{task}|{context[:5000]}" # Cache based on task and first 5k context
        return hashlib.sha256(payload.encode()).hexdigest()

    def _get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    return json.load(f)
            except: return None
        return None

    def _save_to_cache(self, key: str, data: Dict[str, Any]):
        cache_path = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f)
        except: pass

    async def execute_task(self, task: str, provider_mode: str = "core", raw_context: str = "", ticker: Optional[str] = None, retries: int = 1) -> Dict[str, Any]:
        """Hyper-Fast Orchestration with Caching and Throttling."""
        
        # 1. CACHE CHECK
        cache_key = self._get_cache_key(task, raw_context, ticker)
        cached = self._get_cached_response(cache_key)
        if cached:
            print(f"[*] [AIBroker] Cache Hit for {ticker or 'Task'}")
            return cached

        # 2. ROUTING
        if provider_mode == "core":
            res = await self._call_groq(task, context=raw_context, model=self.models["core"])
        elif provider_mode == "fast":
            res = await self._call_groq(task, context=raw_context, model=self.models["fast"])
        elif provider_mode == "grounding":
            res = await self._throttle_gemini(task, raw_context, retries, model=self.models["grounding"], use_grounding=True)
        elif provider_mode == "research":
            res = await self._throttle_gemini(task, raw_context, retries, model=self.models["research"], use_grounding=True)
        else:
            # Default
            res = await self._call_groq(task, context=raw_context, model=self.models["core"])

        # 3. PERSIST
        if "error" not in res:
            self._save_to_cache(cache_key, res)
        
        return res

    async def _throttle_gemini(self, task: str, context: str, retries: int, model: str, use_grounding: bool = False) -> Dict[str, Any]:
        async with self.gemini_semaphore:
            for attempt in range(retries + 1):
                try:
                    res = await self._call_gemini_consolidated(task, context=context, model=model, use_grounding=use_grounding)
                    if "error" in res and "429" in str(res["error"]): raise Exception("429")
                    return res
                except Exception:
                    if attempt < retries: 
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
                        continue
                    # Hard Fallback to Groq if Gemini is pinned
                    return await self._call_groq(task, context=context, model=self.models["fast"])

    async def _call_gemini_consolidated(self, task: str, context: str = "", model: str = "gemini-2.5-flash-lite", use_grounding: bool = False) -> Dict[str, Any]:
        # Gemini handles larger context naturally (up to 1M), but we constrain for speed
        prompt = f"CONTEXT:\n{context[:60000]}\n\nTASK: {task}"
        config = {'system_instruction': self._get_consolidated_prompt()}
        if use_grounding: config['tools'] = [{'google_search': {}}]
        try:
            response = await asyncio.to_thread(self.gemini_client.models.generate_content, model=model, config=config, contents=prompt)
            raw_text = response.text.strip()
            json_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            return json.loads(json_match.group(1)) if json_match else {"summary": raw_text}
        except Exception as e: 
            return {"error": f"gemini_failed: {str(e)}"}

    async def _call_groq(self, task: str, context: str = "", model: str = None) -> Dict[str, Any]:
        """Sub-500ms Synthesis Layer."""
        model_name = model or self.models["core"]
        prompt = f"CONTEXT:\n{context[:20000]}\n\nTASK: {task}"
        try:
            chat_completion = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self._get_consolidated_prompt() + ". JSON ONLY."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(chat_completion.choices[0].message.content)
            # Normalization
            if "summary" not in data: data["summary"] = data.get("report", "Analysis ready.")
            if "sentiment" not in data: data["sentiment"] = {"score": 0.5, "label": "Neutral"}
            return data
        except Exception:
             return {"summary": "Synthesis failed (Engine Delay).", "sentiment": {"score": 0, "label": "N/A"}}

    async def targeted_extraction(self, ticker: str, raw_dom: str) -> Dict[str, Any]:
        """Fix 1: Targeted Extraction (JSON Schema Compression)"""
        extraction_prompt = f"""
        Extract only the structured financial data from this DOM for {ticker}.
        Ignore all HTML tags, noise, and navigation. 
        Focus strictly on: profit_and_loss, balance_sheet, cash_flow.
        Output as a MINIFIED JSON object with clean numeric arrays and label keys.
        """
        return await self._call_groq(extraction_prompt, context=raw_dom[:40000], model=self.models["fast"])

    def _get_consolidated_prompt(self) -> str:
        return """
        Act as the 'Documind Pulse Engine'. Return JSON strictly:
        {
          "summary": "Professional analysis markdown. No emojis. Direct facts.",
          "sentiment": { "score": 0.5, "label": "Neutral" },
          "visuals": { "type": "line|bar|pie|none", "chart_data": [], "insight_cards": [] }
        }
        """

    async def stream_task(self, task: str, raw_context: str = ""):
        prompt = f"CONTEXT:\n{raw_context[:15000]}\n\nQUERY: {task}"
        stream = self.groq_client.chat.completions.create(
            model=self.models["fast"],
            messages=[{"role": "system", "content": "You are Documind Elite. Direct fact-only summary. No emojis."}, {"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
