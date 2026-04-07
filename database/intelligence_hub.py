import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from .postgres_sync import PostgresSync
from .vector_storage import VectorStorage

class IntelligenceHub:
    """
    Unified Database Orchestrator for Documind Elite.
    Seamlessly synchronizes 'Hard Memory' (Supabase/Postgres) 
    with 'Semantic Memory' (ChromaDB Cloud).
    """
    def __init__(self):
        self.pg = PostgresSync()
        self.vector = VectorStorage()

    def sync_market_pulse(self, ticker: str, summary: str, market_stats: Dict[str, Any], sentiment: float):
        """
        Dual-Stream Synchronization:
        1. Vectorize the intelligence for semantic search (RAG).
        2. Persist the metadata and summary in Postgres with the cross-link.
        """
        # Step 1: Semantic Indexing
        payload = f"INTELLIGENCE REPORT: {summary}\nMARKET DATA: {market_stats}"
        vector_id = self.vector.upsert_document(
            text=payload,
            metadata={
                "symbol": ticker, 
                "type": "WATCHLIST_SYNC", 
                "updated": datetime.now().isoformat(), 
                "sentiment": sentiment, 
                "is_public": True
            },
            namespace=f"idx_{ticker}"
        )
        
        # Step 2: Hard Memory Persistence
        self.pg.insert_market_quote(
            ticker, 
            market_stats.get('price', 0.0), 
            market_stats.get('change_pct', 0.0), 
            market_stats.get('volume', 0), 
            str(market_stats.get('market_cap', 0))
        )
        
        self.pg.sync_intelligence_feed(
            ticker, 
            f"Market Intelligence: {ticker}", 
            summary, 
            "Tavily/Agentic", 
            sentiment, 
            vector_id=vector_id
        )
        
        return vector_id

    def get_full_asset_report(self, ticker: str, user_id: str = None) -> Dict[str, Any]:
        """
        Hybrid Intelligence Retrieval:
        Combines structured market data with semantic highlights.
        """
        # 1. Fetch Latest News/Intelligence from Postgres
        # We need a new method in PostgresSync for this, but for now we can use get_market_pulse
        # or implement a specific getter.
        asset_info = None
        assets = self.pg.get_all_assets()
        for a in assets:
            if a['ticker'] == ticker:
                asset_info = a
                break
        
        if not asset_info:
            return {"error": "Asset not found in registry."}

        # 2. Fetch semantic highlights from Chroma
        semantic_results = self.vector.query(
            query_text=f"summarize everything about {ticker}", 
            n_results=5, 
            user_id=user_id
        )
        
        return {
            "asset": asset_info,
            "semantic_highlights": semantic_results.get('documents', [[]])[0],
            "metadata": semantic_results.get('metadatas', [[]])[0]
        }

# Singleton instance
hub = IntelligenceHub()
