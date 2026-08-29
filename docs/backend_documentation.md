# Backend Documentation

## 1. Architecture Overview
The backend is built with FastAPI and runs on Uvicorn. It follows a decentralized Multi-Agent System (MAS) architecture using an Agent-to-Agent (A2A) mesh network. The core orchestrator handles incoming validation requests, initiates the web search task, and triggers multiple peer agents in parallel.

## 2. API Endpoints
- **`GET /search`**: Main entrypoint for validation. Requires a `query` parameter (the startup idea). Returns a full JSON analysis.
- **`GET /api/progress/stream`**: Server-Sent Events (SSE) endpoint. Expects a `request_id` to subscribe to real-time execution logs.
- **`GET /api/history`**: Placeholder endpoint for retrieving past analysis.

## 3. Agent Orchestration
- **StartupValidatorOrchestrator (`crew/orchestrator.py`)**: The central hub that receives requests and manages the mesh network.
- **P2P Mesh Network**: Instead of running sequentially, all intelligence agents (Market, Customer, Competitor) are initialized in parallel. They await the shared Web Search Agent's output (via `asyncio.Future`) and then execute their respective LLM chains concurrently. The `ComparisonAgent` awaits the output of all other agents.

## 4. Services
- **Tavily Service (`services/tavily_service.py`)**: Handles concurrent API requests to Tavily Search. Falls back to DuckDuckGo if limits are hit.
- **LLM Providers (`llm/`, `providers/`)**: Uses an adapter pattern (`BaseLLMProvider`) to support both Google Gemini (`gemini_client.py`) and OpenRouter (`openrouter_client.py`).

## 5. Guardrails & Validation
- **`guardrails/manager.py`**: Validates LLM output against Pydantic schemas. Prevents hallucinations by strictly verifying numeric outputs and claims against the web search source texts.
- **`json-repair`**: Automatically intercepts and repairs malformed JSON strings returned by LLMs before parsing.

## 6. Utilities
- **Progress Manager (`utils/progress.py`)**: Uses Python `asyncio.Queue` and thread-safe sessions to track and yield SSE events to the frontend.
- **Error Handler (`utils/error_handler.py`)**: Custom decorators providing exponential backoff for transient HTTP errors (e.g., rate limits).
- **Logger (`utils/logger.py`)**: Configured via `rich` to output readable terminal logs with timestamps and log levels.

## 7. Configuration & Environment Setup
Uses `pydantic-settings` to load the `.env` file dynamically.
Key configurations (in `core/config.py`):
- `LLM_PROVIDER`: Determines which AI to use (e.g., `gemini` or `openrouter`).
- Concurrency controls (`GEMINI_CONCURRENCY`) and Timeouts (`MARKET_LLM_TIMEOUT`).

## 8. Deployment
The backend can be containerized using Docker, or deployed on any standard ASGI server (e.g., Uvicorn via Gunicorn or systemd). It expects stateless execution, with SSE sessions held in memory for the duration of the request.
