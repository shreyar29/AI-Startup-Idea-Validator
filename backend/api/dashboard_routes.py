from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from database.database import get_db
from database.models import Report
from auth.jwt_manager import get_current_user
from telemetry.metrics_service import MetricsService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/metrics")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns aggregated metrics for the Founder's Executive Dashboard.
    """
    stmt = select(Report.validation_score).where(Report.user_id == current_user["user_id"])
    result = await db.execute(stmt)
    scores = result.scalars().all()
    
    avg_score = sum(scores) / len(scores) if scores else 0
    total_ideas = len(scores)
    
    return {
        "total_ideas_validated": total_ideas,
        "average_validation_score": round(avg_score, 1),
        "mesh_health": MetricsService.get_mesh_health()["mesh_health"],
        "recent_scores": scores[-5:] # Last 5 scores for trend graph
    }
