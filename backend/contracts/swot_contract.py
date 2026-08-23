from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract

class SWOTContract(BaseAgentContract):
    strengths: List[Dict[str, Any]] = Field(default_factory=list)
    weaknesses: List[Dict[str, Any]] = Field(default_factory=list)
    opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 0.5
    confidence: str = "MEDIUM"
    source_traceability: List[Dict[str, Any]] = Field(default_factory=list)
