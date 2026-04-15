import os
import asyncio
from .celery_app import celery_app
from database.pdf_rag import PDFIntelligenceEngine
from .web_intelligence import WebIntelligence
from backend.market_data_engine import MarketDataEngine
from database.vector_storage import VectorStorage
from datetime import datetime

# Initialize engines inside task context to avoid thread-safety issues
pdf_rag = PDFIntelligenceEngine()
web_intel = WebIntelligence()
market_engine = MarketDataEngine()
vector_db = VectorStorage()
from database.postgres_sync import PostgresSync
pg_db = PostgresSync()
from .ai_broker import AIBroker
broker = AIBroker()
from .services.data_update.queue import QueueManager
queue = QueueManager()

@celery_app.task(name="tasks.process_pdf_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def process_pdf_task(symbol: str, pdf_url: str, is_local: bool = False, user_id: str = None):
    """
    Background Task: Process a PDF (Download -> Chunk -> Embed -> Stores).
    Persists even if the main server crashes.
    Now includes user_id for secure Multi-Tenancy. (Prevents IDOR).
    """
    print(f"📦 [CELERY-WORKER] Processing PDF for {symbol} (User: {user_id or 'SYSTEM'})...")
    # Note: Using'ingest_document_secure' if implemented or just passing to ingest_document
    success = asyncio.run(pdf_rag.process_financial_pdf(symbol, pdf_url, is_local=is_local, user_id=user_id))
    if not success:
        raise Exception(f"Failed to process PDF for {symbol}")
    return {"status": "success", "symbol": symbol, "source": pdf_url, "user_id": user_id}


@celery_app.task(name="tasks.discovery_sweep", soft_time_limit=1800)
def discovery_sweep_task(ticker_list: list):
    """
    Background Task: Scheduled discovery for a batch of tickers.
    Satisfies PARALLEL EXECUTION and DISTRIBUTED LOAD.
    """
    print(f"📊 [CELERY-WORKER] Starting Global Discovery for {len(ticker_list)} tickers.")
    
    async def index_batch():
        for ticker in ticker_list:
            # 1. Web context fetch
            web_context = web_intel.get_company_context(ticker, ticker)
            
            # 2. Market metrics sync
            market_stats = market_engine.fetch_equity_intelligence(ticker)
            
            # 3. AI Sentiment & Summary Generation (The 'Neural Reasoning' Layer)
            intelligence = await broker.execute_task(
                f"Analyze the context for {ticker}. Extraction focused.",
                provider_mode="grounding",
                raw_context=str(web_context.get('results', []))
            )
            
            summary_text = intelligence.get('summary', '')
            sentiment = intelligence.get('sentiment', {}).get('score', 0.5)
            
            # B. SEMANTIC MEMORY (Vector)
            payload = f"INTELLIGENCE REPORT: {summary_text}\nMARKET DATA: {market_stats}"
            vector_id = vector_db.upsert_document(
                text=payload,
                metadata={"symbol": ticker, "type": "WATCHLIST_SYNC", "updated": datetime.now().isoformat(), "sentiment": sentiment, "is_public": True},
                namespace=f"idx_{ticker}"
            )
            
            # Hybrid Storage (v2: Event-Driven Ingestion)
            # Instead of direct writes, we publish to the data update stream
            queue.publish_event("MARKET_QUOTE", {
                "ticker": ticker,
                "price": market_stats.get('price', 0.0),
                "change_pct": market_stats.get('change_pct', 0.0),
                "volume": market_stats.get('volume', 0),
                "market_cap": str(market_stats.get('market_cap', 0))
            })
            
            queue.publish_event("INTELLIGENCE_FEED", {
                "ticker": ticker,
                "title": f"Discovery Sync: {ticker}",
                "content": summary_text,
                "source": "Tavily/AI",
                "sentiment": sentiment,
                "vector_id": vector_id
            })
    
    asyncio.run(index_batch())
    return {"status": "complete", "batch_size": len(ticker_list)}

@celery_app.task(name="tasks.macro_heartbeat_sync")
def macro_heartbeat_sync_task():
    """
    Background Task: Sync macro indicators (Gold, Oil, Forex) to index.
    """
    macro_data = market_engine.fetch_macro_heartbeat()
    vector_db.upsert_document(
        text=f"Global Macro Snapshot: {macro_data}",
        metadata={"type": "MACRO_HEARTBEAT", "updated": datetime.now().isoformat(), "is_public": True},
        namespace="macro_heartbeat"
    )
    return {"status": "synced", "data": macro_data}

@celery_app.task(name="tasks.ipo_discovery")
def ipo_discovery_task():
    """
    Background Task: Scout for upcoming IPOs using Tavily and AI synthesis.
    """
    print("🚀 [CELERY-WORKER] Scouting Upcoming IPOs...")
    ipo_intel = web_intel.tavily_client.search(query="upcoming IPOs in India 2024 listed schedule news", search_depth="advanced")
    
    async def summarize_ipos():
        summary = await broker.execute_task(
            "Extract a list of upcoming IPOs from this context. Include company names and status. Return as a structural list.",
            provider_mode="grounding",
            raw_context=str(ipo_intel)
        )
        
        # In the consolidated schema, the model already handles ticker/entity extraction
        # we can pull them directly from the summary or let the next sweep pick them up.
        # For now, just rely on the vector index for discovery tracking.

        vector_db.upsert_document(
            text=summary.get("summary", ""),
            metadata={"type": "IPO_DISCOVERY", "updated": datetime.now().isoformat(), "is_public": True},
            namespace="ipo_discovery_pulse"
        )
    
    asyncio.run(summarize_ipos())
    return {"status": "scouted", "source": "Tavily Intelligence"}

@celery_app.task(name="tasks.mutual_fund_sync")
def mutual_fund_sync_task(mf_ids: list):
    """
    Background Task: Sync NAV and fund metrics for specific Mutual Funds.
    """
    print(f"🏦 [CELERY-WORKER] Syncing {len(mf_ids)} Mutual Funds...")
    for mf in mf_ids:
        stats = market_engine.fetch_mutual_fund_stats(mf)
        if stats:
            vector_db.upsert_document(
                text=f"Mutual Fund Perf: {stats}",
                metadata={"mf_id": mf, "type": "MF_INDEX", "updated": datetime.now().isoformat(), "is_public": True},
                namespace=f"mf_{mf}"
            )
    return {"status": "synced", "mf_count": len(mf_ids)}

@celery_app.task(name="tasks.sector_discovery")
def sector_discovery_task(sector: str):
    """
    Background Task: Perform deep sector-level research and update the index.
    """
    print(f"📡 [CELERY-WORKER] Performing Sector Scan for: {sector}")
    query = f"Key trends, regulatory changes, and top performing companies in the {sector} sector 2024"
    sector_intel = web_intel.tavily_client.search(query=query, search_depth="advanced", max_results=10)
    
    async def synthesize():
        res = await broker.execute_task(
            f"Summarize the current state of the {sector} sector.",
            provider_mode="grounding",
            raw_context=str(sector_intel.get('results', []))
        )
        vector_db.upsert_document(
            text=f"SECTOR REPORT [{sector}]: {res.get('summary')}",
            metadata={"type": "SECTOR_INDEX", "sector": sector, "updated": datetime.now().isoformat(), "is_public": True},
            namespace=f"sector_{sector.lower()}"
        )
    
    asyncio.run(synthesize())
    return {"status": "sector_scouted", "sector": sector}


@celery_app.task(name="tasks.sentiment_trigger_engine")
def sentiment_trigger_engine():
    """
    💓 Background Task: Sentiment Pulse Monitor
    Checks the intelligence_feed for significant shifts and triggers user notifications.
    """
    print("💓 [CELERY-WORKER] Scanning Intelligence Feed for Sentiment Swings...")
    # Fetch recent feeds with high/low sentiment (last 1 hour)
    feeds = pg_db.get_recent_high_impact_feeds(hours=1)
    
    alerts_fired = 0
    for feed in feeds:
        score = float(feed.get('sentiment_score', 0.5))
        ticker = feed.get('ticker', 'UNKNOWN')
        
        # Define high-impact logic (Bullish/Bearish breakouts)
        priority = "high" if score > 0.85 or score < 0.15 else "normal"
        
        if priority == "high":
            title = f"🚀 HIGH IMPACT: {ticker}" if score > 0.5 else f"⚠️ ALERT: {ticker}"
            message = f"Significant {feed.get('sentiment_label', 'market')} shift detected: {feed.get('title')}"
            
            # 1. Store global system-level notification
            pg_db.create_notification(
                user_id=None, # Global
                title=title,
                message=message,
                type="SENTIMENT_SWING"
            )
            
            # 2. Check for users watching this specific ticker (Personalized Alerts)
            watching_users = pg_db.get_users_watching_asset(ticker)
            for user_id in watching_users:
                pg_db.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    type="SENTIMENT_SWING"
                )
            
            alerts_fired += 1

    return {"status": "scan_complete", "alerts_fired": alerts_fired}
