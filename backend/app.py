from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import os
import uuid
import time
from typing import Callable

from routes.search import router as search_router
from routes.auth import router as auth_router
from routes.history import router as history_router
from utils.logger import get_logger
from db import init_db

logger = get_logger(__name__)

API_VERSION = "1.0.0"

app = FastAPI(
    title="VentureLens AI Startup Validator", 
    version=API_VERSION,
    description="Production-grade AI Multi-Agent Validator API"
)

# Configurable CORS instead of wildcard
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]

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

app.include_router(search_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(history_router, prefix="/api", tags=["history"])

@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting VentureLens API v{API_VERSION}...")
    init_db()
    logger.info("Database initialized successfully.")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down VentureLens API gracefully...")

@app.get("/")
def home():
    return {"message": "AI Startup Idea Validator API", "status": "running", "version": API_VERSION}

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "version": API_VERSION, "timestamp": time.time()}

@app.get("/ready", tags=["system"])
def readiness_check():
    # Placeholder for DB/Service readiness checks
    return {"status": "ready", "version": API_VERSION}

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