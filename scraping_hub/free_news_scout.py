import httpx
import asyncio
from bs4 import BeautifulSoup
import random
from typing import List, Dict, Any

class FreeNewsScout:
    """
    100% FREE ASYNC DISCOVERY ENGINE
    Replaces Tavily and Firecrawl for news gathering using BS4 + httpx.
    """
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    async def get_latest_news(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Asynchronous scouting for news without API keys.
        Uses Google News RSS or direct parsing for maximum speed.
        """
        results = []
        # Fallback to Google News/RSS for stable free scraping
        search_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            headers = {"User-Agent": random.choice(self.user_agents)}
            try:
                # Random delay to avoid IP blocks
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                response = await client.get(search_url, headers=headers)
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all("item")[:limit]

                for item in items:
                    results.append({
                        "title": item.title.text,
                        "url": item.link.text,
                        "published": item.pubDate.text,
                        "source": item.source.text if item.source else "Google News"
                    })
            except Exception as e:
                print(f"❌ [FreeScout Error]: {e}")
                
        return results

    async def rip_page_content(self, url: str) -> str:
        """
        Fast extraction of static article text.
        """
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
             headers = {"User-Agent": random.choice(self.user_agents)}
             try:
                 response = await client.get(url, headers=headers)
                 soup = BeautifulSoup(response.content, "html.parser")
                 # Surgical extraction focus: Skip scripts, styles, nav, etc.
                 for element in soup(["script", "style", "nav", "footer", "header"]):
                     element.decompose()
                 return soup.get_text(separator="\n", strip=True)
             except:
                 return ""

if __name__ == "__main__":
    import json
    scout = FreeNewsScout()
    async def test():
        news = await asyncio.run(scout.get_latest_news("Reliance IPO"))
        print(json.dumps(news, indent=2))
