import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json, RealDictCursor
from datetime import datetime
import uuid

class PostgresSync:
    """
    Documind Elite PostgreSQL Sync: 
    The 'Hard Memory' layer for the Multi-Asset Discovery Engine.
    Handles asset registry, historical quotes, and a structured intelligence feed.
    """
    def __init__(self, connection_url: str = None):
        self.connection_url = connection_url or os.getenv("POSTGRES_URL")
        self.conn = None
        if self.connection_url:
            try:
                self.conn = psycopg2.connect(self.connection_url)
                print("✅ [POSTGRES] Connected to production database.")
            except Exception as e:
                print(f"⚠️ [POSTGRES-SYNC-FAILURE] Could not connect: {e}")
                self.conn = None

    def initialize_schema(self):
        """Initializes the multi-asset unified schema for Documind 2.0."""
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                # Enable UUID support
                cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
                
                # Load the full schema from the .sql file
                schema_path = os.path.join(os.path.dirname(__file__), "multi_asset_schema.sql")
                if os.path.exists(schema_path):
                    with open(schema_path, "r") as f:
                        cur.execute(f.read())
                self.conn.commit()
                print("📊 [POSTGRES] Unified Multi-Asset Schema Synchronized.")
        except Exception as e:
            print(f"❌ [POSTGRES-SCHEMA-ERROR] {e}")

    def get_or_create_asset(self, ticker: str, company_name: str, asset_type: str = "EQUITY"):
        """Ensures an asset exists in the Master Registry."""
        if not self.conn: return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM asset_master WHERE ticker = %s", (ticker,))
                res = cur.fetchone()
                if res: return res[0]
                
                asset_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO asset_master (id, ticker, company_name, asset_type) VALUES (%s, %s, %s, %s) RETURNING id",
                    (asset_id, ticker, company_name, asset_type)
                )
                self.conn.commit()
                return asset_id
        except Exception as e:
            print(f"❌ [POSTGRES-ASSET-ERROR] {e}")
            return None

    def insert_market_quote(self, ticker: str, price: float, change_pct: float, volume: int):
        """Standard high-frequency quote injection."""
        if not self.conn: return
        try:
            asset_id = self.get_or_create_asset(ticker, ticker) # Fallback to ticker for name
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO market_quotes (asset_id, price, change_percent, volume) VALUES (%s, %s, %s, %s)",
                    (asset_id, price, change_pct, volume)
                )
                self.conn.commit()
        except Exception as e:
            print(f"❌ [POSTGRES-QUOTE-ERROR] {e}")

    def sync_intelligence_feed(self, ticker: str, title: str, content: str, source: str, sentiment: float, category: str = "NEWS"):
        """Syncs AI-processed market intelligence to the feed."""
        if not self.conn: return
        try:
            asset_id = self.get_or_create_asset(ticker, ticker)
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO intelligence_feed (asset_id, title, content, source, sentiment_score, category) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (asset_id, title, content, source, sentiment, category)
                )
                self.conn.commit()
        except Exception as e:
            print(f"❌ [POSTGRES-FEED-ERROR] {e}")

    def get_market_pulse(self):
        """Retrieves the latest 10 intelligence feed items from the hybrid brain."""
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT f.*, a.ticker, a.company_name 
                    FROM intelligence_feed f
                    JOIN asset_master a ON f.asset_id = a.id
                    ORDER BY published_at DESC LIMIT 10
                """)
                return cur.fetchall()
        except Exception as e:
            print(f"❌ [POSTGRES-PULSE-ERROR] {e}")
            return []

    def get_all_assets(self):
        """Retrieves the Master Asset Registry."""
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM asset_master ORDER BY ticker ASC")
                return cur.fetchall()
        except Exception as e:
            print(f"❌ [POSTGRES-ASSETS-ERROR] {e}")
            return []

    def get_ipo_watchlist(self):
        """Retrieves upcoming IPOs."""
        if not self.conn: return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM ipo_registry ORDER BY listing_date DESC NULLS LAST")
                return cur.fetchall()
        except Exception as e:
            print(f"❌ [POSTGRES-IPO-VIEW-ERROR] {e}")
            return []

if __name__ == "__main__":
    db = PostgresSync()
    db.initialize_schema()
