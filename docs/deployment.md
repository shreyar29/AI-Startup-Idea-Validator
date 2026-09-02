# Deployment & Configuration Guide

VentureLens is architected to be cloud-agnostic, supporting containerized deployments across modern PaaS providers.

## 1. Environment Configuration
The `.env` file must be strictly configured:
- `OPENROUTER_API_KEY`: Required for routing LLM calls.
- `TAVILY_API_KEY`: Required for live web search functionality.
- `SECRET_KEY`: Required for session/auth encryption.

## 2. Backend Deployment (Render / Railway / Heroku)
The backend is a stateless FastAPI ASGI application, with the exception of the SQLite database.
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Database Scalability**: For production, update the `SQLALCHEMY_DATABASE_URL` to point to a managed PostgreSQL instance to prevent SQLite file-locking under heavy concurrent orchestration load.

## 3. Frontend Deployment (Vercel / Netlify)
The frontend is a static React/Vite build.
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment**: Inject `VITE_API_BASE_URL` pointing to your deployed backend domain (ensure `wss://` is supported for the Vera Chat WebSockets).
