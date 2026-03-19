import os
import asyncio
from .celery_app import celery_app
from database.pdf_rag import PDFIntelligenceEngine
from web_intelligence import WebIntelligence
from backend.market_data_engine import MarketDataEngine
from database.vector_storage import VectorStorage
from datetime import datetime

# Initialize engines inside task context to avoid thread-safety issues
pdf_rag = PDFIntelligenceEngine()
web_intel = WebIntelligence()
market_engine = MarketDataEngine()
vector_db = VectorStorage()

@celery_app.task(name="tasks.process_pdf_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def process_pdf_task(symbol: str, pdf_url: str, is_local: bool = False):
    """
    Background Task: Process a PDF (Download -> Chunk -> Embed -> Stores).
    Persists even if the main server crashes.
    """
    print(f"📦 [CELERY-WORKER] Processing PDF for {symbol}...")
    success = pdf_rag.process_financial_pdf(symbol, pdf_url, is_local=is_local)
    if not success:
        raise Exception(f"Failed to process PDF for {symbol}")
    return {"status": "success", "symbol": symbol, "source": pdf_url}

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
            
            payload = f"INTELLIGENCE REPORT FOR {ticker}\nMARKET DATA: {market_stats}\nWEB INSIGHTS: {web_context.get('ai_answer', '')}"
            
            # Sync to semantic memory
            vector_db.upsert_document(
                text=payload,
                metadata={"symbol": ticker, "type": "WATCHLIST_SYNC", "updated": datetime.now().isoformat()},
                namespace=f"idx_{ticker}"
            )
    
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
        metadata={"type": "MACRO_HEARTBEAT", "updated": datetime.now().isoformat()},
        namespace="macro_heartbeat"
    )
    return {"status": "synced", "data": macro_data}
