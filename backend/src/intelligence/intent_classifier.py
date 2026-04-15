import logging
from typing import Dict, Any
from .models import IntentClassification, IntentType
from backend.config import settings
from groq import AsyncGroq

logger = logging.getLogger("documind.intelligence.intent")

class IntentClassifier:
    """
    Neuro-Symbolic Intent Classifier.
    Future: Replace Groq fallback with a local DistilBERT model.
    """
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.intent_keywords = {
            IntentType.TREND_ANALYSIS: ["trend", "history", "growth", "performance", "over time", "historical"],
            IntentType.FINANCIAL_EXTRACTION: ["revenue", "ebitda", "profit", "balance sheet", "income statement", "extract", "numbers"],
            IntentType.COMPARATIVE_ANALYSIS: ["compare", "versus", "vs", "better than", "compared to"],
            IntentType.RISK_ASSESSMENT: ["risk", "hazard", "threat", "weakness", "concern", "red flag"],
            IntentType.NEWS_RETRIEVAL: ["news", "latest", "recent", "press release", "updates", "what happened"],
        }

    def _symbolic_check(self, query: str) -> IntentType:
        """Fast keyword-based heuristic check."""
        query_lower = query.lower()
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        return IntentType.UNKNOWN

    async def classify(self, query: str) -> IntentClassification:
        """
        Classifies user query into a project intent.
        Uses Symbolic check (Fast) -> Groq (Neuro/Surrogate for BERT).
        """
        # 1. Fast symbolic check
        symbolic_intent = self._symbolic_check(query)
        
        # 2. Neuro-Surrogate (High-Fidelity Classification)
        system_prompt = f"""
        Classify the user's financial query into one of these categories:
        {', '.join([it.value for it in IntentType if it != IntentType.UNKNOWN])}

        Output ONLY the category name.
        """
        
        try:
            completion = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile", # High fidelity for classification
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=10,
                temperature=0
            )
            predicted_value = completion.choices[0].message.content.strip().upper()
            
            # Map back to Enum
            try:
                final_intent = IntentType(predicted_value)
                confidence = 0.95 # LLM classification is generally high confidence for this task
            except ValueError:
                final_intent = symbolic_intent if symbolic_intent != IntentType.UNKNOWN else IntentType.GENERAL_QUERY
                confidence = 0.6
                
            return IntentClassification(predicted_intent=final_intent, confidence=confidence)
            
        except Exception as e:
            logger.error(f"Intent Classification failed: {e}")
            return IntentClassification(
                predicted_intent=symbolic_intent if symbolic_intent != IntentType.UNKNOWN else IntentType.GENERAL_QUERY,
                confidence=0.5
            )
