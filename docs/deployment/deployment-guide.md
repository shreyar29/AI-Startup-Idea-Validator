# Deployment Guide

VentureLens is designed to be easily deployed on standard cloud PaaS providers like **Render**, **Railway**, or **Heroku**.

## 1. Prerequisites

You will need accounts and API keys for the following services:
- **Tavily**: For the Web Search Agent.
- **OpenRouter** (or OpenAI/Anthropic): For the core LLM Engine.
- **Render** (or equivalent): For hosting.

## 2. Environment Variables

Your production environment must define the following variables:

```env
# LLM Configuration
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Search
TAVILY_API_KEY=your_tavily_key

# FastAPI
SECRET_KEY=generate_a_secure_random_string_here
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-domain.com

# Agents
MAX_CONCURRENT_AGENTS=6
```

## 3. Deploying the Backend (FastAPI)

1. Connect your repository to your PaaS.
2. Select **Python** as the environment.
3. Set the Root Directory to `/backend`.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Enter your Environment Variables.
7. Deploy.

## 4. Deploying the Frontend (Vite/React)

1. Create a new Static Site deployment on your PaaS (or Vercel/Netlify).
2. Set the Root Directory to `/frontend`.
3. Build Command: `npm install && npm run build`
4. Publish Directory: `dist`
5. Add an Environment Variable for the API URL:
   `VITE_API_URL=https://your-backend-domain.com`
6. Deploy.

## 5. Production Hardening Notes

- **Database**: SQLite is used currently. If deployed on ephemeral filesystems (like Heroku), SQLite data will be lost on restart. Consider migrating the SQLAlchemy connection string to PostgreSQL for true production.
- **Workers**: Uvicorn is currently run directly. For heavier loads, use `gunicorn` with `uvicorn` workers:
  `gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker`
- **Concurrency**: The Agent Mesh heavily relies on AsyncIO. Ensure the deployment container has enough CPU resources to handle concurrent LLM and Tavily network requests.
