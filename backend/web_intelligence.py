import os
from tavily import TavilyClient
from typing import List, Dict

class WebIntelligence:
    """
    Tavily-powered web research layer.
    Extracts company introductions and finds critical primary sources (PDFs).
    """
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def get_company_context(self, ticker: str, company_name: str) -> Dict:
        """
        Fetches introduction, recent news, and high-quality links.
        """
        if not self.client: return {"error": "Tavily API Key missing"}
        
        query = f"Financial summary, competitors, and 2024 outlook for {company_name} ({ticker})"
        print(f"📡 Tavily: Deep searching context for {company_name}...")
        
        # We use 'advanced' search for high-fidelity financial info
        search_result = self.client.search(
            query=query, 
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )
        return {
            "ai_answer": search_result.get("answer"),
            "results": search_result.get("results"),
            "query": query
        }

    def find_annual_reports(self, company_name: str) -> List[str]:
        """Specific search for PDF annual reports and investor presentations."""
        if not self.client: return []
        
        query = f"{company_name} investor relations annual report 2024 filetype:pdf"
        results = self.client.search(query=query, max_results=3)
        
        # Filter only for actual PDF links
        return [r['url'] for r in results['results'] if r['url'].endswith('.pdf')]
