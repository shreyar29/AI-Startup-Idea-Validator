from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class RiskContract(BaseAgentContract):
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    overall_risk_score: int = 50
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
