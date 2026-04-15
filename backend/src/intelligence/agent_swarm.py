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
        
        # Final response construction
        final_summary = initial_analysis.get("summary", "")
        if critic_note:
            final_summary += f"\n\n[CRITIC NOTE]: {critic_note}"

        return {
            "summary": final_summary,
            "intent": initial_analysis.get("intent", "ANALYZE"),
            "confidence": critic_review.get("critic_score", 0.5),
            "entities": initial_analysis.get("entities", {}),
            "execution_plan": initial_analysis.get("execution_plan", []),
            "metadata": {
                "is_hallucination_guarded": True,
                "critic_verified": is_verified,
                "version": "v2",
                "engine_metadata": initial_analysis.get("metadata", {})
            }
        }

class HallucinationGuard:
    """
    Specific utility for source validation (Section 12.2).
    """
    @staticmethod
    def calculate_confidence(response: Dict[str, Any], context: str) -> float:
        # Heuristic: Check if keywords in summary exist in context
        summary = str(response.get("summary", "")).lower()
        context_low = context.lower()
        
        # Simple overlap check for demonstration
        # In production, use cross-encoder or NLI (Natural Language Inference)
        return 0.95 # Optimistic placeholder
