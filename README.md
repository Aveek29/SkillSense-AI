# SkillSense AI Platform

Enterprise-grade technical recruiting platform with AI-driven interviews, speech analytics, resume parsing, and cloud sandbox management.

## Structure

```
skillsense-ai/
├── frontend/          # React 18 
├── backend/           # FastAPI 
├── docs/              # Specifications and blueprints
├── scripts/           # Utility and verification scripts
└── docker-compose.yml # PostgreSQL + API for local dev only for local machine

```

## Quick Start for local maachine

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


