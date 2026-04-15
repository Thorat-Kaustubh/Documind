import logging
from typing import Optional
from .models import IntentType, IntentClassification, VerificationResult
from backend.config import settings
from google import genai

logger = logging.getLogger("documind.intelligence.verifier")

class IntentVerificationLayer:
    """
    Ensures the correctness of predicted intent before execution.
    """
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.confidence_threshold = 0.85

    async def verify(self, query: str, classification: IntentClassification) -> VerificationResult:
        """
        Multi-stage verification flow:
        Confidence Check -> Rule-based checks -> LLM Fallback.
        """
        # 1. Confidence Threshold Check
        if classification.confidence >= self.confidence_threshold:
            return VerificationResult(
                is_verified=True,
                final_intent=classification.predicted_intent,
                verification_method="confidence_threshold"
            )

        # 2. Rule-Based Sanity Check
        # Example: Comparative analysis should have comparison keywords
        if classification.predicted_intent == IntentType.COMPARATIVE_ANALYSIS:
            comparative_terms = ["compare", "vs", "versus", "difference", "against"]
            if any(term in query.lower() for term in comparative_terms):
                 return VerificationResult(
                    is_verified=True,
                    final_intent=IntentType.COMPARATIVE_ANALYSIS,
                    verification_method="rule_based"
                )

        # 3. LLM-Based Verification (The Deep Fallback - Gemini)
        logger.info(f"Triggering LLM Fallback verification for query: {query}")
        try:
            prompt = f"""
            A user asked: "{query}"
            The system classified this as: {classification.predicted_intent.value}
            
            Does this classification accurately reflect the primary goal of the user?
            If yes, respond with "YES".
            If no, provide the correct category from: {[i.value for i in IntentType]}.
            
            ONLY return the category or "YES".
            """
            
            response = await self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            val = response.text.strip().upper()
            if "YES" in val:
                return VerificationResult(
                    is_verified=True,
                    final_intent=classification.predicted_intent,
                    verification_method="llm_fallback"
                )
            else:
                try:
                    corrected_intent = IntentType(val)
                    return VerificationResult(
                        is_verified=True,
                        final_intent=corrected_intent,
                        verification_method="llm_fallback",
                        notes=f"Corrected from {classification.predicted_intent.value}"
                    )
                except ValueError:
                    pass

        except Exception as e:
            logger.error(f"LLM Verification failed: {e}")

        # Default fallback
        return VerificationResult(
            is_verified=False,
            final_intent=classification.predicted_intent,
            verification_method="confidence_threshold",
            notes="Verification failed, proceeding with original intent but marked unverified."
        )
