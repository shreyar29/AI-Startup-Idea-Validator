import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from database.database import get_db
from database.models import Report
from auth.jwt_manager import get_current_user
from export.pdf_exporter import PDFExporter
from export.ppt_exporter import PPTExporter

router = APIRouter(prefix="/api/export", tags=["export"])

from pydantic import BaseModel
from typing import Dict, Any, Optional

class ExportRequest(BaseModel):
    startup_idea: str
    analysis_payload: Dict[str, Any]
    validation_score: float

@router.post("/pdf")
async def export_pdf(request: ExportRequest):
    """
    Export validation report as an Investor PDF.
    """
    filepath = await PDFExporter.generate_investor_report(request.model_dump())
    
    return FileResponse(path=filepath, filename="VentureLens_Investor_Report.pdf", media_type="application/pdf")

@router.post("/ppt")
async def export_ppt(request: ExportRequest):
    """
    Export validation report as a Pitch Deck PPTX.
    """
    filepath = await PPTExporter.generate_pitch_deck(request.model_dump())
    
    return FileResponse(path=filepath, filename="VentureLens_Pitch_Deck.pptx", media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
