from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, List

from database.database import get_db
from database.models import Report, ChatSession
from auth.jwt_manager import get_current_user, RequireRole
from telemetry.metrics_service import MetricsService

router = APIRouter(prefix="/api/workspace", tags=["workspace"])

@router.get("/")
async def get_founder_workspace(
    db: AsyncSession = Depends(get_db), 
    current_user: Dict[str, Any] = Depends(RequireRole(["founder", "admin", "user"]))
):
    """
    Aggregated endpoint returning everything needed to render the Founder Workspace UI.
    """
    user_id = current_user["user_id"]
    
    # 1. Fetch Reports
    report_stmt = select(Report).where(Report.user_id == user_id).order_by(Report.created_at.desc())
    reports = (await db.execute(report_stmt)).scalars().all()
    
    # 2. Fetch Active Chat Sessions (Vera Memory)
    chat_stmt = select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc())
    chat_sessions = (await db.execute(chat_stmt)).scalars().all()
    
    return {
        "reports": [
            {
                "id": r.id, 
                "startup_idea": r.startup_idea, 
                "validation_score": r.validation_score, 
                "version": r.version,
                "created_at": r.created_at
            } for r in reports
        ],
        "active_chats": [
            {"id": c.id, "report_id": c.report_id, "created_at": c.created_at} for c in chat_sessions
        ],
        "metrics": {
            "total_ideas_validated": len(reports),
            "mesh_health": MetricsService.get_mesh_health()["mesh_health"]
        }
    }
