# Backend Documentation

This document catalogs every functional file in the VentureLens backend.

## 1. Routes (`backend/api/`)

### `main.py` (or `app.py`)
- **Purpose**: Entry point for the FastAPI application.
- **Responsibilities**: Initializes routers, middleware (CORS), database engine, and application lifecycle events.
- **Dependencies**: `fastapi`, `uvicorn`, `sqlalchemy`.

### `routes/validation_routes.py`
- **Purpose**: Exposes the core startup validation endpoints.
- **Responsibilities**: Triggers the Orchestrator, manages `/api/analyze` (POST) for new ideas.

### `routes/history_routes.py`
- **Purpose**: User history management.
- **Responsibilities**: Exposes GET `/api/history` and `/api/history/{id}` to fetch past reports from SQLite.

### `routes/chat_routes.py`
- **Purpose**: Handles WebSocket connections for Vera Chat.
- **Responsibilities**: Upgrades HTTP to WS, routes messages to `VeraAgent`, handles streaming.

### `routes/export_routes.py`
- **Purpose**: Handles PDF/PPTX generation requests.
- **Responsibilities**: GET `/api/export/pdf` and `/api/export/ppt`. Calls `PDFExporter` and `PPTExporter`.

## 2. Core Orchestration (`backend/crew/`)

### `orchestrator.py`
- **Purpose**: The heart of the P2P mesh network.
- **Responsibilities**: Initializes agents, injects LLM client, runs the execution graph (Phase 1, Phase 2), applies guardrails, and merges outputs into a final JSON.
- **Dependencies**: `asyncio`, `Agent Contracts`, `GuardrailManager`.

## 3. Intelligence Agents (`backend/agents/`)

### `market_agent.py` & `customer_agent.py`
- **Purpose**: Phase 1 research extraction.
- **Responsibilities**: Extracts TAM/SAM/SOM, growth rates, customer personas, and pain points via structured LLM JSON outputs.

### `competitor_agent.py`
- **Purpose**: Competitive intelligence.
- **Responsibilities**: Identifies top competitors, calculates threat scores, positioning vectors, and moat scores.

### `swot_agent.py`
- **Purpose**: Strategic synthesis.
- **Responsibilities**: Generates a standard SWOT and an actionable TOWS matrix. Includes fallback mechanisms to prevent empty UI states.

### `mvp_agent.py` & `gtm_agent.py`
- **Purpose**: Execution planning.
- **Responsibilities**: Defines core features, phased roadmaps, CAC/LTV estimates, and 90-day action plans.

### `comparison_agent.py`
- **Purpose**: Executive Summary generation.
- **Responsibilities**: Creates the "Final Strategy" recommendation, biggest risk identification, and overall validation score.

### `vera_agent.py`
- **Purpose**: Interactive Co-Founder chat.
- **Responsibilities**: Maintains conversational context, utilizes RAG for context-injection, and streams Markdown text.

## 4. Contracts & Guardrails (`backend/contracts/` & `backend/guardrails/`)

### `agent_contracts.py` & `*_contract.py`
- **Purpose**: Pydantic models for data validation.
- **Responsibilities**: Ensures all LLM outputs strictly adhere to the expected schema before the frontend consumes them. Includes fields like `tows_matrix`, `overall_risk_level`, `action_plan`.

### `manager.py` (GuardrailManager)
- **Purpose**: Data sanitization.
- **Responsibilities**: Fallback injection, ensuring arrays are never null, and preventing UI crashes.

## 5. Services (`backend/services/`)

### `startup_scoring_service.py`
- **Purpose**: The VentureLens scoring engine.
- **Responsibilities**: Calculates the overall `77/100` score using a dynamic weighted average of Market, Customer, Competitor, Risk, MVP, and GTM scores based on the startup's category (e.g., DeepTech, SaaS).

### `pdf_exporter.py` & `ppt_exporter.py`
- **Purpose**: Report rendering.
- **Responsibilities**: Transforms the aggregated JSON payload into downloadable physical formats.

## 6. Database (`backend/database/`)

### `models.py`
- **Purpose**: SQLAlchemy ORM models.
- **Responsibilities**: Defines `User`, `Report`, and `ChatSession` tables.

### `session.py`
- **Purpose**: SQLite connection pooling.
- **Responsibilities**: Provides `get_db` dependency for FastAPI routes.
