from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ExecSummary(BaseModel):
    founder_recommendation: str = ""
    biggest_opportunity: str = "Unknown"
    biggest_risk: str = "Unknown"
    recommended_next_step: str = "Unknown"

class MarketData(BaseModel):
    market_size: str = "Unknown"
    growth_rate: str = "Unknown"
    market_trends: List[str] = Field(default_factory=list)

class CustomerData(BaseModel):
    target_segments: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)

class CompetitorData(BaseModel):
    competitors: List[Any] = Field(default_factory=list)
    competitive_gaps: List[str] = Field(default_factory=list)

class StrategyData(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)

class RiskActionData(BaseModel):
    top_risks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class ExecutionData(BaseModel):
    core_features: List[str] = Field(default_factory=list)
    mvp_scope: str = "Unknown"
    target_segment: str = "Unknown"
    acquisition_channels: List[str] = Field(default_factory=list)
    pricing_strategy: str = "Unknown"
    launch_plan: List[str] = Field(default_factory=list)

class RenderSchema(BaseModel):
    metadata: Dict[str, Any] = Field(default_factory=dict)
    verdict: str = "No verdict available"
    overall_score: int = 0
    executive_summary: ExecSummary = Field(default_factory=ExecSummary)
    market: MarketData = Field(default_factory=MarketData)
    customer: CustomerData = Field(default_factory=CustomerData)
    competitor: CompetitorData = Field(default_factory=CompetitorData)
    strategy: StrategyData = Field(default_factory=StrategyData)
    risk_and_action: RiskActionData = Field(default_factory=RiskActionData)
    execution: ExecutionData = Field(default_factory=ExecutionData)

    class Config:
        extra = "allow"
