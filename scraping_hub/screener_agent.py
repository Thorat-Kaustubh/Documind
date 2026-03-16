from .firecrawl_agent import FirecrawlAgent

class ScreenerAgent:
    """
    Screener Agent: Specifically targets Screener.in for financial data extraction.
    """
    def __init__(self, api_key: str = None):
        self.crawler = FirecrawlAgent(api_key=api_key)

    def get_stock_details(self, symbol: str):
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        print(f"Scraping Screener for {symbol}...")
        return self.crawler.scrape(url)

if __name__ == "__main__":
    # agent = ScreenerAgent()
    # print(agent.get_stock_details("RELIANCE"))
    pass
