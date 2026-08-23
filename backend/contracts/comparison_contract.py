from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class ComparisonContract(BaseAgentContract):
    executive_summary: Dict[str, Any] = Field(default_factory=dict)
    feature_comparison: List[Dict[str, Any]] = Field(default_factory=list)
    feature_summary: Dict[str, Any] = Field(default_factory=dict)
    competitive_advantages: List[str] = Field(default_factory=list)
    market_gaps: List[str] = Field(default_factory=list)
    validation_score: int = 0
    innovation_score: int = 0
    investment_grade: str = "PENDING"
    scoring_breakdown: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    recommendations: List[str] = Field(default_factory=list)
    summary: str = ""
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
