import logging
from .intent_classifier import IntentClassifier
from .intent_verifier import IntentVerificationLayer
from .entity_extractor import FinancialNER
from .planner import QueryPlanner
from .models import QueryPlan

logger = logging.getLogger("documind.intelligence")

class QueryUnderstandingLayer:
    """
    Unified Entry Point for Documind Query Intelligence.
    Implements Section 3 of the V2 Architecture.
    """
    def __init__(self):
        self.classifier = IntentClassifier()
        self.verifier = IntentVerificationLayer()
        self.ner = FinancialNER()
        self.planner = QueryPlanner()

    async def analyze_query(self, query: str) -> QueryPlan:
        """
        Full pipeline: Classify -> Verify -> Extract Entities -> Plan.
        """
        logger.info(f"Analyzing query: '{query}'")
        
        # 1. Classification
        classification = await self.classifier.classify(query)
        logger.info(f"Initial Classification: {classification.predicted_intent} (Conf: {classification.confidence})")
        
        # 2. Verification
        verification = await self.verifier.verify(query, classification)
        logger.info(f"Verified Intent: {verification.final_intent} via {verification.verification_method}")
        
        # 3. Entity Extraction
        entities = await self.ner.extract(query)
        logger.info(f"Extracted Entities: {entities.model_dump()}")
        
        # 4. Query Planning
        plan = self.planner.generate_plan(
            intent=verification.final_intent,
            entities=entities,
            verification_notes=verification.notes or ""
        )
        
        logger.info(f"Final Query Plan Generated: {plan.execution_steps}")
        return plan
