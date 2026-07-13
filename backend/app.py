from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.search import router as search_router
from utils.logger import get_logger

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

@app.get("/")
def home():
    return {"message": "AI Startup Idea Validator API", "status": "running"}