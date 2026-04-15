import re
import json
import logging
from typing import Dict, Any
from .models import FinancialEntities
from backend.config import settings
from groq import AsyncGroq

logger = logging.getLogger("documind.intelligence.ner")

class FinancialNER:
    """
    Extracts financial entities (Company, Metric, Time) from queries.
    Uses Groq for precise multi-entity extraction.
    """
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def extract(self, query: str) -> FinancialEntities:
        """
        Precise entity extraction using Llama-3-70B.
        """
        system_prompt = """
        Extract financial entities from the user query.
        Return ONLY a JSON object with keys: 
        - company (ticker or name)
        - metrics (list of items like "revenue", "ebitda")
        - time_range (e.g. "5y", "FY2023", "Q1")
        - sector (e.g. "Technology", "Pharma")
        
        If an entity is not found, use null or an empty list.
        """
        
        try:
            completion = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            data = json.loads(completion.choices[0].message.content)
            
            return FinancialEntities(
                company=data.get("company"),
                metrics=data.get("metrics") or [],
                time_range=data.get("time_range"),
                sector=data.get("sector")
            )
            
        except Exception as e:
            logger.error(f"NER Extraction failed: {e}")
            # Minimal heuristic fallback
            company_match = re.search(r"\b[A-Z]{2,6}(\.NS|\.BO)?\b", query)
            return FinancialEntities(
                company=company_match.group(0) if company_match else None
            )
