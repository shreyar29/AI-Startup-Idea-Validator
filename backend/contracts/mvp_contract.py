from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class MVPContract(BaseAgentContract):
    core_features: List[Dict[str, Any]] = Field(default_factory=list)
    optional_features: List[Dict[str, Any]] = Field(default_factory=list)
    future_features: List[Dict[str, Any]] = Field(default_factory=list)
    mvp_scope: str = "Unknown"
    estimated_complexity: str = "Medium"
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
