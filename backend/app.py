from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import os
import uuid
import time
from typing import Callable
from contextlib import asynccontextmanager

from core.config import settings
from core.container import container

from routes.search import router as search_router
from routes.auth import router as auth_router
from routes.history import router as history_router
from routes.progress import router as progress_router
from utils.logger import get_logger
from db import init_db

# Placeholder for centralized configuration integration
# from core.config import settings

logger = get_logger(__name__)

API_VERSION = "1.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(f"Starting VentureLens API v{API_VERSION}...")
    
    # Fail fast: Validate critical dependencies at startup
    try:
        provider = container.get_llm_provider()
        is_healthy = await provider.health_check()
        if not is_healthy:
            raise RuntimeError("LLM provider readiness verification failed.")
        logger.info(f"Successfully validated LLM provider: {settings.llm.LLM_PROVIDER}")
    except Exception as e:
        logger.error(f"Startup configuration validation failed: {str(e)}")
        raise RuntimeError(f"Startup validation failed: {str(e)}") from e

    init_db()
    logger.info("Database initialized successfully.")
    
    # Start ProgressManager cleanup task
    from utils.progress import ProgressManager
    async def cleanup_task():
        while True:
            await asyncio.sleep(3600)
            await ProgressManager.cleanup_stale_sessions()
            
    cleaner = asyncio.create_task(cleanup_task())
    
    yield
    
    # Shutdown actions
    cleaner.cancel()
    logger.info("Shutting down VentureLens API gracefully...")
    await container.shutdown()

app = FastAPI(
    title="VentureLens AI Startup Validator", 
    version=API_VERSION,
    description="Production-grade AI Multi-Agent Validator API. Provides robust multi-agent startup validation capabilities.",
    contact={
        "name": "VentureLens Support",
        "url": "https://venturelens.ai/support",
        "email": "support@venturelens.ai",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=[
        {"name": "system", "description": "System health and status endpoints."},
        {"name": "auth", "description": "Authentication and authorization."},
        {"name": "history", "description": "User validation history."},
    ],
    lifespan=lifespan
)

# Configurable CORS instead of wildcard
ALLOWED_ORIGINS = settings.app.allowed_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.time()
        
        logger.info(f"Request started: {request.method} {request.url.path} (ID: {request_id})")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Inject correlation IDs and metrics
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Security Headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Swagger UI needs to load assets from jsdelivr
            if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
                response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
                
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s (ID: {request_id})")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.exception(f"Request failed: {request.method} {request.url.path} - Time: {process_time:.4f}s (ID: {request_id})")
            raise

app.add_middleware(RequestTrackingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled Exception for Request ID {request_id}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request_id
        }
    )

app.include_router(search_router, tags=["search"])
app.include_router(progress_router, prefix="/api", tags=["progress"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(history_router, prefix="/api", tags=["history"])



@app.get("/")
def home():
    return {"message": "AI Startup Idea Validator API", "status": "running", "version": API_VERSION}

@app.get("/health", tags=["system"])
def health_check():
    # Core health check for liveness probes
    return {"status": "ok", "version": API_VERSION, "timestamp": time.time()}

@app.get("/ready", tags=["system"])
async def readiness_check(response: Response):
    # Enhanced readiness check prepared for dependency validation (DB, Cache, external APIs)
    try:
        llm_provider = container.get_llm_provider()
        dependencies_healthy = await llm_provider.health_check()
    except Exception as e:
        logger.warning(f"Readiness check failed: {str(e)}")
        dependencies_healthy = False
    
    if dependencies_healthy:
        return {"status": "ready", "version": API_VERSION}
    
    response.status_code = 503
    return {"status": "unavailable", "version": API_VERSION}

@app.get("/api/logs/stream")
async def stream_logs(request: Request):
    async def log_generator():
        log_file = "validation.log"
        if not os.path.exists(log_file):
            open(log_file, 'a').close()
            
        with open(log_file, "r", encoding="utf-8") as f:
            f.seek(0, 2) # go to end
            while True:
                if await request.is_disconnected():
                    break
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue
                # Ensure no newlines break SSE format
                yield f"data: {line.strip()}\n\n"

    return StreamingResponse(log_generator(), media_type="text/event-stream")

# Trigger reload