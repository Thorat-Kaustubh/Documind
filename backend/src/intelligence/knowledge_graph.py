import logging
from typing import List, Dict, Any
from database.postgres_sync import PostgresSync

logger = logging.getLogger("documind.intelligence.graph")

class KnowledgeGraphService:
    """
    SECTION 9: DATA LAYER ENHANCEMENTS
    Handles relationship mapping between companies, sectors, and themes.
    Enables 'Cross-Asset' intelligence.
    """
    def __init__(self):
        self.db = PostgresSync()

    async def get_related_entities(self, ticker: str) -> Dict[str, Any]:
        """
        Finds companies in the same sector or with shared supply chains.
        """
        # 1. Fetch sector from SQL
        asset = self.db.get_asset_details(ticker)
        if not asset: return {"peers": [], "theme": "Unknown"}
        
        sector = asset.get("sector")
        
        # 2. Fetch peers in sector
        peers = self.db.get_assets_by_sector(sector) if sector else []
        
        return {
            "ticker": ticker,
            "sector": sector,
            "peers": [p['ticker'] for p in peers if p['ticker'] != ticker],
            "relationships": {
                "sector_peers": "Shared regulatory environment",
                "market_cap_group": "Shared volatility cluster"
            }
        }

    async def expand_context(self, ticker: str) -> str:
        """
        Generates a relationship context string to improve AI broadness.
        """
        graph = await self.get_related_entities(ticker)
        if not graph["peers"]: return ""
        
        return f"RELATIONSHIP CONTEXT: {ticker} is a key player in the {graph['sector']} sector. Its primary peers include {', '.join(graph['peers'][:5])}."
