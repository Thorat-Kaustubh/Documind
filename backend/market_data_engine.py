import logging
import yfinance as yf
import pandas as pd
from datetime import datetime
from jugaad_data.nse import NSELive
from database.postgres_sync import PostgresSync

# Structured Logging
logger = logging.getLogger("documind.market")

class MarketDataEngine:
    """
    Unified Multi-Asset Data Engine.
    Implements the 'Type' and 'Frequency' layer for Equity, Commodities, and Forex.
    """
    def __init__(self):
        self.db = PostgresSync()
        self.nse = NSELive()
        self.cache = {}
        self.cache_ttl = 60 # 1 minute cache for fast data
        # Common Macro Indicators
        self.macro_tickers = {
            "GOLD": "GC=F",
            "BRENT_OIL": "BZ=F",
            "USD_INR": "INR=X",
            "NIFTY_50": "^NSEI",
            "SENSEX": "^BSESN"
        }

    def _is_cached(self, key: str):
        if key in self.cache:
            entry = self.cache[key]
            if (datetime.now() - entry['timestamp']).total_seconds() < self.cache_ttl:
                return entry['data']
        return None

    def _set_cache(self, key: str, data: any):
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }

    def fetch_equity_intelligence(self, symbol: str):
        """
        Deep Equity Scan with Caching.
        """
        cached = self._is_cached(symbol)
        if cached: return cached

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            metrics = {
                "price": info.get('currentPrice', 0.0),
                "change_pct": info.get('regularMarketChangePercent', 0.0),
                "volume": info.get('volume', 0),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0.0),
                "sector": info.get('sector', 'Unknown'),
                "news": ticker.news[:5] if ticker.news else []
            }
            
            # Save to hard metrics and cache
            # V2 Architecture: Use Event-Driven Microservice
            from backend.services.data_update.queue import QueueManager
            QueueManager().publish_event("MARKET_QUOTE", {
                "ticker": symbol,
                "price": metrics['price'],
                "change_pct": metrics['change_pct'],
                "volume": metrics['volume'],
                "market_cap": str(metrics['market_cap'])
            })
            
            self._set_cache(symbol, metrics)
            return metrics
        except Exception as e:
            logger.error(f"Error fetching equity {symbol}: {e}")
            return {}

    def fetch_macro_heartbeat(self):
        """
        Fetches global market signals (Commodities, Forex, Indices).
        Now uses jugaad-data for premium NSE/BSE accuracy.
        """
        results = {}
        
        # 1. Fetch NSE/BSE Indices via jugaad-data (Live & Accurate)
        try:
            nifty_data = self.nse.live_index("NIFTY 50")
            results["NIFTY_50"] = nifty_data['data'][0]['lastPrice']
            
            # Optional: Sensex can also be fetched if needed, but Nifty is core
            # jugaad-data is NSE centric, for BSE we still use yfinance or its native tracker
        except Exception:
            results["NIFTY_50"] = 0.0

        # 2. Fetch Global Macro via yfinance
        for label, ticker_id in self.macro_tickers.items():
            if label == "NIFTY_50": continue # Already handled
            try:
                ticker = yf.Ticker(ticker_id)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    results[label] = price
            except:
                results[label] = 0.0
        return results

    def fetch_economic_pulse(self):
        """
        Fetches official RBI rates (Policy Repo, Reverse Repo, etc.)
        using jugaad-data's RBI module.
        """
        # Note: jugaad-data has a dedicated RBI class
        from jugaad_data.rbi import RBI
        r = RBI()
        try:
            return r.current_rates()
        except:
            return {}

    def fetch_corporate_events(self, symbol: str):
        """
        Fetches Corporate Actions and Announcements directly from NSE.
        """
        try:
            quote = self.nse.stock_quote(symbol)
            return {
                "events": quote.get('metadata', {}).get('status', 'No Status'),
                "industry": quote.get('metadata', {}).get('industry', 'N/A'),
                "isin": quote.get('metadata', {}).get('isin', 'N/A')
            }
        except:
            return {}

    def fetch_mutual_fund_stats(self, fund_id: str):
        """
        Fetches Mutual Fund NAV and performance data.
        In India, many MFs are available via yfinance (e.g., '0P0000XW01.BO' for Axis Bluechip)
        """
        try:
            ticker = yf.Ticker(fund_id)
            info = ticker.info
            return {
                "nav": info.get('navPrice', 0.0),
                "category": info.get('category', 'MF'),
                "ytd_return": info.get('ytdReturn', 0.0)
            }
        except:
            return {}

    def get_announcements_feed(self, symbol: str):
        """
        Extracts exchange-level announcements for a specific ticker.
        """
        ticker = yf.Ticker(symbol)
        try:
            return [{"title": n['title'], "link": n['link'], "publisher": n.get('publisher')} for n in ticker.news]
        except:
            return []
