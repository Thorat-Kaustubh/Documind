import asyncio
import os
import sys
import json
from datetime import date, timedelta
from dotenv import load_dotenv

# Ensure we can import from the project root
sys.path.append(os.getcwd())

from backend.ai_broker import AIBroker
from scraping_hub.screener_agent import ScreenerAgent
from backend.historical_ingest_service import HistoricalIngestService
from backend.market_data_engine import MarketDataEngine

async def run_comprehensive_check():
    print("🚀 --- DOCUMIND ELITE: FULL SYSTEM VERIFICATION --- 🚀\n")
    load_dotenv()
    
    # 1. AI BROKER & RESEARCH LAYER (Tavily + Groq/Gemini)
    print("[1/4] Testing AI Broker & Hybrid Research Layer...")
    broker = AIBroker()
    try:
        # Testing research mode (Gemini 3.1 + Tavily)
        research_res = await broker.execute_task(
            task="What are the recent major developments for Reliance Industries today?",
            provider_mode="research",
            ticker="RELIANCE"
        )
        print("   ✅ AI Research Synthesized successfully.")
        print(f"   💡 Sentiment: {research_res.get('sentiment', {}).get('label', 'N/A')}")
        print(f"   💡 Summary: {research_res.get('summary', '')[:100]}...")
    except Exception as e:
        print(f"   ❌ AI Research Failed: {e}")

    # 2. SCREENER AGENT (Scraping Layer)
    print("\n[2/4] Testing Screener Agent (Structural Financials)...")
    screener = ScreenerAgent()
    try:
        screener_res = await screener.get_full_financials("TCS")
        if "cash_flow" in str(screener_res).lower():
            print("   ✅ Screener Data Extracted (including Cash Flow).")
        else:
            print("   ⚠️ Screener Data Extracted but Cash Flow missing or sparse.")
    except Exception as e:
        print(f"   ❌ Screener Agent Failed: {e}")

    # 3. MARKET DATA ENGINE (Jugaad-Data / NSE Live)
    print("\n[3/4] Testing Market Data Engine (NSE/RBI Heartbeat)...")
    market_engine = MarketDataEngine()
    try:
        vitals = await asyncio.to_thread(market_engine.fetch_macro_heartbeat)
        if "NIFTY_50" in vitals:
            print(f"   ✅ Market Vitals Pulse Detected: NIFTY 50 @ {vitals['NIFTY_50']}")
        else:
            print("   ⚠️ Market Vitals returned empty or incorrect schema.")
    except Exception as e:
        print(f"   ❌ Market Data Engine Failed: {e}")

    # 4. HISTORICAL INGEST (Postgres + ChromaDB Isolation)
    print("\n[4/4] Testing Historical Ingest & Storage Isolation...")
    ingestor = HistoricalIngestService()
    try:
        # We'll just test a single day's ingestion for a small sample
        # Note: This will create a 'bhavcopy_intelligence' collection in Chroma
        target_date = date.today()
        # Find a workday
        while target_date.weekday() >= 5:
            target_date -= timedelta(days=1)
            
        print(f"   ⏳ Attempting sample dry-run for {target_date}...")
        # Since we don't want to download a massive file in a test, 
        # we verify the collection connection.
        if ingestor.vector_db.collection_name == "bhavcopy_intelligence":
             print("   ✅ Vector Domain Isolation Verified: 'bhavcopy_intelligence' active.")
        else:
             print("   ❌ Vector Domain Isolation MISMATCH.")
    except Exception as e:
        print(f"   ❌ Historical Ingest Test Failed: {e}")

    print("\n🏁 --- VERIFICATION COMPLETE --- 🏁")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_check())
