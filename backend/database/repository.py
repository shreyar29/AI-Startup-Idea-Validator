from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import TypeVar, Generic, Type, Optional, List
from .models import Base, User, Report, ChatSession, ChatMessage, TelemetryLog

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)
        
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

class ReportRepository(BaseRepository[Report]):
    def __init__(self):
        super().__init__(Report)
        
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[Report]:
        result = await db.execute(select(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()))
        return result.scalars().all()

class ChatSessionRepository(BaseRepository[ChatSession]):
    def __init__(self):
        super().__init__(ChatSession)

class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self):
        super().__init__(ChatMessage)

class TelemetryRepository(BaseRepository[TelemetryLog]):
    def __init__(self):
        super().__init__(TelemetryLog)

# Singleton instances
user_repo = UserRepository()
report_repo = ReportRepository()
chat_session_repo = ChatSessionRepository()
chat_message_repo = ChatMessageRepository()
telemetry_repo = TelemetryRepository()
