from fastapi import FastAPI, Request, Response

try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from core.rate_limiter import limiter
    HAS_SLOWAPI = True
except ImportError:
    HAS_SLOWAPI = False

from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import os
import uuid
import time
from typing import Callable
from contextlib import asynccontextmanager

from core.config import settings
from core.container import container

# Core Mesh Routers (Always available)
from routes.search import router as search_router
from routes.progress import router as progress_router

# Enterprise Architecture Routers (Optional)
try:
    from api.auth_routes import router as auth_router
    from api.chat_routes import router as chat_router
    from api.report_routes import router as report_router
    from api.export_routes import router as export_router
    from api.dashboard_routes import router as dashboard_router
    from api.workspace_routes import router as workspace_router
    from api.metrics_routes import router as metrics_router
    HAS_ENTERPRISE_API = True
except ImportError as e:
    HAS_ENTERPRISE_API = False
from utils.logger import get_logger
from db import init_db

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
    
    # Start ProgressManager cleanup task
    from utils.progress import ProgressManager
    async def cleanup_task():
        while True:
            try:
                await asyncio.sleep(3600)
                await ProgressManager.cleanup_stale_sessions()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.exception(f"Error in cleanup task: {str(e)}")
            
    cleaner = asyncio.create_task(cleanup_task())
    
    yield
    
    # Shutdown actions
    cleaner.cancel()
    try:
        await cleaner
    except asyncio.CancelledError:
        pass
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

# Properly register SlowAPI limiter if available
if HAS_SLOWAPI:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Configurable CORS instead of wildcard
ALLOWED_ORIGINS = settings.app.allowed_origins_list
is_development = os.environ.get("ENVIRONMENT", "").lower() == "development"

if not ALLOWED_ORIGINS:
    if is_development:
        ALLOWED_ORIGINS = ["*"]
    else:
        raise RuntimeError("CORS allowed_origins must be configured in production.")
elif "*" in ALLOWED_ORIGINS and not is_development:
    raise RuntimeError("Wildcard CORS ('*') is not permitted in production.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        start_time = time.perf_counter()
        
        logger.info(f"Request started: {request.method} {request.url.path} (ID: {request_id})")
        
        try:
            # Bypass timeout for streaming endpoints
            if request.url.path.startswith(("/api/logs/stream", "/api/progress")):
                response = await call_next(request)
            else:
                timeout_seconds = getattr(settings.app, 'REQUEST_TIMEOUT', 120)
                response = await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
                
            process_time = time.perf_counter() - start_time
            
            # Inject correlation IDs and metrics
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Security Headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            
            x_forwarded_proto = request.headers.get("x-forwarded-proto", "").lower().split(",")
            is_https = request.url.scheme == "https" or any(proto.strip() == "https" for proto in x_forwarded_proto)
            
            if is_https:
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Swagger UI needs to load assets from jsdelivr
            if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
                response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
                
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s (ID: {request_id})")
            return response
        except asyncio.TimeoutError:
            process_time = time.perf_counter() - start_time
            logger.error(f"Request timeout: {request.method} {request.url.path} - Time: {process_time:.4f}s (ID: {request_id})")
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Gateway Timeout",
                    "message": "The server took too long to process the request.",
                    "request_id": request_id
                }
            )
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.exception(f"Request failed: {request.method} {request.url.path} - Time: {process_time:.4f}s (ID: {request_id})")
            raise

app.add_middleware(RequestTrackingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"Unhandled Exception for Request ID {request_id}")
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

if HAS_ENTERPRISE_API:
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(chat_router) # prefix is defined in the router itself
    app.include_router(report_router)
    app.include_router(export_router)
    app.include_router(dashboard_router)
    app.include_router(workspace_router)
    app.include_router(metrics_router)



# Root handler removed, handled by SPA fallback

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
        
        from database.database import check_db_health
        db_healthy = await check_db_health()
        if not db_healthy:
            dependencies_healthy = False
            logger.warning("Database readiness check failed. Service is unavailable.")
                
        # Check active session count for metrics
        # Chat sessions are now managed via PostgreSQL memory
        active_sessions = 0 # Consider replacing with a quick count query if needed
        logger.debug(f"Active sessions: {active_sessions}")
        
    except Exception as e:
        logger.warning(f"Readiness check failed: {str(e)}")
        dependencies_healthy = False

    if dependencies_healthy:
        return {"status": "ready", "version": API_VERSION}
    
    response.status_code = 503
    return {"status": "unavailable", "version": API_VERSION}

from auth.jwt_manager import JWTManager
from fastapi import Depends, HTTPException

async def verify_admin_sse(request: Request):
    token = request.query_params.get("token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required for log streaming")
        
    payload = JWTManager.decode_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required for log streaming")
    return payload

@app.get("/api/logs/stream")
async def stream_logs(request: Request, admin_user: dict = Depends(verify_admin_sse)):
    # Production deployments must protect this endpoint or disable it
    is_development = os.environ.get("ENVIRONMENT", "").lower() == "development"
    if not is_development:
        raise HTTPException(status_code=403, detail="Log streaming is disabled in production")

        
    async def log_generator():
        log_file = "validation.log"
        
        def touch_file():
            if not os.path.exists(log_file):
                open(log_file, 'a').close()
                
        await asyncio.to_thread(touch_file)
            
        f = await asyncio.to_thread(open, log_file, "r", encoding="utf-8")
        try:
            await asyncio.to_thread(f.seek, 0, 2) # go to end
            while True:
                if await request.is_disconnected():
                    break
                lines = await asyncio.to_thread(f.readlines)
                if not lines:
                    await asyncio.sleep(0.5)
                    continue
                # Ensure no newlines break SSE format
                for line in lines:
                    yield f"data: {line.strip()}\n\n"
        finally:
            await asyncio.to_thread(f.close)

    return StreamingResponse(log_generator(), media_type="text/event-stream")

# --- Static File Serving for SPA (React/Vite) ---
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")
        
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        
        return JSONResponse(status_code=404, content={"message": "Frontend build not found."})
else:
    logger.warning("Frontend dist directory not found. API only mode.")

