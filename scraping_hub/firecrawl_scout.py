import os
from firecrawl import FirecrawlApp
from typing import List, Dict, Any

class FirecrawlScout:
    """
    Enhanced Firecrawl Scout: Incorporates Search, Scrape, and CRAWL.
    Optimized for high-depth financial discovery (NSE, BSE, Screener).
    """
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key or "your_firecrawl" in self.api_key:
            print("⚠️ Firecrawl API Key missing. Scraping will be disabled.")
            self.app = None
        else:
            self.app = FirecrawlApp(api_key=self.api_key)

    def search_and_scrape(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        if not self.app: return []
        try:
            print(f"🛰️ Searching Web: {query}...")
            results = self.app.search(query, {
                'limit': limit,
                'scrapeOptions': {'formats': ['markdown'], 'onlyMainContent': True}
            })
            return results.get('data', [])
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return []

    def deep_crawl_site(self, base_url: str, max_pages: int = 5):
        """
        Uses Firecrawl 'Crawl' to go deep into a financial portal (NSE/BSE).
        Filters only for main content to save tokens.
        """
        if not self.app: return None
        try:
            print(f"🕸️ Deep Crawling: {base_url} (Max: {max_pages} pages)")
            crawl_status = self.app.crawl_url(
                base_url,
                params={
                    'limit': max_pages,
                    'scrapeOptions': {
                        'formats': ['markdown'],
                        'onlyMainContent': True
                    }
                }
            )
            return crawl_status
        except Exception as e:
            print(f"❌ Crawl Error: {e}")
            return None

    def scrape_url(self, url: str) -> Dict[str, Any]:
        if not self.app: return {}
        try:
            return self.app.scrape_url(url, {'formats': ['markdown']})
        except Exception as e:
            return {"error": str(e)}
