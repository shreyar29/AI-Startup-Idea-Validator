# Setup & Execution Guide

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Node.js | v18+ |
| Python | 3.10+ |
| Tavily API Key | [tavily.com](https://tavily.com) |
| OpenRouter API Key | [openrouter.ai](https://openrouter.ai) |

---

## Environment Variables

The project requires a `.env` file in the project root containing:

```env
TAVILY_API_KEY=your_tavily_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-oss-20b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

> **Note:** The `OPENROUTER_MODEL` can be changed to any free model on OpenRouter (e.g., `google/gemma-7b-it:free`) to reduce LLM latency.

---

## Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Install all dependencies
pip install -r requirements.txt

# Start the FastAPI server with hot-reload
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

The backend API will be available at: **http://127.0.0.1:8001**

To verify it's running, visit: http://127.0.0.1:8001/ — it should return:
```json
{"message": "AI Startup Idea Validator API", "status": "running"}
```

---

## Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend application will be available at: **http://localhost:5175**

---

## API Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search` | Accepts `{ "idea": "..." }` and returns structured market intelligence JSON |

### Example Request
```bash
curl -X POST http://127.0.0.1:8001/search \
  -H "Content-Type: application/json" \
  -d '{"idea": "AI-powered platform for detecting skin diseases using smartphone camera"}'
```

### Example Response Shape
```json
{
  "metadata": { "status": "success", "agent": "WebSearchAgent", ... },
  "identified_context": { "product": "...", "industry": "...", ... },
  "search_queries": { "competitors": [...], "market_size": [...], ... },
  "search_results": { "competitors": [...], "market_size": [...], ... }
}
```
