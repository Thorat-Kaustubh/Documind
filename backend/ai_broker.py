import os
import json
from typing import Optional, Dict, Any
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIBroker:
    """
    Documind AI Broker: Routes tasks between Groq and Gemini.
    Optimized for Speed (Groq), Context (Gemini Pro), and Rapid Visuals (Gemini Flash).
    """
    def __init__(self):
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Models configuration based on verified performance
        self.models = {
            "fast": "llama-3.3-70b-versatile",    # Groq
            "deep": "gemini-2.5-pro",             # Gemini Pro
            "visual": "gemini-2.5-flash"          # Gemini Flash
        }

    async def execute_task(self, task: str, provider_mode: str = "fast", raw_context: str = "") -> Dict[str, Any]:
        """
        Executes a task using the selected provider mode.
        Modes: 'fast' (Groq), 'deep' (Compressed Groq), 'visual' (Gemini Flash)
        """
        print(f"Routing task with mode: {provider_mode}...")
        
        try:
            if provider_mode == "fast":
                return await self._call_groq(task)
            elif provider_mode == "deep":
                # Stage 1: Compress Context
                compressed_context = await self._compress_prompt(raw_context) if raw_context else ""
                enriched_task = f"COMPRESSED MARKET INTELLIGENCE:\n{compressed_context}\n\nRESEARCH TASK: {task}"
                return await self._call_groq(enriched_task)
            elif provider_mode == "visual":
                return await self._call_gemini(task, self.models["visual"])
            else:
                return {"error": f"Unknown provider mode: {provider_mode}"}
        except Exception as e:
            return {"error": str(e)}

    async def _compress_prompt(self, context: str, is_file: bool = False) -> str:
        """
        Compresses/Distills raw text or file content into a high-density financial format.
        Optimized for Technical Indicators, Price Targets, Guidance, and Balance Sheet metrics.
        """
        print(f"Compacting {'file data' if is_file else 'market intelligence'}...")
        
        target_focus = "Balance Sheet: Cash Flow, Debt/Equity, Revenue growth, and Margin trends." if is_file else \
                       "Market Drivers: Tickers, Technical Indicators (RSI/Support), and Guidance."
        
        distillation_prompt = f"""
        Extract and condense the following financial intelligence into a high-density, facts-only report.
        FOCUS AREA: {target_focus}
        
        Strictly prioritize the following:
        - TICKERS & PRICE TARGETS: Key symbols and analyst price levels.
        - TECHNICALS: RSI levels, Support/Resistance, Moving Average crossovers.
        - GUIDANCE: Earnings upgrades/downgrades or revenue percentage shifts.
        - FUNDAMENTALS: Debt ratios, Cash reserves, Operating Margins (if available).
        
        Remove all qualitative fluff, introductions, and filler text.
        RAW DATA: {context[:20000]}
        """
        
        # Use a faster, cheaper model for distillation
        response = self.gemini_client.models.generate_content(
            model=self.models["visual"],
            contents=distillation_prompt
        )
        return response.text

    async def _call_groq(self, task: str) -> Dict[str, Any]:
        completion = self.groq_client.chat.completions.create(
            model=self.models["fast"],
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": task}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

    async def _call_gemini(self, task: str, model_id: str) -> Dict[str, Any]:
        response = self.gemini_client.models.generate_content(
            model=model_id,
            config={
                'system_instruction': self._get_system_prompt(),
                'response_mime_type': 'application/json'
            },
            contents=task
        )
        return json.loads(response.text)

    def _get_system_prompt(self) -> str:
        """
        Returns the unified system prompt for all LLMs to ensure consistent output.
        """
        return """
        You are Documind, an advanced financial intelligence engine.
        Analyze the provided data or query and return a strict JSON response.
        
        Return format:
        {
          "summary": "Detailed financial analysis or response text.",
          "sentiment": { 
              "score": 0.0 to 1.0 (0=bearish, 1=bullish), 
              "label": "Bullish|Bearish|Neutral", 
              "confidence": 0.0 to 1.0 
          },
          "visuals": {
            "type": "line|bar|pie|heatmap|candlestick|none",
            "chart_data": [
                // line/bar/pie: {"name": "label", "value": 123}
                // heatmap: {"name": "Sector", "intensity": 0-100, "label": "Text"}
                // candlestick: {"name": "Time", "open": O, "high": H, "low": L, "close": C}
            ],
            "insight_cards": [
                {"title": "Key Insight", "content": "Brief detail"}
            ]
          },
          "sources": ["External Source A", "Data Point B"]
        }
        
        Visualization Rules:
        - For 'candlestick', ensure 5 data points per object (name, open, high, low, close).
        - For 'heatmap', 'intensity' represents temperature/volume (0-100).
        - If no chart is applicable, set visual type to "none" and chart_data to [].
        Always provide professional, data-driven insights.
        """

if __name__ == "__main__":
    import asyncio
    broker = AIBroker()
    async def test():
        res = await broker.execute_task("Analyze the sentiment for Nifty 50 today", provider_mode="fast")
        print(json.dumps(res, indent=2))
    
    asyncio.run(test())
