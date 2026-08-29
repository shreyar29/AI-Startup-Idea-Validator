import asyncio
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ProgressSession:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.queue = asyncio.Queue()
        self.created_at = time.time()
        self.is_completed = False

    async def publish(self, agent: str, status: str, message: str):
        if self.is_completed:
            return
            
        event = {
            "request_id": self.request_id,
            "agent": agent,
            "status": status,
            "message": message,
            "timestamp": int(time.time() * 1000)
        }
        await self.queue.put(event)
        
        if status in ["completed", "failed"] and agent == "Orchestrator":
            self.is_completed = True

class ProgressManager:
    _sessions: Dict[str, ProgressSession] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def create_session(cls, request_id: str) -> ProgressSession:
        async with cls._lock:
            session = ProgressSession(request_id)
            cls._sessions[request_id] = session
            return session

    @classmethod
    async def get_session(cls, request_id: str) -> Optional[ProgressSession]:
        async with cls._lock:
            return cls._sessions.get(request_id)

    @classmethod
    async def publish(cls, request_id: str, agent: str, status: str, message: str):
        session = await cls.get_session(request_id)
        if session:
            await session.publish(agent, status, message)

    @classmethod
    async def remove_session(cls, request_id: str):
        async with cls._lock:
            if request_id in cls._sessions:
                del cls._sessions[request_id]

    @classmethod
    async def cleanup_stale_sessions(cls, max_age_seconds: int = 3600):
        async with cls._lock:
            now = time.time()
            stale = [req_id for req_id, sess in cls._sessions.items() if now - sess.created_at > max_age_seconds]
            for req_id in stale:
                del cls._sessions[req_id]
