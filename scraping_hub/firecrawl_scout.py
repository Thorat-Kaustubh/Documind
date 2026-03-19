import os
import requests
from firecrawl import FirecrawlApp
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class FirecrawlScout:
    """
    Credit-Aware Firecrawl Scout.
    Saves Firecrawl credits by using local requests as a fallback for simple sites.
    """
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key or "your_firecrawl" in self.api_key:
            self.app = None
        else:
            self.app = FirecrawlApp(api_key=self.api_key)

    def scrape_surgical(self, url: str) -> Dict[str, Any]:
        """
        Only use this for complex JS-heavy sites like NSE/BSE or Screener.in.
        Uses 1 Firecrawl Credit.
        """
        if not self.app:
            return self.scrape_free(url)
            
        try:
            print(f"💎 Surgical Extraction (Using Credit): {url}")
            return self.app.scrape_url(url, {'formats': ['markdown']})
        except Exception as e:
            print(f"⚠️ Firecrawl failed, falling back to free: {e}")
            return self.scrape_free(url)

    def scrape_free(self, url: str) -> Dict[str, Any]:
        """
        Free Fallback using Requests + BeautifulSoup.
        Uses 0 Credits. Good for basic news sites.
        """
        print(f"🧊 Free Extraction: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple text extraction
            text = ' '.join([p.get_text() for p in soup.find_all('p')])
            return {"markdown": text[:10000], "metadata": {"source": "free_fallback"}}
        except Exception as e:
            return {"error": str(e)}

    def search_and_scrape(self, query: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Limited search to save credits."""
        if not self.app: return []
        try:
            print(f"🛰️ Surgical Search: {query}...")
            # We limit to 1 result to be extremely frugal with credits
            results = self.app.search(query, {
                'limit': limit,
                'scrapeOptions': {'formats': ['markdown'], 'onlyMainContent': True}
            })
            return results.get('data', [])
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return []
