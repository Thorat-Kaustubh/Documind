from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum

class IntentType(str, Enum):
    TREND_ANALYSIS = "TREND_ANALYSIS"
    FINANCIAL_EXTRACTION = "FINANCIAL_EXTRACTION"
    COMPARATIVE_ANALYSIS = "COMPARATIVE_ANALYSIS"
    GENERAL_QUERY = "GENERAL_QUERY"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    NEWS_RETRIEVAL = "NEWS_RETRIEVAL"
    UNKNOWN = "UNKNOWN"

class FinancialEntities(BaseModel):
    company: Optional[str] = Field(None, description="Company name or ticker")
    metrics: List[str] = Field(default_factory=list, description="Financial metrics like revenue, ebitda, etc.")
    time_range: Optional[str] = Field(None, description="Time range for analysis e.g., '5y', 'Q3 2023'")
    sector: Optional[str] = Field(None, description="Industrial sector")

class QueryPlan(BaseModel):
    intent: IntentType
    entities: FinancialEntities
    execution_steps: List[Literal["sql", "rag", "llm", "web_search"]]
    confidence: float
    reasoning: str

class IntentClassification(BaseModel):
    predicted_intent: IntentType
    confidence: float
    raw_scores: Optional[Dict[str, float]] = None

class VerificationResult(BaseModel):
    is_verified: bool
    final_intent: IntentType
    verification_method: Literal["confidence_threshold", "rule_based", "llm_fallback"]
    notes: Optional[str] = None
