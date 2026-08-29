from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
import re
from database.database import get_db
from database.models import Report
from core.container import container

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

class SimulatorRequest(BaseModel):
    report_id: str
    assumption: str
    startup_idea: Optional[str] = None
    current_score: Optional[int] = None

@router.post("/score")
async def simulate_score(request: SimulatorRequest, db: AsyncSession = Depends(get_db)):
    """
    LLM-powered What-If scenario evaluator.
    Identifies affected areas, recalculates relevant metrics, and returns a new recommendation.
    """
    stmt = select(Report).where(Report.id == request.report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    current_score = request.current_score if request.current_score else (report.validation_score if report else 79)
    startup_idea = request.startup_idea if request.startup_idea else (report.startup_idea if report else "A new startup")
    
    # Extract actual context
    payload = report.analysis_payload if report else {}
    market = payload.get("market_agent", {})
    customer = payload.get("customer_agent", {})
    competitor = payload.get("competitor_agent", {})
    
    context_str = f"""
    Market Size/Growth: {market.get('market_size', 'Unknown')} / {market.get('growth_rate', 'Unknown')}
    Target Customer: {str(customer.get('target_customer_segments', []))[:200]}
    Competitors: {str(competitor.get('competitors', []))[:200]}
    """
    
    prompt = f"""
    You are a Startup Viability Analyst. A founder has provided an original startup idea and wants to simulate a 'What-If' scenario.
    
    Original Startup Idea: {startup_idea}
    What-If Assumption: {request.assumption}
    Current validation score: {current_score}/100.
    
    Actual Startup Context:
    {context_str}
    
    Based on the Actual Startup Context and the What-If Assumption, calculate the impact on four key metrics (Market Potential, Customer Fit, Competitive Risk, Overall Viability).
    Estimate the 'current' metric value (e.g. out of 100 or High/Medium/Low) based on the context, and then the 'scenario' metric value after applying the assumption.
    
    Return ONLY a raw valid JSON object (no markdown formatting, no code blocks) with the following structure:
    {{
        "metrics": [
            {{"name": "Market Potential", "current": "XX/100", "scenario": "YY/100"}},
            {{"name": "Customer Fit", "current": "XX/100", "scenario": "YY/100"}},
            {{"name": "Competitive Risk", "current": "High/Med/Low", "scenario": "High/Med/Low"}},
            {{"name": "Overall Viability", "current": "{current_score}/100", "scenario": "YY/100"}}
        ],
        "recommendation": "Your brief recommendation here explaining the actual recalculation based on the context.",
        "affected_areas": ["Market", "Customer", "Pricing"]
    }}
    """
    
    llm = container.get_llm_provider()
    try:
        llm_response = await llm.generate_response(
            system_prompt="You are a data-driven startup analyst. Always return raw JSON. Do not hallucinate, derive estimates logically.",
            user_prompt=prompt
        )
        
        # Clean response
        clean_resp = re.sub(r'```json\s*', '', llm_response)
        clean_resp = re.sub(r'```', '', clean_resp).strip()
        
        parsed_data = json.loads(clean_resp)
        return parsed_data
        
    except Exception as e:
        # Fallback if LLM fails
        return {
            "metrics": [
                {"name": "Market Potential", "current": "80/100", "scenario": "80/100"},
                {"name": "Customer Fit", "current": "80/100", "scenario": "80/100"},
                {"name": "Competitive Risk", "current": "Medium", "scenario": "Medium"},
                {"name": "Overall Viability", "current": f"{current_score}/100", "scenario": f"{current_score}/100"}
            ],
            "recommendation": f"Failed to run complex simulation. ({str(e)})",
            "affected_areas": ["General"]
        }
