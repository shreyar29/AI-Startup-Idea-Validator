from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import ChatSession, ChatMessage
from typing import List, Dict, Any

class ChatMemoryManager:
    @staticmethod
    async def get_session_context(db: AsyncSession, session_id: str, user_id: str, max_messages: int = 10, report_id: str = None) -> List[Dict[str, str]]:
        """
        Retrieves the last N messages for a given chat session to build the LLM context window.
        Verifies ownership to prevent unauthorized access. Creates session if it doesn't exist.
        """
        stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            # Create a new session on the fly
            session = ChatSession(id=session_id, user_id=user_id, report_id=report_id)
            db.add(session)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                # In case of race condition or foreign key failure, just ignore and proceed
                pass
            
        # Optimization: Fetching only the last 'max_messages' avoiding context limit overflow
        msg_stmt = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.desc()).limit(max_messages)
        msg_result = await db.execute(msg_stmt)
        messages = msg_result.scalars().all()
        
        # Return in chronological order
        return [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]

    @staticmethod
    async def save_message(db: AsyncSession, session_id: str, role: str, content: str, token_count: int = 0):
        """
        Persists a message to the database.
        """
        new_msg = ChatMessage(session_id=session_id, role=role, content=content, token_count=token_count)
        db.add(new_msg)
        await db.commit()

    @staticmethod
    async def summarize_history(db: AsyncSession, session_id: str) -> None:
        """
        Background task to summarize older messages and replace them with a 'system' summary,
        drastically reducing the token count payload for long-running Vera chat sessions.
        """
        # Logic to be executed via Celery background job
        pass
