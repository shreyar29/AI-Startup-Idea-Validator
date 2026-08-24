from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from database.database import get_db
from database.models import Report
from auth.jwt_manager import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reports", tags=["reports"])

class ReportCreate(BaseModel):
    user_id: str = Field(..., description="The ID of the user")
    prompt: str = Field(..., description="The validated startup idea")
    response_data: Dict[str, Any] = Field(..., description="The comprehensive validation result JSON")

@router.post("")
async def create_report(entry: ReportCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a new report. Replaces legacy /history endpoint.
    """
    new_report = Report(
        user_id=entry.user_id,
        startup_idea=entry.prompt,
        analysis_payload=entry.response_data,
        validation_score=entry.response_data.get("startup_score_agent", {}).get("overall_score", 0)
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return {"status": "success", "id": new_report.id}

@router.get("")
async def get_reports(db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Fetch all reports for the authenticated user for the Startup Workspace.
    """
    stmt = select(Report).where(Report.user_id == current_user["user_id"]).order_by(Report.created_at.desc())
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "startup_idea": r.startup_idea,
            "validation_score": r.validation_score,
            "created_at": r.created_at
        }
        for r in reports
    ]

@router.get("/{report_id}")
async def get_report_details(report_id: str, db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Fetch specific report details.
    """
    stmt = select(Report).where(Report.id == report_id, Report.user_id == current_user["user_id"])
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": report.id,
        "startup_idea": report.startup_idea,
        "analysis_payload": report.analysis_payload,
        "validation_score": report.validation_score,
        "version": report.version,
        "parent_report_id": report.parent_report_id,
        "created_at": report.created_at
    }

@router.post("/{report_id}/branch")
async def branch_report(report_id: str, db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Branches an existing report, creating a Version N+1.
    Allows founders to pivot their idea and compare.
    """
    stmt = select(Report).where(Report.id == report_id, Report.user_id == current_user["user_id"])
    result = await db.execute(stmt)
    parent_report = result.scalar_one_or_none()
    
    if not parent_report:
        raise HTTPException(status_code=404, detail="Parent report not found")
        
    new_report = Report(
        user_id=current_user["user_id"],
        startup_idea=parent_report.startup_idea,
        analysis_payload=parent_report.analysis_payload,
        validation_score=parent_report.validation_score,
        version=parent_report.version + 1,
        parent_report_id=parent_report.id
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    
    return {"message": "Report branched successfully", "new_report_id": new_report.id, "version": new_report.version}
