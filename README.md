<div align="center">
  <img src="https://img.icons8.com/3d-fluency/94/startup.png" alt="Startup Icon"/>
  <h1>🚀 VentureLens</h1>
  <p><b>The Ultimate AI-Powered Startup Intelligence & Due-Diligence Engine</b></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react&logoColor=black)](#)
  [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](#)
  [![AI Agents](https://img.shields.io/badge/Architecture-P2P%20Agent%20Mesh-8A2BE2)](#)
</div>

<br/>

VentureLens transforms raw, napkin-sketch startup ideas into **comprehensive, investor-ready due-diligence reports** in seconds. Powered by a decentralized network of specialized AI agents, it doesn't just guess—it researches, analyzes, and strategizes.

Instead of generic ChatGPT advice, VentureLens executes real-time web searches, extracts structured market data, and orchestrates **8 specialized AI agents** (Market, Customer, Competitor, Risk, etc.) to evaluate your business model ruthlessly.

---

## ✨ Why VentureLens?

- **🕸️ P2P Agent Mesh Architecture**: 8 specialized AI agents work in parallel to analyze your idea from every angle. No monolithic bottlenecks.
- **🔎 Evidence-Backed Intelligence**: Integrates with Tavily to scrape real-time market data. All insights are grounded in reality—*zero hallucinations*.
- **🧮 Dynamic Scoring Engine**: Calculates a holistic `0-100` viability score weighted dynamically based on your industry (e.g., DeepTech vs B2B SaaS).
- **🤖 Vera: Your AI Co-Founder**: An interactive chat interface powered by a custom **RAG (Retrieval-Augmented Generation)** pipeline. Interrogate your generated report in real-time!
- **📊 Export to PDF & PPTX**: Instantly generate professional pitch decks and executive summaries for investors.
- **🎨 Premium UI/UX**: Built with React, TailwindCSS, Recharts, and Framer Motion for a stunning, glassmorphic dark-mode experience.

---

## 🏗 System Architecture

VentureLens operates on a decoupled client-server architecture:

- **Frontend**: React (Vite), TailwindCSS, Framer Motion, Context API.
- **Backend**: FastAPI, AsyncIO, SQLAlchemy, SQLite (via Alembic).
- **AI Core**: OpenRouter (LLM Routing), Tavily (Search), Qdrant (RAG Vector Store).

### 🧠 How the Agent Mesh Works:
1. **Phase 1 (Data Gathering)**: Web Search Agent aggregates real-world data.
2. **Phase 2 (Analysis)**: Market, Customer, and Competitor Agents run in parallel to extract structured contracts (JSON).
3. **Phase 3 (Synthesis)**: SWOT, MVP, GTM, and Risk Agents consume Phase 2 data to generate strategic roadmaps.
4. **Phase 4 (Scoring)**: The Scoring Engine weighs all metrics and calculates the final validation score.

*(For detailed architectural diagrams, check out `docs/architecture.md`)*

---

## 📁 Project Structure

```text
VentureLens/
├── backend/
│   ├── agents/          # Specialized LLM Agents (Market, Competitor, etc.)
│   ├── api/             # FastAPI Routes (Validation, Chat, Export)
│   ├── contracts/       # Pydantic Schemas for Agent Output Validation
│   ├── crew/            # Orchestrator (Mesh Network Controller)
│   ├── database/        # SQLAlchemy Models & SQLite Session
│   ├── guardrails/      # Hallucination & Data Sanitization Managers
│   └── app.py           # FastAPI Entry Point
├── frontend/
│   ├── src/
│   │   ├── components/  # React UI Components (Report Sections, Charts)
│   │   ├── pages/       # Route Views (Dashboard, Workspace, Home)
│   │   └── App.jsx      # React Router
├── docs/                # Comprehensive System Documentation
└── .env                 # Environment Configuration
```

---

## 🚀 Quick Start Guide

### 1. Clone the repository
```bash
git clone https://github.com/your-username/VentureLens.git
cd VentureLens
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key
SECRET_KEY=your_secure_random_string
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r ../requirements.txt
python -m uvicorn app:app --reload
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

🎯 **Visit `http://localhost:5173` and launch your startup!**

---

## 📖 Comprehensive Documentation

To dive deeper into the technical implementation, explore the `docs/` folder:
- 🏗️ [System Architecture](docs/architecture.md)
- 🔄 [System Workflows](docs/system-workflow.md)
- 🤖 [Agent Implementation](docs/agents/agents-documentation.md)
- ⚙️ [Backend Structure](docs/backend/backend-documentation.md)
- 🎨 [Frontend Structure](docs/frontend/frontend-documentation.md)
- 🗄️ [Database Schema](docs/database/database-documentation.md)
- 🚀 [Deployment Guide](docs/deployment/deployment-guide.md)

---

## 🔮 Future Roadmap

- [ ] **PostgreSQL Migration**: Move from SQLite for robust horizontal scalability.
- [ ] **Multi-Tenant Workspaces**: Implement JWT auth for collaborative team environments.
- [ ] **Custom Document RAG**: Upload your own PDFs and market research to feed into the initial context.
- [ ] **Native Editor**: Allow Vera to dynamically edit and update the JSON report based on your chat feedback.
