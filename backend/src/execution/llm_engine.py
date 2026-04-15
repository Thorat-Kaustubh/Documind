import json
import logging
import asyncio
from typing import Dict, Any, Optional
from google import genai
from groq import AsyncGroq
from backend.config import settings
from backend.src.shared.configuration import config

logger = logging.getLogger("documind.execution.llm")

class LLMEngine:
    """
    SECTION 5.3: LLM ENGINE
    Standardized interface for low-latency and deep reasoning models.
    """
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.gemini_semaphore = asyncio.Semaphore(5)
        
        self.models = {
            "fast": config.fast_model,
            "core": config.core_model,
            "deep": config.research_model
        }
        
        # Documind V2: Internalized JSONB-First System Prompt
        self.SCHEMA_GUARD = """
        IMPORTANT: Your response MUST be valid JSONB-indexable data.
        OUTPUT SCHEMA:
        {
          "summary": "STRING",
          "intent": "STRING (e.g. ANALYZE, RESEARCH, SQL_QUERY)",
          "confidence": FLOAT (0.0-1.0),
          "entities": {"company": "STRING", "metrics": ["ARRAY"]},
          "execution_plan": [{"step": "STRING", "type": "sql|rag|llm", "params": {}}],
          "metadata": {"version": "v2", "model": "STRING", "timestamp": "ISO8601"}
        }
        """

    async def generate_response(self, task: str, context: str, mode: str = "fast", system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Routes the task to the appropriate model based on mode.
        """
        if mode == "deep":
            return await self._call_gemini(task, context, system_prompt)
        return await self._call_groq(task, context, system_prompt)

    async def _call_gemini(self, task: str, context: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        prompt = f"CONTEXT:\n{context[:200000]}\n\nTASK: {task}"
        config_gen = {
            'system_instruction': (system_prompt or "Act as Documind Analyst.") + self.SCHEMA_GUARD,
            'response_mime_type': 'application/json'
        }
        
        async with self.gemini_semaphore:
            try:
                response = await asyncio.to_thread(
                    self.gemini_client.models.generate_content, 
                    model=self.models["deep"], 
                    config=config_gen, 
                    contents=prompt
                )
                data = json.loads(response.text)
                # Hardening: Ensure minimal structure
                if "summary" not in data: data["summary"] = response.text[:500]
                return data
            except Exception as e:
                logger.error(f"LLM Engine: Gemini failure: {e}")
                return {"summary": "Error during analysis", "error": "deep_reasoning_failed", "message": str(e)}

    async def _call_groq(self, task: str, context: str, system_prompt: Optional[str]) -> Dict[str, Any]:
        prompt = f"CONTEXT:\n{context[:30000]}\n\nTASK: {task}"
        try:
            chat_completion = await self.groq_client.chat.completions.create(
                model=self.models["core"],
                messages=[
                    {"role": "system", "content": (system_prompt or "Act as Documind.") + self.SCHEMA_GUARD},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(chat_completion.choices[0].message.content)
            # Hardening: Ensure minimal structure
            if "summary" not in data: data["summary"] = "Structure mismatch in synthesis."
            return data
        except Exception as e:
            logger.error(f"LLM Engine: Groq failure: {e}")
            return {"summary": "Service unavailable", "error": "synthesis_failed", "message": str(e)}
