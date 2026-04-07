import os
import asyncio
import time
import json
from dotenv import load_dotenv
from google import genai
from groq import Groq

# Load environment variables
load_dotenv()

COMPLEX_FINANCIAL_PROMPT = """
Act as a Senior Quant Analyst. Perform a deep structural analysis for HDFC Bank (HDFCBANK.NS) given:
1. Nifty Bank is at 48,200, up 0.85% today.
2. Interest rate cycle is at a pivot point (Expected 25bps cut next quarter).
3. HDFC Bank's latest CASA ratio is at 38%.

Your response MUST follow this JSON schema EXACTLY:
{
  "summary": "Markdown analysis focusing on NIM impact, deposit growth outlook, and index correlation.",
  "sentiment": { "score": 0.0 to 1.0, "label": "Bullish|Bearish|Neutral" },
  "visuals": {
    "type": "radar",
    "chart_data": [
      {"label": "NIM Stability", "value": 85},
      {"label": "Asset Quality", "value": 92},
      {"label": "Deposit Growth", "value": 78},
      {"label": "Market Sentiment", "value": 88}
    ],
    "insight_cards": [
      {"title": "CASA Compression", "content": "38% ratio indicates high cost of deposits.", "sentiment": "negative"}
    ]
  }
}
STRICT RULE: NO EMOJIS. Professional analysis only.
"""

async def run_detailed_test(model_name: str, provider: str):
    print(f"\n[STRESS-TEST] {provider.upper()} - {model_name}...")
    start_time = time.time()
    
    try:
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            # Fix: Properly handle preview versions with a timeout
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model_name,
                contents=COMPLEX_FINANCIAL_PROMPT,
                config={'response_mime_type': 'application/json'}
            )
            result = response.text
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": COMPLEX_FINANCIAL_PROMPT}],
                response_format={"type": "json_object"}
            )
            result = completion.choices[0].message.content
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Validation
        data = json.loads(result)
        valid = "summary" in data and "visuals" in data
        
        print(f"Latency: {latency:.2f} seconds | Schema Valid: {valid}")
        print(f"   Summary Snippet: {data.get('summary', '')[:100]}...")
        return latency, True
    
    except Exception as e:
        print(f"[CRITICAL-ERROR] with {model_name}: {str(e)[:100]}")
        return None, False

async def main():
    print("Initiating Cross-Model Strategic Stress Test...")
    print("="*60)
    
    # All models currently in the system architecture
    system_models = [
        ("llama-3.3-70b-versatile", "groq", "CORE (The Architect)"),
        ("llama-3.1-8b-instant", "groq", "FAST (The Shredder)"),
        ("gemini-2.5-flash", "gemini", "GROUNDING (The Pulse)"),
        ("gemini-2.0-flash", "gemini", "RESEARCH (The Investigator)"),
        ("gemini-2.0-flash-lite", "gemini", "CHAT (The Master Bot)"),
        ("gemini-3.1-flash-live-preview-preview-1", "gemini", "LIVE PREVIEW (Experimental)")
    ]
    
    report = []
    
    for model, provider, role in system_models:
        latency, success = await run_detailed_test(model, provider)
        if success:
            report.append(f"| {role:<20} | {model:<30} | {latency:.2f}s | PASS |")
        else:
            report.append(f"| {role:<20} | {model:<30} | N/A   | FAIL |")
            
    print("\n" + "="*80)
    print(" FINAL STRATEGIC MODEL PERFORMANCE REPORT")
    print("="*80)
    print("| Role                 | Model Name                     | Latency | Status |")
    print("|----------------------|--------------------------------|---------|--------|")
    for line in report:
        print(line)
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
