from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class ChartDataItem(BaseModel):
    """Single point in a chart (e.g., date vs price)."""
    label: str = Field(..., description="The label for the X-axis (e.g., '2024-Q1')")
    value: Union[float, int] = Field(..., description="The numeric value for the Y-axis")
    extra: Optional[Dict[str, Any]] = Field(default=None, description="Metadata for tooltips")

class InsightCard(BaseModel):
    """High-level insight block to display next to charts."""
    title: str
    content: str
    sentiment: Optional[str] = "neutral" # neutral, positive, negative

class VisualIntelligence(BaseModel):
    """
    Strict Schema for AI-Generated Visuals.
    Ensures Recharts compatibility and system stability.
    """
    type: str = Field(..., pattern="^(line|bar|pie|area|radar|none)$")
    chart_data: List[ChartDataItem] = Field(default_factory=list)
    insight_cards: List[InsightCard] = Field(default_factory=list)
    recommendation: Optional[str] = None

class DocumindResponse(BaseModel):
    """Standardized response from the AIBroker."""
    summary: str = Field(..., description="Professional markdown analysis")
    sentiment: Dict[str, Any] = Field(
        default_factory=lambda: {"score": 0.5, "label": "Neutral"}
    )
    visuals: VisualIntelligence
    sources: List[str] = Field(default_factory=list)

def validate_visuals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Utility to validate and repair AI-generated JSON.
    Guarantees the frontend receives a valid structure.
    """
    try:
        validated = DocumindResponse(**data)
        return validated.model_dump()
    except Exception as e:
        # Fallback/Repair logic
        return {
            "summary": data.get("summary", "Analysis available (Format optimized)."),
            "sentiment": data.get("sentiment", {"score": 0.5, "label": "Neutral"}),
            "visuals": {
                "type": "none",
                "chart_data": [],
                "insight_cards": []
            },
            "error": f"Schema Validation Error: {str(e)}"
        }
