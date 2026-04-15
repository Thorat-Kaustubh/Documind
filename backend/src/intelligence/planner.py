from typing import List
from .models import QueryPlan, IntentType, FinancialEntities

class QueryPlanner:
    """
    Generates structured execution plans based on intent and entities.
    """
    
    def generate_plan(self, intent: IntentType, entities: FinancialEntities, verification_notes: str = "") -> QueryPlan:
        """
        Determines the optimal execution path (SQL, RAG, Web Search, LLM).
        """
        execution_steps = []
        reasoning = ""
        
        if intent == IntentType.FINANCIAL_EXTRACTION:
            # Prefer SQL for structured data, fallback to RAG for documents
            execution_steps = ["sql", "rag", "llm"]
            reasoning = f"Verified extraction for {entities.company}. Attempting SQL retrieval for metrics: {entities.metrics}."
            
        elif intent == IntentType.TREND_ANALYSIS:
            execution_steps = ["sql", "llm"]
            reasoning = f"Analyzing trends for {entities.company} over {entities.time_range}. Requiring historical structured data."
            
        elif intent == IntentType.COMPARATIVE_ANALYSIS:
            execution_steps = ["sql", "rag", "llm"]
            reasoning = "Multi-source comparison. Fetching industry benchmarks (SQL) and peer filings (RAG)."
            
        elif intent == IntentType.NEWS_RETRIEVAL:
            execution_steps = ["web_search", "llm"]
            reasoning = "Real-time query identified. Routing to web intelligence for recent updates."
            
        elif intent == IntentType.RISK_ASSESSMENT:
            execution_steps = ["rag", "llm"]
            reasoning = "Deep qualitative analysis required. Scanning filings for risk factors and legal disclosures."
            
        else:
            execution_steps = ["rag", "llm"]
            reasoning = "General query. Defaulting to knowledge retrieval and synthesis."

        # Boost confidence if we have a clear company and metrics
        confidence = 0.9 if entities.company and entities.metrics else 0.75
        
        return QueryPlan(
            intent=intent,
            entities=entities,
            execution_steps=execution_steps,
            confidence=confidence,
            reasoning=reasoning + (f" [{verification_notes}]" if verification_notes else "")
        )
