# VentureLens — Development of AI Based Startup Idea Validator with Market Analysis Assistance

A production-ready, multi-agent AI system that validates startup ideas by performing live web research and synthesizing comprehensive market, competitor, and customer intelligence via a decentralized mesh network.

## Project Overview
VentureLens is an advanced AI-powered platform designed to provide founders, investors, and product managers with deep, data-driven insights into any startup idea. By leveraging a Multi-Agent System (MAS), it dynamically searches the web, analyzes the market size, evaluates customer pain points, and dissects competitors to generate a final Executive Strategy Report.

## Features Implemented
- **Decentralized Agent-to-Agent (A2A) Mesh Network**: Downstream agents execute in parallel, sharing a unified web research cache to optimize API usage and latency.
- **Query Strategist**: Dynamically converts abstract startup ideas into 6 targeted search queries.
- **Concurrent Web Search**: Harnesses `httpx.AsyncClient` and Tavily Search API for rapid, simultaneous deep-web extraction.
- **LLM Provider Agnostic**: Seamlessly switches between OpenRouter and Google Gemini via `pydantic-settings` configuration.
- **Robust Guardrails**: Real-time evaluation of LLM outputs using semantic matching, JSON schema enforcement, and `json-repair` to prevent hallucinations.
- **Server-Sent Events (SSE)**: Streams real-time validation progress logs directly to the frontend.
- **Executive-Ready UI**: A premium, responsive React dashboard utilizing Glassmorphism, Framer Motion animations, and data-rich visualization cards.

## Current Architecture
The system operates on a decentralized pipeline:
```text
User Input → FastAPI → Orchestrator
                            ├── WebSearchAgent (Tavily + Gemini/OpenRouter)
                            │     └── Executes deep web research & caches it
                            ├── MarketOpportunityAgent (Market Sizing & Trends)
                            ├── CustomerAgent (Personas & Pain Points)
                            ├── CompetitorAgent (Feature Gap Analysis)
                            └── ComparisonAgent (Master Synthesis Node)
                                  └── Dynamic Strategy, Feature Matrix → JSON response
```

## Tech Stack
| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, Vite, Tailwind CSS, Framer Motion, Recharts, React Router v7 |
| **Backend** | FastAPI, Python 3.12, Uvicorn, Pydantic, httpx |
| **LLM Integrations**| Google Gemini (via `google-genai`), OpenRouter |
| **Search Engine**| Tavily Search API, DuckDuckGo (Fallback) |

## Installation & Setup

### Prerequisites
- Node.js v18+
- Python 3.10+
- Tavily API key
- Google Gemini API key or OpenRouter API key

### 1. Configure Environment Variables
Create a `.env` file in the project root (or use the existing one):
```env
# Search Provider
TAVILY_API_KEY=your_tavily_key

# Google Gemini (Default)
LLM_PROVIDER=gemini
GOOGLE_AI_API_KEY=your_gemini_key
GOOGLE_MODEL=gemini-3.5-flash

# OpenRouter (Optional)
# OPENROUTER_API_KEY=your_openrouter_key
# OPENROUTER_MODEL=openai/gpt-oss-20b:free
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Backend runs at: `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`)

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://localhost:5173`

### 4. Running All Services Together
You can run both servers concurrently in separate terminal windows, or use a process manager like `concurrently` (if installed globally):
```bash
npx concurrently "cd backend && python -m uvicorn app:app --port 8000" "cd frontend && npm run dev"
```

## Folder Structure
```text
/
├── backend/
│   ├── agents/          # Individual AI agents (Market, Customer, Competitor, Comparison)
│   ├── core/            # Configuration and dependencies
│   ├── crew/            # Orchestrator for managing A2A mesh network
│   ├── guardrails/      # Output validation and hallucination prevention
│   ├── llm/             # Gemini and OpenRouter client adapters
│   ├── providers/       # LLM provider abstractions
│   ├── routes/          # FastAPI routers (Search, Progress, History)
│   ├── services/        # External services (Tavily Search)
│   ├── strategy/        # Query strategist for generating search intents
│   └── utils/           # Logging, error handling, SSE progress manager
├── frontend/
│   ├── public/          # Static assets
│   ├── src/
│   │   ├── components/  # Reusable React components & Dashboard Sections
│   │   ├── pages/       # Route pages (Home, Dashboard, Contact)
│   │   ├── services/    # API integration & SSE hooks
│   │   ├── styles/      # Tailwind & global CSS
│   │   └── App.jsx      # React Router configuration
├── docs/                # Comprehensive system and agent documentation
├── .env                 # Environment variables
└── README.md
```

## API Overview
- `GET /search?query={idea}`: Triggers the multi-agent pipeline. Returns the `X-Request-ID` header.
- `GET /api/progress/stream?request_id={id}`: SSE endpoint streaming real-time execution logs.
- `GET /api/history`: Retrieves previously validated startup ideas.

## Future Improvements
- Implement persistent database storage (PostgreSQL) for user histories.
- Expand web search capabilities with PDF/Document parsing.
- Introduce continuous real-time scraping via Headless Browsers.
- Add user authentication via OAuth2/JWT.

## Troubleshooting
- **Backend crashes with `ModuleNotFoundError`**: Ensure you are in the active virtual environment and have run `pip install -r requirements.txt`.
- **Progress bar gets stuck**: Verify that your browser permits SSE (Server-Sent Events) and that the backend is not throwing a CORS error. Ensure `X-Request-ID` is correctly generated on the frontend and passed in the headers.
- **LLM Timeouts / Rate Limits**: Increase the timeout settings in `.env` (e.g., `GEMINI_TIMEOUT=120`) and decrease `GEMINI_CONCURRENCY` to 1 if using a free tier API key.

## Contribution Guidelines
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.
