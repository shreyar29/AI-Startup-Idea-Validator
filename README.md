# VentureLens — AI Startup Idea Validator

A production-ready, multi-agent AI system that validates startup ideas by performing live web research and synthesizing comprehensive market, competitor, and customer intelligence via a decentralized mesh network.

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

### Milestone 1: Core Web Search Pipeline

```text
User Input → FastAPI → WebSearchAgent
                           ├── QueryStrategist (OpenRouter LLM)
                           │     └── Generates 6 categorized queries
                           ├── TavilySearchService (concurrent async HTTP)
                           │     └── Executes all queries simultaneously
                           └── ResultProcessor
                                 └── Deduplication, filtering → JSON response
```

### Milestone 1 Features
- **Query Strategist**: Converts abstract startup ideas into 6 highly targeted, category-specific search queries using an LLM.
- **Concurrent Web Search**: Uses `httpx.AsyncClient` to simultaneously search the web across all categories via the Tavily Search API.
- **Result Processor**: Deduplicates URL sources and structurally filters incoming search data for high-quality market intelligence.

### Milestone 2: Decentralized P2P Mesh Network & Analysis Synthesis

VentureLens was upgraded to use a **Decentralized Agent-to-Agent (A2A) Mesh Network** for rapid, parallelized startup validation and analysis.

```text
User Input → FastAPI → Orchestrator
                            ├── WebSearchAgent (Tavily + OpenRouter)
                            │     └── Caches deep web research for downstream peers
                            ├── MarketOpportunityAgent (Market Sizing & Trends)
                            ├── CustomerAgent (Personas & Pain Points)
                            ├── CompetitorAgent (Feature Gap Analysis)
                            └── ComparisonAgent (Master Synthesis Node)
                                  └── Dynamic Scoring, Feature Matrix → JSON response
```

### Milestone 2 Features
- **Concurrent Mesh Execution**: Downstream agents (Market, Customer, Competitor) run concurrently and hook into a single cached web search task, bypassing redundant API calls.
- **Resilient LLM Inference**: Fully protected by `json-repair` and strict schema unpacking to automatically fix LLM hallucinations without crashing.
- **Exponential Backoff Engine**: HTTP client transparently intercepts and retries `429 Too Many Requests` limits caused by high-concurrency execution.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS, Framer Motion, Recharts |
| Backend | FastAPI, Python 3.10+, Uvicorn, SQLite |
| LLM | OpenRouter (Multiple models supported) |
| Search | Tavily Search API (async httpx) |
| Styling | Outfit + Inter fonts, Glassmorphism UI |

## API Documentation
The API is automatically documented via OpenAPI (Swagger). Once the backend is running, navigate to `http://localhost:8000/docs` to view the interactive API playground, schemas, and endpoints.

## User Guide
1. Create an account or log in via the interactive Authentication screen.
2. Navigate to the **Validate** page from the top navigation bar.
3. Describe your startup idea in plain English (or select a sample idea to autofill).
4. Select your industry from the dropdown (optional).
5. Click **Validate**. 
6. Wait for the A2A mesh network to compile the research. Use the sticky **Quick Nav** sidebar to quickly jump between the Market, Customer, Competitor, and Feature Matrix sections of the generated report.

## Developer Guide
### Adding New Agents
To add a new agent to the mesh:
1. Create a new file in `backend/agents/`.
2. Define the agent class and accept `shared_context` in the `__init__`.
3. Implement `get_analysis()` to await the `WebSearchAgent` and execute your unique LLM parsing logic.
4. Instantiate the agent in `orchestrator.py`, add it to the `peers` dictionary, and call `.connect_peers()`.

### Editing the UI
The frontend uses standard React functional components. All styling is managed via Tailwind utility classes. The `api.js` file handles all outbound requests with an automated exponential backoff interceptor for transient network failures.