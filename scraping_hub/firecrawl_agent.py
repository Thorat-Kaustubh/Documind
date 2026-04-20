import os
import httpx
import json
import asyncio
from typing import Optional, Dict, Any, List
from backend.src.execution.llm_engine import LLMEngine

class FirecrawlAgent:
    """
    Transforms complex, JS-heavy financial pages into structured intelligence.
    Optimized for LLM reasoning and machine-validated pipelines.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.endpoint = "https://api.firecrawl.dev/v1/scrape"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.llm_engine = LLMEngine()
        
        # Load the "Fidelity First" rules
        prompt_path = os.path.join(os.path.dirname(__file__), "firecrawl_system_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except:
            self.system_prompt = "You are a financial data extraction engine. Extract structured data from markdown."

    async def extract_intelligence(self, url: str, goal: str = "full content", source_type: str = "news") -> Dict[str, Any]:
        """
        Primary Objective: Convert messy pages into signal-rich content.
        Uses the provided High-Fidelity System Prompt for Step 3.
        """
        if not self.api_key:
            return self._trigger_fallback("MISSING_API_KEY", "Firecrawl API key not configured.")

        # Step 1 & 2: Page Understanding & Content Cleaning
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
            "waitFor": 3000 # Wait for JS rendering
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                print(f"📡 [FirecrawlAgent] Starting High-Fidelity extraction for: {url}")
                response = await client.post(self.endpoint, json=payload, headers=self.headers)
                
                if response.status_code == 402:
                    return self._trigger_fallback("CREDIT_EXHAUSTED", "Firecrawl credits depleted.")
                
                response.raise_for_status()
                raw_data = response.json()
                
                if not raw_data.get("success"):
                    return self._trigger_fallback("EXTRACTION_FAILED", raw_data.get("error", "Unknown"))

                markdown = raw_data.get("data", {}).get("markdown", "")
                
                # Step 3: Financial Intelligence Extraction (Using AI Broker)
                print(f"🧠 [FirecrawlAgent] Running Step 3: Intelligence Extraction...")
                
                # We use the system prompt provided in 'firecrawl_system_prompt.txt'
                # The AI Broker will process the clean markdown into the required JSON.
                intelligence = await self.llm_engine.generate_response(
                    task=f"EXTRACTION GOAL: {goal}. SOURCE TYPE: {source_type}. URL: {url}",
                    mode="core",
                    context=markdown,
                    system_prompt=self.system_prompt
                )

                # Step 4: Validate and return structured output
                if "error" in intelligence:
                    return self._trigger_fallback("AI_REASONING_FAILED", intelligence["error"])

                return intelligence

            except Exception as e:
                return self._trigger_fallback("SYSTEM_ERROR", str(e))

    def _trigger_fallback(self, error_code: str, reason: str) -> Dict[str, Any]:
        """
        Signal for fault-tolerant fallback.
        """
        print(f"⚠️ [Firecrawl-Error] {error_code}: {reason}")
        return {
            "status": "FAILED_LOW_CONFIDENCE",
            "reason": f"[{error_code}] {reason}",
            "action": "TRIGGER_FALLBACK: FreeNewsScout"
        }

if __name__ == "__main__":
    agent = FirecrawlAgent()
    async def test():
        url = "https://www.moneycontrol.com/india/stockpricequote/refineries/relianceindustries/RI"
        res = await agent.extract_intelligence(url, source_type="financial", goal="full metrics and tables")
        print(json.dumps(res, indent=2))
    
    asyncio.run(test())
