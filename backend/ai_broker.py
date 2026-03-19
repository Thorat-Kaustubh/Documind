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
        Executes a task with integrated NER (Entity Extraction) if context is provided.
        """
        print(f"Routing task with mode: {provider_mode}...")
        
        # If we have raw context (e.g. from scraping), extract entities first to clean it up
        entities = {}
        if raw_context:
            try:
                entities = await self.extract_entities(raw_context)
            except: pass
        
        try:
            if provider_mode == "fast":
                return await self._call_groq(task, context=raw_context)
            elif provider_mode == "deep":
                # Stage 1: Compress Context
                compressed_context = await self._compress_prompt(raw_context) if raw_context else ""
                enriched_task = f"COMPRESSED MARKET INTELLIGENCE:\n{compressed_context}\n\nRESEARCH TASK: {task}"
                return await self._call_groq(enriched_task)
            elif provider_mode == "visual":
                return await self._call_gemini(task, self.models["visual"], context=raw_context)
            else:
                return {"error": f"Unknown provider mode: {provider_mode}"}
        except Exception as e:
            return {"error": str(e)}

    async def stream_task(self, task: str, raw_context: str = ""):
        """
        SSE Streaming: Provides millisecond response times by streaming the intelligence summary.
        """
        prompt = f"CONTEXT:\n{raw_context[:10000]}\n\nUSER QUERY: {task}"
        
        # We use Groq for the fastest streaming experience
        stream = self.groq_client.chat.completions.create(
            model=self.models["fast"],
            messages=[
                {"role": "system", "content": "You are Documind Elite. Provide a rich, markdown-heavy financial analysis. Cite sources explicitly. Start directly with the analysis."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

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

    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Performs Zero-Shot NER to identify critical financial entities.
        Replaces the need for a custom-trained NER model.
        """
        extraction_prompt = f"""
        Act as a Financial Data Scientist. Extract structured entities from the text below.
        
        TEXT: {text[:5000]}
        
        Return ONLY a JSON object with:
        {{
            "tickers": ["SYMBOL1", "SYMBOL2"],
            "monetary_values": ["Value (Context)", "..."],
            "key_people": ["Name (Title)", "..."],
            "strategic_events": ["Mergers", "Earnings", "Lawsuits"]
        }}
        """
        try:
            response = self.gemini_client.models.generate_content(
                model=self.models["visual"],
                config={'response_mime_type': 'application/json'},
                contents=extraction_prompt
            )
            return json.loads(response.text)
        except:
            return {"tickers": [], "monetary_values": []}

    async def _call_groq(self, task: str, context: str = "") -> Dict[str, Any]:
        prompt = f"CONTEXT:\n{context}\n\nTASK: {task}" if context else task
        completion = self.groq_client.chat.completions.create(
            model=self.models["fast"],
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

    async def _call_gemini(self, task: str, model_id: str, context: str = "") -> Dict[str, Any]:
        prompt = f"CONTEXT:\n{context}\n\nTASK: {task}" if context else task
        response = self.gemini_client.models.generate_content(
            model=model_id,
            config={
                'system_instruction': self._get_system_prompt(),
                'response_mime_type': 'application/json'
            },
            contents=prompt
        )
        return json.loads(response.text)

    def _get_system_prompt(self) -> str:
        """
        Returns the unified system prompt for all LLMs to ensure consistent output.
        """
        return """
        You are Documind Elite, a world-class Financial Intelligence Assistant comparable to Bloomberg Terminal mixed with Gemini/ChatGPT.
        
        GOAL: Provide multi-layered analysis that combines hard market data, real-time news sentiment, and deep-document RAG.
        
        RULES:
        1. CITATION: Every numerical fact or strategic claim MUST be cited (e.g., "[Source: Q3 10-Q]").
        2. STRUCTURE: Use professional headers: # MARKET PULSE, # STRATEGIC INSIGHT, # RISK ASSESSMENT.
        3. MULTI-LLM REASONING: If 'deep' mode is used, cross-reference multiple data points before drawing a conclusion.
        4. JSON FORMAT: You MUST return a valid JSON object with the following structure:
        
        {
          "summary": "Full formatted markdown response with headers and citations.",
          "sentiment": { "score": 0.1-0.9, "label": "Bullish/Bearish", "confidence": 0.8 },
          "visuals": {
            "type": "line|bar|pie|candlestick|none",
            "chart_data": [], // Ensure data adheres to recharts specifications
            "insight_cards": [{"title": "Alert", "content": "Critical detail"}]
          },
          "follow_up_questions": ["What is their debt maturity profile?", "How does this compare to sector peers?"],
          "sources": ["Screener.in", "Tavily Search", "PDF RAG Index"]
        }
        
        TONE: Objective, precise, and data-driven. Avoid hype.
        """

if __name__ == "__main__":
    import asyncio
    broker = AIBroker()
    async def test():
        res = await broker.execute_task("Analyze the sentiment for Nifty 50 today", provider_mode="fast")
        print(json.dumps(res, indent=2))
    
    asyncio.run(test())
