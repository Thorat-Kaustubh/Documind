import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List, Dict, Any
import json
import os

class DocumindNewsSpider(scrapy.Spider):
    """
    Industrial-grade news crawler for deep sector research.
    """
    name = 'news_spider'
    
    def __init__(self, query: str = None, start_urls: List[str] = None, *args, **kwargs):
        super(DocumindNewsSpider, self).__init__(*args, **kwargs)
        self.query = query
        if start_urls:
             self.start_urls = start_urls
        else:
             # Default fallback to a generic search for the query
             self.start_urls = [f"https://www.google.com/search?q={query}"]
        
    def parse(self, response):
        """
        Processes search results and follows links to full articles.
        """
        # Surgical link extraction (avoiding non-article UI elements)
        links = response.css('a::attr(href)').getall()
        for link in links:
            if 'url?q=' in link:
                full_url = link.split('url?q=')[1].split('&')[0]
                yield scrapy.Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        """
        Extracts high-density content from a financial article.
        """
        yield {
            "title": response.css('h1::text').get() or response.css('title::text').get(),
            "url": response.url,
            "content": "\n".join(response.css('p::text').getall()),
            "metadata": {
                "scout_type": "HEAVY_SCRAPY",
                "extracted_at": response.headers.get('Date', b'').decode('utf-8')
            }
        }

class HeavyScoutProcess:
    """
    Manager for the Scrapy process.
    Handles configuration for concurrency and rate-limiting.
    """
    def __init__(self, output_file: str = "scout_results.json"):
        self.settings = {
            'CONCURRENT_REQUESTS': 16,
            'DOWNLOAD_DELAY': 1.5,
            'FEEDS': { output_file: { 'format': 'json', 'overwrite': True } },
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'AUTOTHROTTLE_ENABLED': True
        }
        self.output_file = output_file

    def run_scout(self, query: str, start_urls: List[str] = None):
        """
        Triggers the Scrapy crawler in a separate process context.
        """
        process = CrawlerProcess(self.settings)
        process.crawl(DocumindNewsSpider, query=query, start_urls=start_urls)
        process.start() # This blocks until completion

if __name__ == "__main__":
    # Example usage for a background worker
    scout = HeavyScoutProcess()
    scout.run_scout(query="Reliance green hydrogen strategy 2024")
    
    if os.path.exists("scout_results.json"):
        with open("scout_results.json") as f:
            print(f"✅ Extracted {len(json.load(f))} high-density news articles.")
