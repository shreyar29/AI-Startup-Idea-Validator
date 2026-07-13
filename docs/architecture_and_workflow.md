# Architecture & Workflow

This document details the system architecture and data pipeline of **VentureLens AI Startup Idea Validator** as currently implemented.

---

## System Architecture

The application follows **Clean Architecture** with a strict **Single Responsibility Principle** across agents, services, and processors.

```
┌──────────────────────────────────────────────┐
│               FRONTEND (React/Vite)           │
│  ValidateStartup.jsx → api.js → Axios POST   │
└─────────────────────┬────────────────────────┘
                      │ HTTP POST /search
┌─────────────────────▼────────────────────────┐
│              BACKEND (FastAPI)                │
│  routes/search.py → WebSearchAgent           │
│                          │                   │
│              ┌───────────▼──────────┐        │
│              │    QueryStrategist   │        │
│              │  (OpenRouter LLM)    │        │
│              │ Generates 6 queries  │        │
│              └───────────┬──────────┘        │
│                          │                   │
│              ┌───────────▼──────────┐        │
│              │  TavilySearchService │        │
│              │ (async httpx client) │        │
│              │ Concurrent execution │        │
│              └───────────┬──────────┘        │
│                          │                   │
│              ┌───────────▼──────────┐        │
│              │   ResultProcessor    │        │
│              │ Dedup + filter JSON  │        │
│              └───────────┬──────────┘        │
│                          │                   │
│              Structured JSON Response         │
└──────────────────────────────────────────────┘
```

---

## Component Responsibilities

### Frontend
| File | Responsibility |
|------|---------------|
| `ValidateStartup.jsx` | Main UI: textarea input, animated pipeline stages, results rendering |
| `api.js` | Axios POST to `/search`, structured error unwrapping |
| `Navbar.jsx` | Navigation (Home, Validate) |
| `Home.jsx` | Landing page with feature overview |
| `index.css` | Global styles: glassmorphism, gradients, Outfit/Inter fonts |

### Backend
| File | Responsibility |
|------|---------------|
| `app.py` | FastAPI entry point, CORS middleware, router registration |
| `routes/search.py` | `/search` POST endpoint — wires all dependencies and calls `WebSearchAgent.run()` |
| `agents/web_search_agent.py` | Orchestrator — calls QueryStrategist, TavilySearchService, ResultProcessor concurrently |
| `strategy/query_strategist.py` | Calls OpenRouter LLM with the query prompt to generate 6 search categories |
| `strategy/query_prompt.py` | System prompt instructing the LLM to output exactly 1 optimized query per category |
| `strategy/query_rules.py` | Input validation rules for startup idea text |
| `llm/openrouter_client.py` | Async HTTP client for OpenRouter chat completions API |
| `services/tavily_service.py` | Native async httpx client — fires all queries concurrently via `asyncio.gather` |
| `processors/result_processor.py` | URL deduplication, content filtering, final JSON structuring |
| `utils/logger.py` | Centralized logging configuration |
| `utils/text_sanitizer.py` | Strips non-ASCII characters from LLM query output |

---

## Data Flow (Step by Step)

### Step 1 — User Input
User types a startup idea into the multi-line textarea on the `/validate` page and clicks "Validate". The frontend displays animated pipeline stage indicators.

### Step 2 — HTTP POST
`api.js` sends `POST /search` with body `{ "idea": "<user text>" }` to the FastAPI backend on port `8001`.

### Step 3 — Query Strategy (LLM)
`QueryStrategist` sends the idea to OpenRouter using the system prompt from `query_prompt.py`. The LLM returns exactly **1 highly targeted search query** per category:
- `competitors`, `market_size`, `industry_trends`, `customer_pain_points`, `funding`, `recent_news`

### Step 4 — Concurrent Web Search
`TavilySearchService` opens a single `httpx.AsyncClient` session and fires all 6 category searches **simultaneously** using `asyncio.gather`. Each query POSTs directly to the Tavily Search API at `https://api.tavily.com/search`.

### Step 5 — Result Processing
`ResultProcessor` deduplicates results by URL across all categories and filters out entries with insufficient content length, producing a clean `search_results` dictionary.

### Step 6 — Structured JSON Response
The complete JSON payload is returned to the frontend containing:
- `identified_context` — LLM-detected product, industry, audience, technology
- `search_queries` — the 6 generated queries
- `search_results` — categorized, deduplicated web results
- `metadata` — status, agent name, timestamp, query counts

### Step 7 — Frontend Visualization
React components dynamically render the response:
- **Identified Context** card shows the LLM's understanding of the idea
- **Market Intelligence Report** renders per-category grids of search result cards with source hostnames, titles, and content snippets

---

## Performance Design

- **LLM Output**: Strictly 1 query per category = minimal token generation time
- **Search Concurrency**: All Tavily calls run in parallel (`asyncio.gather`) — no sequential waiting
- **Native Async HTTP**: `httpx.AsyncClient` used instead of thread-based wrappers — no thread pool exhaustion
- **Semaphore**: Concurrency limited to 10 simultaneous requests to avoid rate limiting
