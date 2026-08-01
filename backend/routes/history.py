from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import json
from typing import Optional
from db import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class HistoryEntry(BaseModel):
    user_id: int
    prompt: str
    response_data: dict

@router.post("/history")
def save_history(entry: HistoryEntry):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (user_id, prompt, response_data) VALUES (?, ?, ?)",
            (entry.user_id, entry.prompt, json.dumps(entry.response_data))
        )
        conn.commit()
        history_id = cursor.lastrowid
        logger.info(f"Saved new history entry (ID: {history_id}) for user {entry.user_id}")
        return {"status": "success", "id": history_id}

@router.get("/history/{user_id}")
def get_history(user_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, prompt, response_data, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        logger.info(f"Retrieved {len(rows)} history entries for user {user_id}")
        
        history = []
        for row in rows:
            history.append({
                "id": row["id"],
                "prompt": row["prompt"],
                "response_data": json.loads(row["response_data"]),
                "created_at": row["created_at"]
            })
            
        return {"history": history}
