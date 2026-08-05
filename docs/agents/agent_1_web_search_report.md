# Web Search Agent (including Query Strategist)

## 1. Purpose & Responsibilities
The Web Search Agent is the foundational data-gathering unit of the VentureLens MAS. Its primary responsibility is to autonomously translate an abstract startup idea into highly targeted search queries, execute those queries concurrently across the deep web, and process the results into a deduplicated, cached knowledge base for downstream agents.

## 2. Inputs & Outputs
- **Inputs**: 
  - `query` (str): The raw startup idea provided by the user (e.g., "AI-powered CRM for plumbers").
- **Outputs**: 
  - `Dict[str, Any]`: A structured JSON dictionary containing deduplicated search results categorized by "Market", "Competitors", and "Customers", along with URL references.

## 3. Internal Workflow & Decision-Making Process
1. **Strategy Generation**: The agent passes the user's idea to the **Query Strategist** (an LLM-powered module). The Strategist outputs 6 optimized search intents mapped to predefined categories.
2. **Concurrent Search**: The agent feeds the 6 queries into the **Tavily Service**, utilizing `httpx.AsyncClient` to perform the searches in parallel.
3. **Deduplication**: Resulting URLs and snippets are processed to remove redundant links and prioritize high-quality domains.
4. **Caching**: The finalized JSON payload is resolved via an `asyncio.Future` (`shared_context["search_data"]`), instantly unblocking downstream peer agents.

## 4. Models & Tools Used
- **LLM**: Gemini or OpenRouter (depending on config) for generating the query strategy.
- **Search Engine**: Tavily Search API (primary) and DuckDuckGo (fallback).

## 5. Backend & Frontend Integration
- **Backend Flow**: Initialized first in the orchestrator. Its output is the absolute dependency for all other agents.
- **Frontend Flow**: Rendered in the dashboard under the "Research Evidence" section (via `WebSearchSection.jsx`), which displays the exact URLs and evidence the AI used.

## 6. Error Handling
If the LLM fails to generate queries, it falls back to hardcoded default queries based on the raw input. If Tavily fails due to rate limits, exponential backoff is triggered, followed by a fallback to `ddgs`.

## 7. Future Improvements
- Integrate specialized academic/research API endpoints (e.g., ArXiv, PubMed) for deep-tech startup ideas.
