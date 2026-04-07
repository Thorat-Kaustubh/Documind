import os
import logging
import psycopg2
from psycopg2 import sql, pool
from psycopg2.extras import Json, RealDictCursor
from datetime import datetime
import uuid
from contextlib import contextmanager

# Structured Logging
logger = logging.getLogger("documind.database")

class PostgresSync:
    """
    Documind Elite PostgreSQL Sync: 
    The 'Hard Memory' layer for the Multi-Asset Discovery Engine.
    Handles asset registry, historical quotes, and a structured intelligence feed.
    Uses a ThreadedConnectionPool for production stability.
    """
    _pool = None

    def __init__(self, connection_url: str = None):
        self.connection_url = connection_url or os.getenv("POSTGRES_URL")
        if not PostgresSync._pool and self.connection_url:
            try:
                PostgresSync._pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=self.connection_url
                )
                logger.info("✅ [POSTGRES] Connection Pool Initialized.")
            except Exception as e:
                logger.error(f"❌ [POSTGRES-POOL-ERROR] Could not initialize pool: {e}")

    @contextmanager
    def get_cursor(self):
        """Context manager for thread-safe cursor handling from the pool."""
        conn = None
        if not PostgresSync._pool:
            yield None
            return
        try:
            conn = PostgresSync._pool.getconn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
            conn.commit()
        except Exception as e:
            if conn: conn.rollback()
            logger.error(f"❌ [POSTGRES-CURSOR-ERROR] {e}")
            raise e
        finally:
            if conn: PostgresSync._pool.putconn(conn)

    def initialize_schema(self):
        """Initializes the multi-asset unified schema for Documind 2.0."""
        try:
            with self.get_cursor() as cur:
                if not cur: return
                # Enable UUID support
                cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
                
                # Load the full schema from the .sql file
                schema_path = os.path.join(os.path.dirname(__file__), "multi_asset_schema.sql")
                if os.path.exists(schema_path):
                    with open(schema_path, "r") as f:
                        cur.execute(f.read())
                logger.info("📊 [POSTGRES] Unified Multi-Asset Schema Synchronized.")
        except Exception as e:
            logger.error(f"❌ [POSTGRES-SCHEMA-ERROR] {e}")

    def get_or_create_asset(self, ticker: str, company_name: str, asset_type: str = "EQUITY"):
        """Ensures an asset exists in the Master Registry."""
        try:
            with self.get_cursor() as cur:
                if not cur: return None
                cur.execute("SELECT id FROM asset_master WHERE ticker = %s", (ticker,))
                res = cur.fetchone()
                if res: return res['id']
                
                asset_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO asset_master (id, ticker, company_name, asset_type) VALUES (%s, %s, %s, %s) RETURNING id",
                    (asset_id, ticker, company_name, asset_type)
                )
                return asset_id
        except Exception as e:
            logger.error(f"❌ [POSTGRES-ASSET-ERROR] {e}")
            return None

    def insert_market_quote(self, ticker: str, price: float, change_pct: float, volume: int, market_cap: str = None):
        """Standard high-frequency quote injection."""
        try:
            asset_id = self.get_or_create_asset(ticker, ticker) # Fallback to ticker for name
            with self.get_cursor() as cur:
                if not cur or not asset_id: return
                cur.execute(
                    "INSERT INTO market_quotes (asset_id, price, change_percent, volume, market_cap) VALUES (%s, %s, %s, %s, %s)",
                    (asset_id, price, change_pct, volume, market_cap)
                )
        except Exception as e:
            logger.error(f"❌ [POSTGRES-QUOTE-ERROR] {e}")

    def sync_intelligence_feed(self, ticker: str, title: str, content: str, source: str, sentiment: float, category: str = "NEWS", vector_id: str = None):
        """Syncs AI-processed market intelligence to the feed with optional vector cross-link."""
        try:
            asset_id = self.get_or_create_asset(ticker, ticker)
            with self.get_cursor() as cur:
                if not cur or not asset_id: return
                cur.execute(
                    """INSERT INTO intelligence_feed (asset_id, title, content, source, sentiment_score, category, vector_id) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (asset_id, title, content, source, sentiment, category, vector_id)
                )
        except Exception as e:
            logger.error(f"❌ [POSTGRES-FEED-ERROR] {e}")

    def get_market_pulse(self):
        """Retrieves the latest 10 intelligence feed items from the hybrid brain."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("""
                    SELECT f.*, a.ticker, a.company_name 
                    FROM intelligence_feed f
                    JOIN asset_master a ON f.asset_id = a.id
                    ORDER BY published_at DESC LIMIT 10
                """)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-PULSE-ERROR] {e}")
            return []

    def get_all_assets(self):
        """Retrieves the Master Asset Registry."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("SELECT * FROM asset_master ORDER BY ticker ASC")
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-ASSETS-ERROR] {e}")
            return []

    def get_asset_intelligence(self, ticker: str, limit: int = 5):
        """Retrieves the latest structured intelligence items for a specific asset."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("""
                    SELECT f.*, a.ticker, a.company_name 
                    FROM intelligence_feed f
                    JOIN asset_master a ON f.asset_id = a.id
                    WHERE a.ticker = %s
                    ORDER BY published_at DESC NULLS LAST LIMIT %s
                """, (ticker, limit))
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-ASSET-FEED-ERROR] {e}")
            return []

    def get_ipo_watchlist(self):
        """Retrieves upcoming IPOs."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("SELECT * FROM ipo_registry ORDER BY listing_date DESC NULLS LAST")
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-IPO-VIEW-ERROR] {e}")
            return []

    def get_recent_high_impact_feeds(self, hours: int = 1):
        """Fetches intelligence items with extreme sentiment in the specified time window."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("""
                    SELECT f.*, a.ticker 
                    FROM intelligence_feed f
                    JOIN asset_master a ON f.asset_id = a.id
                    WHERE f.published_at >= NOW() - INTERVAL '%s hours'
                    AND (f.sentiment_score > 0.8 OR f.sentiment_score < 0.2)
                """, (hours,))
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-HIGH-IMPACT-ERROR] {e}")
            return []

    def create_notification(self, user_id: str, title: str, message: str, type: str = "SYSTEM"):
        """Registers a new notification for a user (or global if user_id is None)."""
        try:
            with self.get_cursor() as cur:
                if not cur: return
                cur.execute("""
                    INSERT INTO notifications (user_id, title, message, type)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, title, message, type))
        except Exception as e:
            logger.error(f"❌ [POSTGRES-NOTIF-ERROR] {e}")

    def create_audit_log(self, user_id: str, action: str, resource: str, ip_address: str = None):
        """Registers a persistent audit trail for security/compliance."""
        try:
            with self.get_cursor() as cur:
                if not cur: return
                cur.execute("""
                    INSERT INTO audit_logs (user_id, action, resource, ip_address)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, action, resource, ip_address))
        except Exception as e:
            logger.error(f"❌ [POSTGRES-AUDIT-ERROR] {e}")

    def get_user_notifications(self, user_id: str):
        """Retrieves all notifications for a specific user."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("""
                    SELECT * FROM notifications 
                    WHERE user_id = %s OR user_id IS NULL
                    ORDER BY created_at DESC LIMIT 20
                """, (user_id,))
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-NOTIF-GET-ERROR] {e}")
            return []

    def get_users_watching_asset(self, ticker: str):
        """Returns a list of user IDs who have this ticker in their watchlist."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("""
                    SELECT w.user_id 
                    FROM user_watchlists w
                    JOIN asset_master a ON w.asset_id = a.id
                    WHERE a.ticker = %s
                """, (ticker,))
                return [row['user_id'] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"❌ [POSTGRES-WATCHING-USERS-ERROR] {e}")
            return []

    def manage_watchlist(self, user_id: str, ticker: str, action: str = "ADD"):
        """Adds or removes an asset from a user's personal watchlist."""
        try:
            asset_id = self.get_or_create_asset(ticker, ticker)
            with self.get_cursor() as cur:
                if not cur or not asset_id: return False
                if action == "ADD":
                    cur.execute("""
                        INSERT INTO user_watchlists (user_id, asset_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """, (user_id, asset_id))
                else:
                    cur.execute("DELETE FROM user_watchlists WHERE user_id = %s AND asset_id = %s", (user_id, asset_id))
                return True
        except Exception as e:
            logger.error(f"❌ [POSTGRES-WATCHLIST-MANAGE-ERROR] {e}")
            return False

    def get_user_watchlist(self, user_id: str):
        """Retrieves a user's personal watchlist with real-time quotes."""
        try:
            with self.get_cursor() as cur:
                if not cur: return []
                cur.execute("""
                    SELECT a.ticker, a.company_name, q.price, q.change_percent 
                    FROM user_watchlists w
                    JOIN asset_master a ON w.asset_id = a.id
                    LEFT JOIN LATERAL (
                        SELECT price, change_percent FROM market_quotes 
                        WHERE asset_id = a.id ORDER BY timestamp DESC LIMIT 1
                    ) q ON TRUE
                    WHERE w.user_id = %s
                """, (user_id,))
                return cur.fetchall()
        except Exception as e:
            logger.error(f"❌ [POSTGRES-WATCHLIST-GET-ERROR] {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = PostgresSync()
    db.initialize_schema()
