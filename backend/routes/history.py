from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import json
from db import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Assumption: Authorization is expected to be enforced by a future authentication layer (e.g., JWT middleware).
# For now, we trust the provided user_id to preserve existing functionality without introducing new security paradigms.

class HistoryEntry(BaseModel):
    user_id: int = Field(..., gt=0, description="The ID of the user")
    prompt: str = Field(..., min_length=5, max_length=2000, strip_whitespace=True, description="The validated startup idea")
    response_data: dict = Field(..., description="The comprehensive validation result JSON")

@router.post("/history")
def save_history(entry: HistoryEntry, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (user_id, prompt, response_data) VALUES (?, ?, ?)",
                (entry.user_id, entry.prompt, json.dumps(entry.response_data))
            )
            conn.commit()
            history_id = cursor.lastrowid
            logger.info(f"[{request_id}] Saved new history entry (ID: {history_id}) for user {entry.user_id}")
            return {"status": "success", "id": history_id}
    except Exception:
        logger.exception(f"[{request_id}] Internal error saving history for user {entry.user_id}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while saving history.")

@router.get("/history/{user_id}")
def get_history(user_id: int, request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, prompt, response_data, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            logger.info(f"[{request_id}] Retrieved {len(rows)} history entries for user {user_id}")
            
            history = []
            for row in rows:
                try:
                    parsed_response = json.loads(row["response_data"])
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"[{request_id}] Malformed JSON found in history entry ID: {row['id']}")
                    parsed_response = {}
                    
                history.append({
                    "id": row["id"],
                    "prompt": row["prompt"],
                    "response_data": parsed_response,
                    "created_at": row["created_at"]
                })
                
            return {"history": history}
    except Exception:
        logger.exception(f"[{request_id}] Internal error retrieving history for user {user_id}")
        raise HTTPException(status_code=500, detail="An internal server error occurred while retrieving history.")
