import asyncio
import uuid
import logging
from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

from core.rate_limiter import limiter
from core.dependencies import get_orchestrator
from crew.orchestrator import StartupValidatorOrchestrator
from utils.progress import ProgressManager
from core.security import SecurityManager
from database.database import get_db
from database.models import Report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/validation", tags=["validation"])

# In a fully unified architecture, jobs can be stored in the database or Redis.
# For simplicity and to avoid Redis dependency, we will store pending jobs in memory 
# for polling, and persist the final report to the DB.
_IN_MEMORY_JOBS = {}

async def run_validation_background(job_id: str, query: str, orchestrator: StartupValidatorOrchestrator):
    try:
        result = await orchestrator.validate_idea(query, job_id)
        
        # In a real enterprise system, we would associate this with the logged-in user.
        # Since this demo might run unauthenticated initially, we use a placeholder user ID
        # or require auth. For now, we just store it in memory for the polling client to retrieve.
        # Once retrieved, the client (or a subsequent authenticated call) can formally persist it to a Workspace Project.
        
        _IN_MEMORY_JOBS[job_id] = {"status": "SUCCESS", "result": result}
    except Exception as e:
        logger.exception(f"Background validation failed for {job_id}")
        _IN_MEMORY_JOBS[job_id] = {"status": "FAILURE", "error": str(e)}

@router.post("")
@router.post("/")
@limiter.limit("10/minute")
async def start_validation(
    request: Request,
    response: Response,
    query: str = Query(..., min_length=10, max_length=1000, description="The startup idea to validate"),
    orchestrator: StartupValidatorOrchestrator = Depends(get_orchestrator)
):
    """
    Main endpoint for validating a startup idea.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    response.headers["X-Request-ID"] = request_id
    
    try:
        valid_query = SecurityManager.sanitize_prompt(query)
    except Exception as e:
        logger.warning(f"Security validation failed for Request ID {request_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    await ProgressManager.create_session(request_id)
    
    try:
        logger.info(f"Received validation request (Request ID: {request_id}, Input Length: {len(query)})")
        await ProgressManager.publish(request_id, "Validation", "running", "Validating input parameters...")
        await ProgressManager.publish(request_id, "Validation", "completed", "Input validated successfully.")
        
        _IN_MEMORY_JOBS[request_id] = {"status": "PENDING"}
        asyncio.create_task(run_validation_background(request_id, valid_query, orchestrator))
        
        return {"job_id": request_id, "request_id": request_id, "status": "queued"}
    
    except Exception as e:
        logger.exception(f"Error queuing validation request {request_id}")
        await ProgressManager.publish(request_id, "System", "failed", "An unexpected error occurred.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while queuing your request.")

@router.get("/{job_id}/result")
async def get_validation_result(job_id: str):
    task_result = _IN_MEMORY_JOBS.get(job_id)
    if not task_result:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if task_result["status"] == "PENDING":
        return {"status": "pending"}
    elif task_result["status"] == "SUCCESS":
        return {"status": "SUCCESS", "result": task_result["result"]}
    else:
        raise HTTPException(status_code=500, detail=task_result.get("error", "Unknown error"))
