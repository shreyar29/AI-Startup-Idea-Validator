from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

class ExecSummary(BaseModel):
    founder_recommendation: Optional[str] = None
    market_fit: Optional[str] = None

class StartupScore(BaseModel):
    overall_score: int = 0
    market_score: int = 0
    competition_score: int = 0
    execution_score: int = 0
    risk_score: int = 0
    gtm_score: int = 0
    verdict: str = "Requires Further Analysis"
    confidence_level: str = "N/A"
    score_explanation: List[str] = Field(default_factory=list)

class Market(BaseModel):
    market_size: Optional[str] = None
    growth_rate: Optional[str] = None
    market_maturity: Optional[str] = None
    market_trends: List[str] = Field(default_factory=list)

class Competitor(BaseModel):
    name: str = "Unknown"
    strengths: Union[str, List[Any], Any] = "N/A"
    weaknesses: Union[str, List[Any], Any] = "N/A"

class CompetitorAnalysis(BaseModel):
    competitors: List[Competitor] = Field(default_factory=list)
    gap_analysis: Union[str, List[Any], Any] = "No gaps identified."

class SWOT(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)

class RiskItem(BaseModel):
    category: str = "General"
    risk: str = "Unknown Risk"
    severity: str = "Medium"
    likelihood: str = "Medium"
    impact: str = "Medium"
    mitigation: str = "Further validation is recommended."
    time_horizon: str = "Medium-term"
    risk_score: float = 0.0

class Risk(BaseModel):
    top_risks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    overall_risk_level: str = "Unknown"
    overall_risk_score: int = 0

class MVP(BaseModel):
    core_features: List[str] = Field(default_factory=list)

class GTM(BaseModel):
    launch_channels: Union[List[str], List[Any], Any] = Field(default_factory=list)
    acquisition_channels: Union[List[str], List[Any], Any] = Field(default_factory=list)

class FinalEvaluation(BaseModel):
    executive_summary: Optional[Any] = None
    startup_score: StartupScore = Field(default_factory=StartupScore)
    market: Market = Field(default_factory=Market)
    competitor: CompetitorAnalysis = Field(default_factory=CompetitorAnalysis)
    swot: SWOT = Field(default_factory=SWOT)
    risk: Risk = Field(default_factory=Risk)
    mvp: MVP = Field(default_factory=MVP)
    gtm: GTM = Field(default_factory=GTM)
    customer: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"

class ReportContext(BaseModel):
    idea: Dict[str, Any] = Field(default_factory=dict)
    final_evaluation: FinalEvaluation = Field(default_factory=FinalEvaluation)
    
    class Config:
        extra = "allow"
