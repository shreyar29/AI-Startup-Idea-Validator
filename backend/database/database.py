from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings
from sqlalchemy import text
from utils.logger import get_logger

logger = get_logger(__name__)

DATABASE_URL = settings.app.DATABASE_URL
is_postgres = DATABASE_URL.startswith("postgresql")

engine_kwargs = {
    "echo": False,
    "future": True,
}

if is_postgres:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20,
    })
else:
    # SQLite compatibility
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False}
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def init_db():
    """Create all tables in the database if they don't exist."""
    try:
        from database.models import User, SearchHistory, StartupScorecard  # Ensure models are imported
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {str(e)}")

async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Database dependency failure: Session creation or transaction failed. (Error: {type(e).__name__})")
        raise

async def check_db_health() -> bool:
    """
    Executes a lightweight query to verify database connectivity.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed due to connectivity issue. (Error: {type(e).__name__})")
        return False
