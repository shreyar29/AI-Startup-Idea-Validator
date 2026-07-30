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
- **Semaphore**: Concurrency limited to 10 simultaneous requests to avoid rate limiting

---

## Milestone 2 — Decentralized P2P Mesh Network & Analysis Synthesis

Following the completion of the Web Search Agent in Milestone 1, the architecture was fundamentally upgraded in **Milestone 2**. The centralized, fragile `CrewAI` orchestration was completely removed and replaced with a highly performant, custom **Decentralized Agent-to-Agent (A2A) Mesh Network**.

### Architectural & Workflow Updates
1. **Decentralized Orchestration**: Agents now operate as autonomous nodes in a mesh network, sharing a central `context` dictionary.
2. **Concurrent & Sequential Execution Modes**: Downstream analysis agents (Market, Customer, Competitor) hook into a single cached `asyncio.Task` executed by the Web Search Agent, completely eliminating redundant web searches and minimizing Tavily API calls.
3. **Exponential Backoff Engine**: Implemented directly in the HTTP client to intercept `HTTP 429 Too Many Requests` API rate limits caused by concurrent mesh execution.
4. **Indestructible JSON Parsing**: Integrated the heuristic `json-repair` library into the parsing utility to automatically intercept, repair, and unpack malformed LLM hallucinations (missing commas, unescaped quotes, stray arrays) on the fly without crashing the pipeline.
5. **Context Window Optimization**: Raw search snippets are aggressively truncated (e.g., `[:3000]` characters) before LLM injection, vastly improving generation speed (Time-To-First-Token) and reducing token costs.

### New Component Responsibilities (Milestone 2)

| File | Responsibility |
|------|---------------|
| `backend/crew/orchestrator.py` | The entry point for the mesh network. Initializes the agents, maps their peer connections, and triggers the final synthesis node. Replaced legacy CrewAI logic. |
| `backend/agents/market_agent.py` | Synthesizes web snippets to extract market size, growth rate (CAGR), maturity, and distinct trends. |
| `backend/agents/customer_agent.py` | Generates realistic user personas, identifies pain points, uncovers unmet needs, and calculates an overall sentiment score based on research data. |
| `backend/agents/competitor_agent.py` | Discovers actual real-world competitors, actively filtering out generic placeholders (`Unknown`, `N/A`). Extracts features, pricing, strengths/weaknesses, and performs a mathematical feature gap analysis. |
| `backend/agents/comparison_agent.py` | The master synthesis node. Compiles Market, Customer, and Competitor insights into a massive `context_payload` to dynamically calculate `validation_score`, `innovation_score`, and generate a verified `feature_matrix` array. |
| `backend/llm/openrouter_client.py` | Upgraded to include an intelligent Exponential Backoff Engine with randomized jitter to transparently handle concurrency rate limits (HTTP 429). |
| `backend/utils/error_handler.py` | Upgraded `safe_parse_llm_json` to utilize `json-repair`, automatically fixing structural LLM syntax errors, and seamlessly unpacking single-element arrays into JSON objects. |
| `backend/utils/logger.py` | Replaced verbose console spam with configurable, structured, and timestamped logging. |

### Milestone 2 Data Flow (Synthesis Pipeline)

1. **Orchestrator Trigger**: The `StartupValidatorOrchestrator` initializes all nodes and commands the `ComparisonAgent` to generate its report.
2. **Peer Task Resolution**: The `ComparisonAgent` demands upstream data from the Market, Customer, and Competitor peers.
3. **Web Search Task Caching**: The Market, Customer, and Competitor peers simultaneously demand web data from the `WebSearchAgent`. The search is executed exactly **once**, and the payload is distributed from memory to all three nodes.
4. **Resilient LLM Inference**: The three analysis agents process the truncated `[:3000]` snippets. If the LLM generates broken JSON, `json-repair` fixes it. If it fails entirely, the 3-attempt retry loop catches the `MalformedLLMOutputError`.
5. **Final Aggregation**: The `ComparisonAgent` cross-references all verified outputs into a comprehensive matrix and computes the final startup recommendation scores, returning 100% schema-compliant JSON to the frontend.
