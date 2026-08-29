# Backend Documentation

## Entry Point

**`app.py`** — FastAPI application entry point.
- Creates the `FastAPI` instance titled `"VentureLens AI Startup Validator"`
- Registers CORS middleware (allows all origins — suitable for development)
- Registers the search router from `routes/search.py`
- Exposes `GET /` health check endpoint

---

## API Routes

### `routes/search.py`

**Endpoint:** `POST /search`

**Request Body:**
```json
{ "idea": "string (1–2000 chars, required)" }
```

**Behavior:**
1. Validates the request body via Pydantic
2. Instantiates `OpenRouterClient`, `TavilySearchService`, `QueryStrategist`, `ResultProcessor`
3. Creates `WebSearchAgent` with all injected dependencies
4. Calls `agent.run(idea)` and returns the structured result

**Response:** See architecture doc for full JSON shape.

---

## Agents

### `agents/web_search_agent.py` — `WebSearchAgent`

The **orchestrator**. Takes a startup idea string and coordinates the full pipeline:
1. Calls `QueryStrategist.generate_search_queries(idea)` — awaits LLM response
2. Sanitizes query output via `utils/text_sanitizer.py`
3. Dispatches all categories concurrently using `asyncio.gather` and `TavilySearchService.search()`
4. Passes raw results to `ResultProcessor.process()`
5. Returns the final structured dictionary

---

## Strategy

### `strategy/query_strategist.py` — `QueryStrategist`

Calls the OpenRouter LLM to convert a startup idea into structured search queries.

- Injects `OpenRouterClient`
- Validates input idea via `query_rules.py`
- Sends `SYSTEM_PROMPT` + user idea to `client.generate_response()`
- Parses the returned JSON string into a Python dict

### `strategy/query_prompt.py` — `SYSTEM_PROMPT`

Contains the complete LLM system prompt. Key contract:
- Role: "Query Strategist" — generates queries ONLY, never analyzes
- Output: Exactly **1 query per category** (competitors, market_size, industry_trends, customer_pain_points, funding, recent_news, optional regulations)
- Format: Strict RFC8259 JSON — no markdown, no extra tokens

### `strategy/query_rules.py`

Input validation rules:
- Minimum/maximum character length
- Sanitization of control characters

---

## Services

### `services/tavily_service.py` — `TavilySearchService`

Executes web searches against the Tavily API using **native async HTTP**.

- Uses `httpx.AsyncClient` — no thread pool, no blocking
- All queries for a single request run **concurrently** via `asyncio.gather`
- `asyncio.Semaphore(10)` prevents more than 10 simultaneous requests
- POST body: `{ "api_key": ..., "query": ... }` → `https://api.tavily.com/search`
- Each failed query logs an error and returns `[]` (graceful degradation)

---

## Processors

### `processors/result_processor.py` — `ResultProcessor`

Cleans and structures the raw Tavily search results:
- **URL deduplication**: Tracks seen URLs across all categories; skips duplicates
- **Content filtering**: Skips results with insufficient content length
- Returns a clean `{ category: [result, ...] }` dictionary

---

## LLM Client

### `llm/openrouter_client.py` — `OpenRouterClient`

Async HTTPX client for the OpenRouter chat completions API.

- Configuration via environment variables: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`
- Method: `async generate_response(system_prompt, user_prompt)` → `str`
- Custom exception types: `OpenRouterAuthError`, `OpenRouterTimeoutError`, `OpenRouterNetworkError`, `OpenRouterAPIError`

---

## Utilities

### `utils/logger.py`
Returns a configured `logging.Logger` instance for any module. Replaces `print()` throughout to prevent Unicode encoding errors on Windows.

### `utils/text_sanitizer.py`
Strips non-ASCII/non-printable characters from LLM-generated query strings before passing them to Tavily.
