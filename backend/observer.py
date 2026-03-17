import asyncio
import os
from scraping_hub.firecrawl_scout import FirecrawlScout
from ai_broker import AIBroker
from database.vector_storage import VectorStorage
from database.postgres_sync import PostgresSync

class DocumindIntelligenceHub:
    """
    Hybrid Intelligence Hub: 
    - Firecrawl for Ratios (Screener) & Deep Reads (NSE/News content).
    - Future: Scrapy for bulk headline discovery.
    """
    def __init__(self):
        self.scout = FirecrawlScout()
        self.broker = AIBroker()
        self.vector_db = VectorStorage()
        self.pg_db = PostgresSync()

    async def deep_analyze_company(self, company_name: str, ticker: str):
        """
        Performs a high-fidelity intelligence sweep.
        """
        print(f"\n🚀 Initiating Multi-Source Intelligence for: {company_name}")
        
        # 1. Fundamental Data (Screener.in)
        screener_url = f"https://www.screener.in/company/{ticker}/"
        print(f"📡 Fetching Fundamentals from Screener: {screener_url}")
        fundamental_data = self.scout.scrape_url(screener_url)
        
        # 2. Market Sentiment (ET/Moneycontrol Search)
        print(f"🛰️ Scouting Market Sentiment for {company_name}...")
        news_intel = self.scout.search_and_scrape(f"latest news Economic Times Moneycontrol {company_name}", limit=2)

        # 3. Combine and Synthesize
        raw_context = f"""
        FUNDAMENTAL DATA (SCREENER):
        {fundamental_data.get('markdown', 'N/A')[:10000]}
        
        RECENT MARKET NEWS:
        {str(news_intel)[:10000]}
        """
        
        print("🧠 Synthesizing Multi-Source Intelligence...")
        analysis = await self.broker.execute_task(
            task=f"Analyze {company_name} for investment risk vs opportunity.",
            provider_mode="deep",
            raw_context=raw_context
        )

        # 4. Storage
        self.vector_db.add_document(
            text=analysis.get("summary", ""),
            metadata={"symbol": ticker, "source": "Multi-Source Intelligence"},
            doc_id=f"intel_{ticker}_{int(asyncio.get_event_loop().time())}"
        )
        
        print("✅ Intelligence Report stored in Cloud.")
        return analysis

if __name__ == "__main__":
    hub = DocumindIntelligenceHub()
    # Test for Reliance or TCS
    asyncio.run(hub.deep_analyze_company("Reliance Industries", "RELIANCE"))
