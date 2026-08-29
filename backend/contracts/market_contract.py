from pydantic import Field
from typing import List, Dict, Any
from .base_contract import BaseAgentContract


class MarketContract(BaseAgentContract):
    market_size: str = "Unknown"
    growth_rate: str = "Unknown"
    market_maturity: str = "Unknown"
    tam: str = "Unknown"
    sam: str = "Unknown"
    som: str = "Unknown"
    methodology: str = "Data unavailable"
    market_segmentation: List[str] = Field(default_factory=list)
    growth_drivers: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    industry_insights: List[str] = Field(default_factory=list)
    regulations: List[str] = Field(default_factory=list)
    market_summary: str = "Unknown"
    opportunity_score: int = 50
    confidence_score: str = "Medium"
