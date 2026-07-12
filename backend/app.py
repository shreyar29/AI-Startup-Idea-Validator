from fastapi import FastAPI
from agents.web_search_agent import search_startup

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Startup Idea Validator API"}

@app.get("/search")
def search(query: str):
    return search_startup(query)