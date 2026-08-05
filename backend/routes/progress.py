from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
from utils.progress import ProgressManager

router = APIRouter()

@router.get("/progress/{request_id}")
async def get_progress(request_id: str, request: Request):
    session = await ProgressManager.get_session(request_id)
    if not session:
        raise HTTPException(status_code=404, detail="Progress session not found or already completed.")

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    event = await asyncio.wait_for(session.queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    if event["status"] in ["completed", "failed"] and event["agent"] == "Orchestrator":
                        break
                except asyncio.TimeoutError:
                    # Keep-alive or just continue checking for disconnection
                    continue
        finally:
            await ProgressManager.remove_session(request_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
