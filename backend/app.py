from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.search import router as search_router
from routes.auth import router as auth_router
from routes.history import router as history_router
from utils.logger import get_logger
from db import init_db

logger = get_logger(__name__)

app = FastAPI(title="VentureLens AI Startup Validator", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(history_router, prefix="/api", tags=["history"])

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def home():
    return {"message": "AI Startup Idea Validator API", "status": "running"}