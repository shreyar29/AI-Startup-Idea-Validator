# Libraries & Dependencies

## Frontend (Node.js / React)

| Library | Version | Purpose |
|---------|---------|---------|
| **React** | 19.x | Core UI framework |
| **Vite** | 6.x | Development server and production bundler |
| **Tailwind CSS** | 3.x | Utility-first CSS framework for layout and styling |
| **Framer Motion** | Latest | Animation library — pipeline stage transitions, fade-ins |
| **Axios** | Latest | Promise-based HTTP client for backend API calls |
| **Lucide React** | Latest | SVG icon library (Search, Sparkles, Zap, ExternalLink, etc.) |
| **React Router DOM** | 6.x | Client-side routing (Home `/`, Validate `/validate`) |

### Fonts (Google Fonts)
| Font | Weights | Usage |
|------|---------|-------|
| **Outfit** | 300–800 | All headings (h1–h6) |
| **Inter** | 300–600 | Body text, UI labels |

---

## Backend (Python)

| Library | Purpose |
|---------|---------|
| **FastAPI** | REST API framework with automatic OpenAPI docs |
| **Uvicorn** | ASGI server for running FastAPI |
| **HTTPX** | Fully async HTTP client — used for both OpenRouter and Tavily API calls |
| **python-dotenv** | Loads `.env` file into environment variables at startup |
| **anyio** | Async concurrency layer required by HTTPX and FastAPI |
| **tavily-python** | Official Tavily SDK (kept as fallback; primary calls use httpx directly) |

### Key Python Standard Library Modules Used
| Module | Usage |
|--------|-------|
| `asyncio` | Concurrent execution of Tavily searches via `gather` + `Semaphore` |
| `logging` | Structured application logging across all modules |
| `os` | Environment variable access |
| `json` | Parsing LLM JSON responses |

---

## External APIs

| API | Provider | Usage |
|-----|----------|-------|
| **Tavily Search API** | [tavily.com](https://tavily.com) | AI-optimized deep web search — fetches competitors, market data, news |
| **OpenRouter Chat Completions** | [openrouter.ai](https://openrouter.ai) | Routes to LLM (default: `openai/gpt-oss-20b:free`) for query generation |
