import asyncio
import uuid
from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request
from core.rate_limiter import limiter
from crew.orchestrator import StartupValidatorOrchestrator
from core.dependencies import get_orchestrator
from utils.logger import get_logger
from guardrails.manager import GuardrailManager
from utils.progress import ProgressManager
from core.security import SecurityManager

logger = get_logger(__name__)

router = APIRouter()

# In-memory store for background task results (Safe fallback for Celery)
validation_results = {}

async def run_validation_background(request_id: str, query: str, orchestrator: StartupValidatorOrchestrator):
    try:
        result = await orchestrator.validate_idea(query, request_id)
        validation_results[request_id] = {"status": "SUCCESS", "result": result}
    except Exception as e:
        logger.exception(f"Background validation failed for {request_id}")
        validation_results[request_id] = {"status": "FAILURE", "error": str(e)}

@router.post("/validation")
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
        
        # Queue the job as an asyncio background task
        validation_results[request_id] = {"status": "PENDING"}
        asyncio.create_task(run_validation_background(request_id, valid_query, orchestrator))
        
        return {"job_id": request_id, "request_id": request_id, "status": "queued"}
    
    except Exception as e:
        logger.exception(f"Error queuing validation request {request_id}")
        await ProgressManager.publish(request_id, "System", "failed", "An unexpected error occurred.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while queuing your request.")

@router.get("/validation/{job_id}/result")
async def get_validation_result(job_id: str):
    task_result = validation_results.get(job_id)
    if not task_result:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if task_result["status"] == "PENDING":
        return {"status": "pending"}
    elif task_result["status"] == "SUCCESS":
        return {"status": "SUCCESS", "result": task_result["result"]}
    else:
        raise HTTPException(status_code=500, detail=task_result.get("error", "Unknown error"))
