import logging
from typing import Dict, Any, List
from backend.src.execution.llm_engine import LLMEngine

logger = logging.getLogger("documind.intelligence.agents")

class AgentSwarm:
    """
    SECTION 12: AI LAYER ENHANCEMENTS (MULTI-AGENT)
    Orchestrates specialized roles: Research, Analyst, and Critic.
    """
    def __init__(self, llm_engine: LLMEngine):
        self.engine = llm_engine

    async def analyze_with_critic(self, query: str, context: str) -> Dict[str, Any]:
        """
        The 'Critic' pattern: Generate -> Review -> Finalize.
        Aligned to JSONB-First Schema.
        """
        # 1. ANALYST Phase (Generation)
        analyst_prompt = "Act as a Senior Financial Analyst. Extract insights from context."
        initial_analysis = await self.engine.generate_response(query, context, mode="deep", system_prompt=analyst_prompt)
        
        # Guard: In case of engine level error
        if "error" in initial_analysis:
            return {
                "summary": initial_analysis.get("summary", "Analysis failed."),
                "intent": "ERROR",
                "confidence": 0.0,
                "error": initial_analysis["error"]
            }

        # 2. CRITIC Phase (Hallucination Guard)
        # Verify the analyst's work with specialized fact-checking prompt
        critic_prompt = f"""
        Act as a Fact-Checker. Review the analysis below for accuracy and hallucinations.
        CONTEXT: {context[:20000]}
        ANALYSIS: {initial_analysis.get('summary', 'No summary provided')}
        
        Output JSON: {{"critic_score": float, "is_verified": bool, "corrections": str}}
        """
        
        critic_review = await self.engine.generate_response("Critical Review", critic_prompt, mode="fast")
        
        # 3. CONSOLIDATION & SCHEMA ALIGNMENT (V2 JSONB-First)
        is_verified = critic_review.get("is_verified", True)
        critic_note = critic_review.get("corrections", "Data verification recommended.") if not is_verified else ""
        
        # Run Hallucination Guard
        calculated_confidence = HallucinationGuard.calculate_confidence(initial_analysis, context)
        critic_llm_score = float(critic_review.get("critic_score", 0.8))
        
        # Final score is the lower of the LLM critic or the Heuristic Guard
        final_confidence = min(critic_llm_score, calculated_confidence)
        
        if final_confidence < 0.75:
            is_verified = False
            critic_note += f" [System Guard Flag: Low confidence ({final_confidence}). Potential hallucination detected.]"

        # Final response construction
        final_summary = initial_analysis.get("summary", "")
        if critic_note:
            final_summary += f"\n\n[CRITIC NOTE]: {critic_note}"

        return {
            "summary": final_summary,
            "intent": initial_analysis.get("intent", "ANALYZE"),
            "confidence": final_confidence,
            "entities": initial_analysis.get("entities", {}),
            "execution_plan": initial_analysis.get("execution_plan", []),
            "metadata": {
                "is_hallucination_guarded": True,
                "critic_verified": is_verified,
                "version": "v2",
                "engine_metadata": initial_analysis.get("metadata", {})
            }
        }

import re

class HallucinationGuard:
    """
    Specific utility for source validation (Section 12.2).
    """
    @staticmethod
    def calculate_confidence(response: Dict[str, Any], context: str) -> float:
        # Heuristic: Check if keywords and numbers in summary exist in context
        summary = str(response.get("summary", ""))
        if not summary or not context: return 0.5
        
        context_low = context.lower()
        
        # 1. Extract exact numbers, percentages, and dollar amounts (e.g., $10M, 15%, 2024)
        numbers = set(re.findall(r'\$?\d+(?:\.\d+)?[a-zA-Z%]*', summary))
        
        # 2. Extract capitalized phrases (Potential Entities)
        entities = set(re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', summary))
        
        total_checks = len(numbers) + len(entities)
        if total_checks == 0:
            return 0.90 # High confidence if no specific factual claims are made

        hits = 0
        
        for num in numbers:
            if num.lower() in context_low:
                hits += 1
            else:
                logger.warning(f"Hallucination Guard: Metric '{num}' not found in context.")

        for ent in entities:
            if ent.lower() in context_low:
                hits += 1
            else:
                logger.warning(f"Hallucination Guard: Entity '{ent}' not found in context.")

        confidence_score = hits / total_checks
        
        # Scale to a 0.4 - 1.0 range (we don't drop to 0 for just rephrasing)
        normalized_confidence = 0.4 + (confidence_score * 0.6)
        
        return round(normalized_confidence, 2)
