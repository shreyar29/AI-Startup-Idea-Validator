# VentureLens — AI Startup Idea Validator

A production-ready, multi-agent AI system that validates startup ideas by performing live, categorized web research and returning structured market intelligence.

## Quick Start

### Prerequisites
- Node.js v18+
- Python 3.10+
- Tavily API key
- OpenRouter API key

### 1. Configure Environment Variables
Create a `.env` file in the project root (or use the existing one):
```env
TAVILY_API_KEY=your_tavily_key
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openai/gpt-oss-20b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```
Backend runs at: `http://127.0.0.1:8001`

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://localhost:5175`

## Architecture

```
User Input → FastAPI → WebSearchAgent
                           ├── QueryStrategist (OpenRouter LLM)
                           │     └── Generates 6 categorized queries
                           ├── TavilySearchService (concurrent async HTTP)
                           │     └── Executes all queries simultaneously
                           └── ResultProcessor
                                 └── Deduplication, filtering → JSON response
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.10+, Uvicorn |
| LLM | OpenRouter (gpt-oss-20b:free) |
| Search | Tavily Search API (async httpx) |
| Styling | Outfit + Inter fonts, Glassmorphism UI |