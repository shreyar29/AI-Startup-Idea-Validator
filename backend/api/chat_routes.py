import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any
import json

from core.container import container
from database.database import get_db
from database.models import Report
from auth.jwt_manager import get_current_user
from memory.chat_memory import ChatMemoryManager
from core.rate_limiter import limiter

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    question: str
    active_section: str = "overview"
    vera_mode: str = "Founder"

@router.post("/stream")
@limiter.limit("10/minute")
async def stream_chat(request: Request, chat_req: ChatRequest, db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SSE endpoint for streaming Vera responses.
    """
    # 1. Sanitize and validate input to prevent prompt injection / token exhaustion
    question = chat_req.question.strip()[:1000]
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    mode = chat_req.vera_mode.strip()[:50]
    section = chat_req.active_section.strip()[:50]

    # 2. Retrieve prior context
    try:
        context = await ChatMemoryManager.get_session_context(db, chat_req.session_id, current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
        
    # 3. Fetch report payload for context
    stmt = select(Report).where(Report.id == chat_req.session_id)
    report = (await db.execute(stmt)).scalar_one_or_none()
    report_context = ""
    
    if report and report.analysis_payload:
        # Token Optimization: Only include executive summary and active section
        payload = report.analysis_payload
        active_data = payload.get(section, {}) if section != "overview" else {}
        exec_summary = payload.get("executive_summary", {})
        
        context_payload = {
            "executive_summary": exec_summary,
            section: active_data
        }
        
        report_context = json.dumps(context_payload, indent=2)
        # Hard limit to prevent LLM context blowout
        if len(report_context) > 15000:
            report_context = report_context[:15000] + "\n...[TRUNCATED]"
        
    # 4. Save user message
    await ChatMemoryManager.save_message(db, chat_req.session_id, "user", question)
    
    # 5. Build Prompt safely
    history_text = "Chat History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in context[-5:]])
    system_prompt = f"""You are Vera, an elite AI startup strategist.
Right now, you must STRICTLY act as a {mode}.

If mode is 'Investor': Be highly skeptical, focus entirely on ROI, unit economics, defensibility, and traction. Ask hard questions.
If mode is 'Customer': Be a demanding user. Focus on usability, pricing, real-world value, and why you would switch from existing solutions.
If mode is 'Competitor': Be aggressive and analytical. Point out the startup's weaknesses and how you will crush them.
If mode is 'VC Partner': Focus on market size, team execution, fund return potential (10x+), and exit strategies.
If mode is 'Founder': Be a brutally honest, tactical co-founder. Focus on execution, survival, and prioritization.

REPORT CONTEXT:
{report_context}

RULES:
1. You MUST stream your response.
2. Answer based ONLY on the report context and history.
3. Be brutally honest, concise, and structured.
4. DO NOT break character. You are a {mode}. Speak exactly as a {mode} would."""

    user_prompt = f"{history_text}\n\nFounder Question: {question}"

    async def event_generator():
        llm = container.get_llm_provider()
        full_response = ""
        
        try:
            async for chunk in llm.generate_stream(system_prompt=system_prompt, user_prompt=user_prompt):
                if await request.is_disconnected():
                    break
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
            yield "data: [DONE]\n\n"
            
            # Save Vera's complete response
            if full_response.strip():
                await ChatMemoryManager.save_message(db, chat_req.session_id, "vera", full_response.strip())
            
        except Exception as e:
            # Prevent leaking sensitive exceptions
            safe_error = "An error occurred while communicating with the AI provider."
            yield f"data: {json.dumps({'error': safe_error})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.delete("/session/{session_id}")
async def clear_session(session_id: str, db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Clears the chat history for a given session.
    """
    from database.models import ChatMessage, ChatSession
    from sqlalchemy import delete
    
    # Verify ownership
    stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user["user_id"])
    session = (await db.execute(stmt)).scalar_one_or_none()
    
    if not session:
        # If it doesn't exist, it's already empty
        return {"status": "success", "message": "Session is empty"}
        
    delete_stmt = delete(ChatMessage).where(ChatMessage.session_id == session_id)
    await db.execute(delete_stmt)
    await db.commit()
    
    return {"status": "success", "message": "Session cleared"}
