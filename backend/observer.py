import asyncio
import os
import time
from datetime import datetime
from scraping_hub.firecrawl_scout import FirecrawlScout
from ai_broker import AIBroker
from database.vector_storage import VectorStorage
from database.postgres_sync import PostgresSync
from web_intelligence import WebIntelligence
from backend.market_data_engine import MarketDataEngine

class DocumindKnowledgeGraph:
    """
    Documind Knowledge Engine: MULTI-ASSET DISCOVERY FLEET
    Implements Crawl -> Index -> Serve for:
    - EQUITY, IPOs, MUTUAL FUNDS, COMMODITIES, NEWS
    """
    def __init__(self):
        self.scout = FirecrawlScout()
        self.broker = AIBroker()
        self.vector_db = VectorStorage()
        self.pg_db = PostgresSync()
        self.web_intel = WebIntelligence()
        self.market_engine = MarketDataEngine()
        
        # Expanded multi-asset monitoring
        self.watchlists = {
            "EQUITY": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "NVDA", "AAPL", "TSLA"],
            "COMMODITIES": ["GOLD", "BRENT_OIL"],
            "FOREX": ["USD_INR"],
            "MUTUAL_FUNDS": ["0P0000XW01.BO"], # Placeholder MF IDs
            "SECTORS": ["Banking", "Technology", "Renewable Energy"]
        }

    async def run_omni_discovery_service(self):
        """
        The persistent heartbeat service for deep cross-asset intelligence.
        Optimized for high-parallelism.
        """
        print(f"🚀 [OMNI-DISCOVERY] Fleet Launched at {datetime.now()}")
        semaphore = asyncio.Semaphore(3) # Limit concurrency to avoid rate limits

        async def tethered_index(ticker: str):
            async with semaphore:
                await self._index_entity_knowledge(ticker)

        while True:
            try:
                # 1. MACRO SYNC (Fast, direct API)
                print("🌍 [Crawl] Global Macro Signals...")
                macro_data = self.market_engine.fetch_macro_heartbeat()
                self._index_macro_context(macro_data)

                # 2. PARALLEL EQUITY SYNC
                print(f"📊 [Crawl] Parallel Sector Discovery for {len(self.watchlists['EQUITY'])} tickers...")
                tasks = [tethered_index(ticker) for ticker in self.watchlists["EQUITY"]]
                await asyncio.gather(*tasks)

                # 3. IPO DISCOVERY
                print("🚀 [Crawl] Scouting Upcoming IPOs...")
                await self._scout_upcoming_ipos()

                # 4. MUTUAL FUND SYNC
                print("🏦 [Crawl] Parallel Fund Discovery...")
                mf_tasks = [self._index_mf_data(mf) for mf in self.watchlists["MUTUAL_FUNDS"]]
                await asyncio.gather(*mf_tasks)

                # 5. ECONOMY SYNC (RBI Pulse)
                print("💰 [Crawl] Fetching RBI Economic Pulse...")
                rbi_data = self.market_engine.fetch_economic_pulse()
                self._index_rbi_context(rbi_data)

                # 6. SECTOR INTELLIGENCE
                print("🏗️ [Crawl] Harvesting Sector Trends...")
                # (Optional: Sector-specific logic)

                print(f"✅ [OMNI-SYNC] Complete at {datetime.now()}. AI Brain updated.")
            except Exception as e:
                print(f"❌ [Fleet Alert] Discovery interrupted: {e}")
            
            await asyncio.sleep(3600)

    async def _index_entity_knowledge(self, ticker: str):
        """Standard Index Link: WEB_DATA + MARKET_STATS + CORPORATE_EVENTS + AI_SYNTHESIS"""
        print(f"🔎 Indexing {ticker} (Upsert)...")
        # Fixed: Using correct async method name from WebIntelligence
        web_context = await self.web_intel.get_comprehensive_intelligence(ticker, ticker)
        market_stats = self.market_engine.fetch_equity_intelligence(ticker)
        corp_events = self.market_engine.fetch_corporate_events(ticker)
        
        payload = (
            f"INTELLIGENCE REPORT FOR {ticker}\n"
            f"MARKET DATA: {market_stats}\n"
            f"CORPORATE EVENTS: {corp_events}\n"
            f"WEB INSIGHTS: {web_context.get('ai_answer', '')}"
        )
        
        self.vector_db.upsert_document(
            text=payload,
            metadata={
                "symbol": ticker, 
                "type": "EQUITY_INDEX", 
                "updated": datetime.now().isoformat(),
                "industry": corp_events.get('industry', 'N/A')
            },
            namespace=f"idx_{ticker}"
        )

    async def _scout_upcoming_ipos(self):
        """Tavily-driven IPO discovery with Intelligent Upsert"""
        ipo_intel = self.web_intel.tavily.search(query="upcoming IPOs in India 2024 listed schedule news", search_depth="advanced")
        summary = await self.broker.execute_task(
            "Summarize upcoming IPOs with expected dates and valuation hints.",
            provider_mode="scout",
            raw_context=str(ipo_intel)
        )
        self.vector_db.upsert_document(
            text=summary.get("summary", ""),
            metadata={"type": "IPO_DISCOVERY", "updated": datetime.now().isoformat()},
            namespace="ipo_discovery_pulse"
        )

    def _index_macro_context(self, data: dict):
        """Indexes global macro shifts deterministically"""
        self.vector_db.upsert_document(
            text=f"Global Macro Snapshot: {data}",
            metadata={"type": "MACRO_INDEX", "updated": datetime.now().isoformat()},
            namespace="macro_heartbeat"
        )

    async def _index_mf_data(self, mf_id: str):
        stats = self.market_engine.fetch_mutual_fund_stats(mf_id)
        if stats:
            self.vector_db.upsert_document(
                text=f"Mutual Fund Perf: {stats}",
                metadata={"mf_id": mf_id, "type": "MF_INDEX"},
                namespace=f"mf_{mf_id}"
            )

    def _index_rbi_context(self, data: dict):
        """Indexes macroeconomic context from RBI"""
        if not data: return
        self.vector_db.upsert_document(
            text=f"Official RBI Economic Indicators: {data}",
            metadata={"type": "RBI_ECON_INDEX", "updated": datetime.now().isoformat()},
            namespace="economy_pulse"
        )

if __name__ == "__main__":
    kg = DocumindKnowledgeGraph()
    asyncio.run(kg.run_omni_discovery_service())
