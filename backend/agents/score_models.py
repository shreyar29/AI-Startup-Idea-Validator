from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime, timezone

class Verdict(str, Enum):
    EXCEPTIONAL = "Exceptional Opportunity"
    PROMISING = "Promising Opportunity"
    MODERATE = "Moderate Opportunity"
    HIGH_RISK = "High Risk Opportunity"
    NOT_RECOMMENDED = "Not Recommended"
    INSUFFICIENT_DATA = "Insufficient Data"

class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class StartupScorecard(BaseModel):
    overall_score: int
    market_score: int
    customer_score: int
    competition_score: int
    risk_score: int
    execution_score: int
    gtm_score: int
    verdict: Verdict
    confidence_level: Confidence
    score_explanation: List[str]
    investment_readiness: Optional[str] = None
    message: Optional[str] = None
    status: str = "success"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
