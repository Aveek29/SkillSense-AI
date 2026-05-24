# SkillSense AI Platform

Enterprise-grade technical recruiting platform with AI-driven interviews, speech analytics, resume parsing, and cloud sandbox management.

## Structure

```
skillsense-ai/
├── frontend/          # React 18 + Vite SPA — deploy on Vercel
├── backend/           # FastAPI + Python 3.11 — deploy on Render
├── docs/              # Specifications and blueprints
├── scripts/           # Utility and verification scripts
└── docker-compose.yml # PostgreSQL + API for local dev
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env   # fill in GROQ_API_KEY and JWT_SECRET_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Frontend → Vercel
1. Push to GitHub
2. Import `frontend/` as a Vercel project
3. Set env var `VITE_API_URL` to your Render backend URL + `/api/v1`

### Backend → Render
1. Push to GitHub
2. Create a new Web Service from `backend/`
3. Use Docker deployment (Dockerfile included)
4. Set required env vars: `GROQ_API_KEY`, `JWT_SECRET_KEY`, `AES_SECRET_KEY_B64`
5. Health check path: `/api/v1/health`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM features |
| `JWT_SECRET_KEY` | Yes | Secret key for JWT token signing |
| `AES_SECRET_KEY_B64` | No | AES-256 encryption key (base64) |
| `DATABASE_URL` | No | Database URL (defaults to SQLite) |
| `GEMINI_API_KEY` | No | Google Gemini fallback API key |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
