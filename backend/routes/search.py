import asyncio
from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request
from crew.orchestrator import StartupValidatorOrchestrator
from core.dependencies import get_orchestrator
from utils.logger import get_logger
from guardrails.manager import GuardrailManager
from utils.progress import ProgressManager

logger = get_logger(__name__)

router = APIRouter()

@router.get("/search")
async def search(
    request: Request,
    response: Response,
    query: str = Query(..., min_length=10, max_length=1000, description="The startup idea to validate"),
    orchestrator: StartupValidatorOrchestrator = Depends(get_orchestrator)
):
    """
    Main endpoint for validating a startup idea.
    Triggers the full multi-agent workflow via the A2A Orchestrator.
    
    Session Cleanup Assumption:
    ProgressManager session is deliberately NOT cleaned up here in a 'finally' block 
    because the asynchronous SSE stream (/api/progress/{request_id}) needs time 
    to flush the final "completed" events to the client. Session cleanup is safely 
    handled by the background cleanup_task in app.py.
    """
    request_id = request.state.request_id
    response.headers["X-Request-ID"] = request_id
    await ProgressManager.create_session(request_id)
    
    try:
        # Avoid logging the full user input (startup idea) to prevent sensitive data leakage.
        logger.info(f"Received search request (Request ID: {request_id}, Input Length: {len(query)})")
        await ProgressManager.publish(request_id, "Validation", "running", "Validating input parameters...")
        
        # (1) Input Guardrail
        try:
            valid_query = GuardrailManager.validate_input(query)
            await ProgressManager.publish(request_id, "Validation", "completed", "Input validated successfully.")
        except ValueError as e:
            logger.warning(f"Input validation failed for Request ID {request_id}: {str(e)}")
            await ProgressManager.publish(request_id, "Validation", "failed", f"Validation error: {str(e)}")
            await ProgressManager.publish(request_id, "Orchestrator", "failed", "Pipeline aborted.")
            raise HTTPException(status_code=400, detail=str(e))
            
        return await orchestrator.validate_idea(valid_query, request_id)
    
    except asyncio.CancelledError:
        logger.warning(f"Request {request_id} was cancelled by the client. Halting orchestrator.")
        # Propagating CancelledError ensures FastAPI safely terminates the request and cancels downstream tasks.
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing search request {request_id}")
        await ProgressManager.publish(request_id, "System", "failed", "An unexpected error occurred.")
        await ProgressManager.publish(request_id, "Orchestrator", "failed", "Pipeline aborted.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")
