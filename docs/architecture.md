# Central Architecture Directory

Welcome to the VentureLens engineering documentation hub. This directory maps out the specific architectural implementations of the platform.

## Architecture Documents

- 🎨 **[Frontend Architecture](frontend.md)**: React, Vite, Framer Motion, and Context API details.
- ⚡ **[Backend Architecture](backend.md)**: FastAPI, AsyncIO, SQLAlchemy, and API routing.
- 🕸️ **[Agent Mesh Architecture](agents.md)**: The 10 specialized LLM agents and Orchestrator logic.
- 🧠 **[RAG Pipeline Architecture](rag.md)**: Qdrant, WebSockets, and the Vera AI context pipeline.
- 🛡️ **[Guardrails Architecture](guardrails.md)**: Pydantic validation and hallucination prevention.
- 📊 **[Workspace & Exports](workspace.md)**: UI visualization, PDF (fpdf2), and PPTX generation.
- 🚀 **[Deployment Guide](deployment.md)**: Cloud-agnostic deployment configurations.

## The VentureLens Repository Map

For engineers navigating the codebase, here is the primary responsibility map:

- `backend/app.py`: The ASGI entry point. Initializes routes and database schemas.
- `backend/crew/orchestrator.py`: The nerve center. Executes the concurrent `asyncio` mesh logic.
- `backend/agents/`: Directory containing individual prompt/persona logic (e.g., `market_agent.py`).
- `backend/contracts/`: Defines the strict data shapes required by the frontend using Pydantic.
- `backend/rag/`: Logic for chunking JSON reports and querying the in-memory Qdrant instance.
- `backend/export/`: Python scripts to natively generate `.pdf` and `.pptx` binary blobs.
- `frontend/src/pages/`: Main route views (Dashboard, Workspace, VeraChat).
- `frontend/src/contexts/`: React Contexts preventing prop-drilling of massive JSON states.
