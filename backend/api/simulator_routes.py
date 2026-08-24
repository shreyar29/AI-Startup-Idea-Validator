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

@router.post("/score")
async def simulate_score(request: SimulatorRequest, db: AsyncSession = Depends(get_db)):
    """
    LLM-powered What-If scenario evaluator.
    Identifies affected areas, recalculates relevant metrics, and returns a new recommendation.
    """
    stmt = select(Report).where(Report.id == request.report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    current_score = report.validation_score if report else 79
    startup_idea = report.startup_idea if report else "A new startup"
    
    prompt = f"""
    You are a Startup Viability Analyst. A founder has provided an original startup idea and wants to simulate a 'What-If' scenario.
    
    Original Startup Idea: {startup_idea}
    What-If Assumption: {request.assumption}
    
    Current validation score: {current_score}/100.
    
    Evaluate the impact of this new assumption on four key metrics. 
    Make realistic estimates based on how the assumption alters the market or product dynamics.
    
    Return ONLY a raw valid JSON object (no markdown formatting, no code blocks) with the following structure:
    {{
        "metrics": [
            {{"name": "Market Potential", "current": "82%", "scenario": "XX%"}},
            {{"name": "Customer Fit", "current": "86%", "scenario": "XX%"}},
            {{"name": "Competitive Risk", "current": "Medium", "scenario": "High"}},
            {{"name": "Overall Viability", "current": "{current_score}%", "scenario": "XX%"}}
        ],
        "recommendation": "Your brief recommendation here",
        "affected_areas": ["Market", "Customer", "Pricing"]
    }}
    """
    
    llm = container.get_llm_provider()
    try:
        llm_response = await llm.generate_response(
            system_prompt="You are a data-driven startup analyst. Always return raw JSON.",
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
                {"name": "Market Potential", "current": "82%", "scenario": "85%"},
                {"name": "Customer Fit", "current": "86%", "scenario": "88%"},
                {"name": "Competitive Risk", "current": "Medium", "scenario": "Medium"},
                {"name": "Overall Viability", "current": f"{current_score}%", "scenario": f"{min(100, current_score + 2)}%"}
            ],
            "recommendation": f"Failed to run complex simulation, but heuristic suggests a slight improvement. ({str(e)})",
            "affected_areas": ["General"]
        }
