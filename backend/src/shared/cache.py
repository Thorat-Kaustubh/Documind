import redis
import json
import hashlib
import logging
from typing import Optional, Any
from backend.config import settings

logger = logging.getLogger("documind.shared.cache")

class TieredCache:
    """
    SECTION 9: DATA LAYER ENHANCEMENTS
    Implements a multi-level caching strategy:
    L1: Redis (High-speed Key-Value)
    L2: Semantic Cache (Vector-based similarity)
    L3: Precomputed (Cold storage snapshots)
    """
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
        self.expiry = 3600 # Default 1 hour

    def _get_key(self, query: str, context_hash: Optional[str] = None) -> str:
        payload = f"{query}:{context_hash or ''}"
        return f"cache:v2:{hashlib.sha256(payload.encode()).hexdigest()}"

    def get_l1(self, query: str, context_hash: Optional[str] = None) -> Optional[Any]:
        """Fast lookup in Redis."""
        key = self._get_key(query, context_hash)
        try:
            data = self.redis_client.get(key)
            if data:
                logger.info(f"L1 Cache Hit: {key}")
                return json.loads(data)
        except Exception as e:
            logger.error(f"L1 Cache Error: {e}")
        return None

    def set_l1(self, query: str, value: Any, context_hash: Optional[str] = None):
        """Standardize write to Redis."""
        key = self._get_key(query, context_hash)
        try:
            self.redis_client.setex(key, self.expiry, json.dumps(value))
        except Exception as e:
            logger.error(f"L1 Cache Write Error: {e}")

    async def get_l2_semantic(self, query: str) -> Optional[Any]:
        """
        Placeholder for Semantic Cache (L2).
        Uses vector similarity to find 'nearly identical' queries.
        """
        # Logic to call VectorDB and search for query similarity > 0.95
        return None

    def get_l3_precomputed(self, ticker: str, category: str) -> Optional[Any]:
        """
        Cold cache for pre-processed signals (e.g. daily P&L summaries).
        """
        key = f"precompute:{ticker}:{category}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
