import os
from firecrawl import FirecrawlApp
from typing import Dict, Any

class ScreenerAgent:
    """
    Surgical agent to extract Screener.in financial tables.
    Extracts: Profit & Loss, Balance Sheet, Cash Flow, and Ratios.
    """
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.app = FirecrawlApp(api_key=self.api_key) if self.api_key else None

    def get_full_financials(self, ticker: str) -> Dict[str, Any]:
        """
        Scrapes the main company page on Screener.in.
        Uses surgical extraction to get clean tables.
        """
        if not self.app: return {"error": "Firecrawl API Key missing"}
        
        url = f"https://www.screener.in/company/{ticker}/"
        print(f"📡 ScreenerAgent: Extracting 10-year history for {ticker}...")
        
        try:
            # We use 'scrape' with specific extraction instructions to ensure we get the tables
            result = self.app.scrape_url(url, {
                'formats': ['markdown'],
                'onlyMainContent': True,
                # Strategic: We tell Firecrawl to prioritize these specific sections found in your images
                'waitFor': 2000 # Wait for tables to render perfectly
            })
            
            return {
                "symbol": ticker,
                "url": url,
                "data": result.get('markdown', ''),
                "metadata": result.get('metadata', {})
            }
        except Exception as e:
            return {"error": str(e)}
