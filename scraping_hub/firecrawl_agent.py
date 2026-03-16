import os
import requests
from typing import Optional, Dict, Any

class FirecrawlAgent:
    """
    Firecrawl Agent: Utilizes Firecrawl API to extract clean Markdown from financial news and data pages.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.endpoint = "https://api.firecrawl.dev/v1/scrape"

    def scrape(self, url: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"error": "Firecrawl API key not found."}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "formats": ["markdown"]
        }

        try:
            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test
    agent = FirecrawlAgent()
    # result = agent.scrape("https://www.moneycontrol.com/")
    # print(result)
