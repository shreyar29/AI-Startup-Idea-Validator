from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request
import uuid
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
    """
    request_id = request.state.request_id
    response.headers["X-Request-ID"] = request_id
    await ProgressManager.create_session(request_id)
    
    try:
        logger.info(f"Received search request for idea: {query}")
        await ProgressManager.publish(request_id, "Validation", "running", "Validating input parameters...")
        
        # (1) Input Guardrail
        try:
            valid_query = GuardrailManager.validate_input(query)
            await ProgressManager.publish(request_id, "Validation", "completed", "Input validated successfully.")
        except ValueError as e:
            logger.warning(f"Input validation failed: {str(e)}")
            await ProgressManager.publish(request_id, "Validation", "failed", f"Validation error: {str(e)}")
            await ProgressManager.publish(request_id, "Orchestrator", "failed", "Pipeline aborted.")
            raise HTTPException(status_code=400, detail=str(e))
            
        return await orchestrator.validate_idea(valid_query, request_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing search request")
        await ProgressManager.publish(request_id, "System", "failed", "An unexpected error occurred.")
        await ProgressManager.publish(request_id, "Orchestrator", "failed", "Pipeline aborted.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")
