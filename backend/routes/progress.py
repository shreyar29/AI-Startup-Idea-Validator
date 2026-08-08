from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
from utils.progress import ProgressManager

router = APIRouter()

@router.get("/progress/{request_id}")
async def get_progress(request_id: str, request: Request):
    session = await ProgressManager.get_session(request_id)
    retries = 0
    while not session and retries < 20: # Wait up to 10 seconds for session creation
        await asyncio.sleep(0.5)
        session = await ProgressManager.get_session(request_id)
        retries += 1

    if not session:
        raise HTTPException(status_code=404, detail="Progress session not found or already completed.")

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    event = await asyncio.wait_for(session.queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    if isinstance(event, dict):
                        if event.get("status") in ["completed", "failed"] and event.get("agent") == "Orchestrator":
                            break
                except asyncio.TimeoutError:
                    # Emit SSE comment to keep reverse proxies alive
                    yield ": keep-alive\n\n"
        finally:
            pass # Session cleanup is handled by the background task, so clients can reconnect

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
