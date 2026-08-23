from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class CustomerContract(BaseAgentContract):
    target_customer_segments: List[Dict[str, Any]] = Field(default_factory=list)
    pain_points: List[Dict[str, Any]] = Field(default_factory=list)
    unmet_needs: List[Dict[str, Any]] = Field(default_factory=list)
    customer_personas: List[Dict[str, Any]] = Field(default_factory=list)
    customer_journey: List[Dict[str, Any]] = Field(default_factory=list)
    sentiment: Dict[str, Any] = Field(default_factory=dict)
    feature_demand: List[Dict[str, Any]] = Field(default_factory=list)
    customer_validation_metrics: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
