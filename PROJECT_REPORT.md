# SkillSense AI — Comprehensive Project Report

## Executive Summary

SkillSense AI is an enterprise-grade unified interview assessment and cloud sandbox optimization platform. It combines **speech analytics**, **NLP-powered resume parsing**, **AI-driven evaluation** (via Groq LLM), **Prophet time-series forecasting**, and **Isolation Forest anomaly detection** into a single coherent system with a modern React frontend.

This report documents the complete audit, bug fixes, and production hardening applied across the entire codebase.

---

## 1. Project Architecture

```
SkillSense AI/
├── backend/                    # FastAPI + SQLAlchemy + Groq LLM
│   ├── app/
│   │   ├── core/               # Config, auth, database, utils
│   │   ├── models/             # SQLAlchemy ORM tables (4 models)
│   │   ├── routers/            # Auth API endpoints
│   │   ├── services/           # 7 AI/ML/cloud services
│   │   └── main.py             # FastAPI entry (15 API routes)
│   ├── database/               # Seed scripts, SQLite DB
│   ├── .env                    # Runtime config
│   ├── requirements.txt        # 24 Python dependencies
│   └── Dockerfile              # Multi-stage Python 3.11 build
├── frontend/                   # React 18 + Vite 5
│   ├── src/
│   │   ├── views/              # 4 page views
│   │   ├── components/         # 7 reusable components
│   │   ├── assets/index.css    # 408-line design system (5 themes)
│   │   └── App.jsx             # SPA shell with routing
│   └── vite.config.js          # Proxy to :8000
├── scripts/                    # Setup, verification, testing
├── docker-compose.yml          # PostgreSQL 16 + API
└── .vscode/settings.json       # IDE config
```

### Tech Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI + Uvicorn | Async REST API |
| Database | SQLAlchemy + SQLite/PostgreSQL | ORM + data persistence |
| Auth | JWT (python-jose) + bcrypt (passlib) | Token-based authentication |
| LLM Primary | Groq (llama-3.3-70b-versatile) | AI grading, question generation, monitoring |
| LLM Fallback | Google Gemini Pro | Secondary LLM provider |
| NLP | spaCy + EntityRuler | Resume skill extraction (NER) |
| Audio DSP | Librosa + NumPy | Speech fluency analysis |
| Forecasting | Facebook Prophet | Time-series cost prediction |
| Anomaly Detection | Isolation Forest (scikit-learn) | VM resource anomaly detection |
| Cloud | boto3 (AWS EC2) | Sandbox provisioning (with mock fallback) |
| Frontend | React 18 + Vite 5 | SPA with code splitting |
| Charts | ApexCharts (react-apexcharts) | Radar, bar, area charts |
| Design | CSS Custom Properties | 5 glass-morphism themes |

---

## 2. Files Audited & Modified

### Backend (18 files)
| File | Status | Changes |
|------|--------|---------|
| `app/main.py` | **Fixed** | Auth on submit-answer (401→optional), session-summary & cost-tip auth (→optional), utcnow→timezone-aware, added DATABASE_DIR creation, guest_user role field |
| `app/core/config.py` | **Fixed** | Default DATABASE_URL: `./skillsense_dev.db` → `./database/skillsense_dev.db` |
| `app/core/auth.py` | **Fixed** | Removed unused `Request` import, `utcnow()` → `datetime.now(timezone.utc)` |
| `app/core/database.py` | Verified | SQLite path resolution, pool settings — clean |
| `app/core/utils.py` | Verified | `clean_json_payload()` LLM response parser — clean |
| `app/models/tables.py` | **Fixed** | All `default=datetime.datetime.utcnow` → `lambda: datetime.now(timezone.utc)` (4 tables) |
| `app/routers/auth.py` | **Fixed** | Removed unused `EmailStr` import |
| `app/services/sandbox_service.py` | **Rewritten** | Production-ready: boto3 credential validation, graceful mock fallback, proper EC2 config (GP3, encryption, metadata options, tags), cost tracking, instance status checking |
| `app/services/llm_service.py` | **Fixed** | Removed unused `mode_lower` in `_fallback_question_generator`, mode alignment with frontend |
| `app/services/monitoring_service.py` | **Fixed** | Optional GroqAIService injection to avoid duplicate clients |
| `app/services/groq_service.py` | Verified | Groq client, fallback chain — clean |
| `app/services/parser_service.py` | Verified | spaCy + regex fallback — clean |
| `app/services/audio_service.py` | Verified | Librosa DSP + transcript fallback — clean |
| `app/services/forecasting_service.py` | Verified | Prophet + math fallback — clean |
| `app/services/anomaly_service.py` | Verified | Isolation Forest + rule-based fallback — clean |
| `.env` | **Fixed** | Added `JWT_SECRET_KEY`, `AES_SECRET_KEY_B64`, fixed `DATABASE_URL` |
| `.env.example` | **Fixed** | Updated `DATABASE_URL` to match restructured path |
| `app/core/security.py` | **Deleted** | Dead code (never imported anywhere) |

### Frontend (8 files)
| File | Status | Changes |
|------|--------|---------|
| `src/components/ChatBot.jsx` | **Fixed** | `dragging` (undefined) → `draggingRef.current` (React ref) |
| `src/views/InterviewConsole.jsx` | **Fixed** | Added `Authorization: Bearer` header support from localStorage |
| `src/views/PortalView.jsx` | **Fixed** | Mode keys aligned with backend: `HR`→`HR & Cultural`, `System Design`→`System Design & Architecture`, `Behavioral`→`Behavioral & Leadership`, `Coding`→`Coding & Algorithms`, `DevOps`→`Hybrid (AI Adaptive)` |
| `src/views/RecruiterDashboard.jsx` | **Rewritten** | Fetches anomalies from `/api/v1/recruiter/sandbox/anomalies` with mock fallback, dynamic stats, API status indicator |
| `src/views/ReportDashboard.jsx` | Verified | Charts, averages, question breakdown — clean |
| `src/App.jsx` | Verified | SPA routing, theme management — clean |
| `src/components/Button.jsx` | Verified | Memoized button — clean |
| `src/components/SandboxMetricCard.jsx` | Verified | CPU/RAM meters — clean |
| `src/components/CostTrendChart.jsx` | Verified | ApexCharts area — clean |
| `src/components/AudioWaveform.jsx` | Verified | Canvas visualizer — clean |
| `src/components/WebcamStream.jsx` | Verified | Camera feed — clean |
| `src/components/ThemeSwitcher.jsx` | Verified | 5-theme dropdown — clean |
| `src/assets/index.css` | Verified | 408-line design system — clean |

### Scripts (3 files)
| File | Status | Changes |
|------|--------|---------|
| `scripts/verify_system.py` | **Fixed** | Path: `skillsense-ai/backend` → `backend` (flat restructure), removed dead `app.core.security` import check, updated DB path |
| `scripts/verify_groq_integration.py` | **Fixed** | Same path fixes, DB path updated |
| `scripts/setup_and_fix.py` | **Fixed** | Same path fixes, DB path updated in `.env` defaults |
| `scripts/_autotest.py` | Verified | Raw HTTP test — clean |

### Deleted Files
| File | Reason |
|------|--------|
| `backend/app/core/security.py` | Dead code — `SecureCredentialStore` never imported anywhere |
| `backend/database/schema.sql` | Redundant — SQLAlchemy `Base.metadata.create_all()` handles schema |
| `frontend/src/hooks/` | Empty directory |
| `frontend/public/assets/branding/` | Empty directory |
| `frontend/public/assets/fonts/` | Empty directory |
| `frontend/dist/` | Build output (should not be in repo) |

---

## 3. Critical Bugs Fixed

### 3.1 Authorization 401 Errors (Interview Flow Breaker)
**Before:** `submit-answer`, `session-summary`, `cost-tip` all required `get_current_user` (JWT mandatory). Frontend never sends auth headers → **every interview answer submission returned 401**.

**After:** All three endpoints use `get_optional_user` — works with or without auth. Frontend's `InterviewConsole.jsx` now sends `Authorization: Bearer` header when a token exists in localStorage.

### 3.2 Undefined `dragging` Variable (ChatBot Crash)
**Before:** `ChatBot.jsx:139` referenced `dragging` — a variable that doesn't exist. This caused a ReferenceError during drag interactions.

**After:** Changed to `draggingRef.current` — the correct React ref that tracks drag state.

### 3.3 Database Path Mismatch (Startup Crash)
**Before:** `.env` and `config.py` default pointed to `./skillsense_dev.db` (old flat structure). After restructure, the DB should live in `./database/skillsense_dev.db`.

**After:** Both `.env` and `config.py` updated. `main.py` startup now creates the `database/` directory automatically via `os.makedirs(DATABASE_DIR, exist_ok=True)`.

### 3.4 Deprecated `datetime.utcnow()` (Python 3.12+ Warning)
**Before:** Used in `auth.py`, `main.py`, `tables.py` (4 model defaults) — deprecated since Python 3.12.

**After:** All replaced with `datetime.now(timezone.utc)` or `lambda: datetime.now(timezone.utc)` for SQLAlchemy defaults.

### 3.5 Frontend-Backend Mode Key Mismatch
**Before:** Frontend sent `HR`, `System Design`, `Behavioral`, `Coding`, `DevOps`. Backend `INTERVIEW_MODES` expected `HR & Cultural`, `System Design & Architecture`, `Behavioral & Leadership`, `Coding & Algorithms`, `Hybrid (AI Adaptive)`. Mode was stored in DB with inconsistent keys.

**After:** Frontend mode keys aligned exactly with backend `INTERVIEW_MODES` dictionary.

### 3.6 Missing Security Keys in `.env`
**Before:** `.env` had no `JWT_SECRET_KEY` or `AES_SECRET_KEY_B64`. JWT encoding would fail with empty string.

**After:** Default dev keys added to `.env` with comments to change for production.

### 3.7 Dead Code References in Scripts
**Before:** All 3 scripts referenced `skillsense-ai/backend` (old nested path), and `verify_system.py` imported `app.core.security` (deleted module).

**After:** All paths updated to flat restructure (`backend/`). Dead import removed.

### 3.8 Sandbox Service Ungraceful AWS Failure
**Before:** `provision_developer_sandbox` and `terminate_developer_sandbox` raised `RuntimeError` on AWS API failure → 500 error cascade.

**After:** Complete rewrite with: boto3 credential validation on init, graceful mock fallback on any AWS error, proper EC2 config (GP3 EBS, encryption, metadata options, tags), cost tracking, instance status checking.

### 3.9 Duplicate GroqAIService Instances
**Before:** `MonitoringInsightService` created its own `GroqAIService()` instance. `LLMOrchestratorService` also created one. Two separate clients with separate connection pools.

**After:** `MonitoringInsightService` accepts optional `GroqAIService` injection. `main.py` can share instances if needed.

---

## 4. Data Flow Architecture

```
Candidate Portal (PortalView)
    │
    ├─ POST /upload-resume ──► Resume Parser (spaCy NER)
    │                           ├─ Creates/ fetches DBUser
    │                           ├─ Creates DBInterviewSession
    │                           ├─ Provisions Sandbox (EC2 / mock)
    │                           └─ LLM generates first question
    │
    └─► InterviewConsole
         │
         ├─ POST /submit-answer ──► Audio Service (Librosa)
         │   (every answer)         ├─ Speech fluency metrics
         │                          ├─ LLM grades response (3-axis)
         │                          ├─ Appends to history_logs JSON
         │                          ├─ Auto-terminates sandbox at Q5
         │                          └─ Returns next question
         │
         └─► ReportDashboard
              ├─ Competency radar (ApexCharts)
              ├─ Per-question bar chart
              └─ Detailed analysis cards

Recruiter Dashboard (RecruiterDashboard)
    │
    ├─ POST /recruiter/sandbox/anomalies ──► Isolation Forest
    │                                        ├─ Rule-based fallback
    │                                        └─ Groq enriches insights
    │
    └─ POST /recruiter/sandbox/forecast ──► Prophet
                                             └─ Time-series projections

AI ChatBot (ChatBot)
    └─ POST /chat ──► Groq bilingual chat (Hindi/English)
```

---

## 5. Graceful Degradation Matrix

Every service has a real→fallback chain. The system runs fully functional without any external dependencies:

| Service | Real Library | Fallback | Trigger |
|---------|-------------|----------|---------|
| LLM Grading | Groq API | Gemini → heuristic keyword scoring | No API key |
| Question Gen | Groq API | Gemini → domain question bank | No API key |
| Resume Parsing | spaCy NER | Regex keyword matching | No spaCy model |
| Audio DSP | Librosa | Transcript-only statistical estimation | No librosa |
| Forecasting | Facebook Prophet | Linear trend with weekly factors | No prophet |
| Anomaly Detection | Isolation Forest | Rule-based threshold detection | No scikit-learn |
| Chat | Groq API | Static offline message | No API key |
| Sandbox | AWS EC2 (boto3) | Mock instance IDs + cost estimates | No AWS creds |
| Monitoring | Groq API | Predefined insight templates | No API key |

---

## 6. Security Summary

| Area | Status | Notes |
|------|--------|-------|
| JWT Authentication | Implemented | HS256, configurable expiry, role-based access |
| Password Hashing | Implemented | bcrypt via passlib |
| CORS | Configurable | Defaults to localhost:3000,5173 |
| AES-256-GCM | Schema ready | `aws_credential_secret_b64` column on users table |
| Input Validation | Pydantic schemas | All request bodies validated |
| File Upload | Size/type check | PDF-only on resume, temp file cleanup |
| Secrets | `.env` excluded | Added to `.gitignore` pattern |
| EC2 Security | Hardened | IMDSv2 required, encrypted EBS, tagged instances |

---

## 7. Database Schema

4 SQLAlchemy models with SQLite (dev) / PostgreSQL (production) support:

- **users** — UUID PK, name, email, bcrypt hash, role, AES-encrypted AWS creds
- **interview_sessions** — UUID PK, FK→users, domain, mode, status, JSON history_logs, JSON skills
- **sandbox_resources** — Instance ID PK, FK→users, FK→sessions, provider, tier, region, status, hourly_rate
- **sandbox_metrics** — Auto-increment PK, FK→sandbox_resources, CPU/RAM/cost telemetry, Isolation Forest anomaly scores

---

## 8. Frontend Design System

5 glass-morphism themes via CSS custom properties:
1. **Slate Dark** (default) — Deep indigo
2. **Neon Cyberpunk** — Hot pink
3. **Emerald Horizon** — Forest green
4. **Sunset Fusion** — Warm orange
5. **Ocean Mist** — Deep blue

Components use `var(--primary)`, `var(--bg-card)`, `var(--glass-border)` etc. for theme-aware styling. All glass panels use `backdrop-filter: blur()` with semi-transparent backgrounds.

---

## 9. Deployment Options

| Method | Command | Notes |
|--------|---------|-------|
| Local Dev | `cd backend; uvicorn app.main:app --reload --port 8000` | SQLite auto-created |
| Frontend Dev | `cd frontend; npm run dev` | Port 3000, proxies to :8000 |
| Docker | `docker-compose up --build` | PostgreSQL 16 + API |
| Production | Render.com `render.yaml` | Auto-deploy from git |

---

## 10. How to Run

### Quick Start
```bash
# 1. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
npm install
npm run dev

# 3. Open http://localhost:3000
```

### Scripts
```bash
python scripts/setup_and_fix.py        # Full environment setup
python scripts/verify_system.py        # System verification
python scripts/verify_groq_integration.py  # Groq API integration test
python scripts/_autotest.py            # Raw API test (requires running server)
```

---

## 11. Changes Summary (This Session)

**18 files modified**, **1 file rewritten**, **3 scripts fixed**, **3 files deleted**

| Category | Count | Files |
|----------|-------|-------|
| Auth fixes | 4 | main.py, auth.py, routers/auth.py, InterviewConsole.jsx |
| Path fixes | 4 | config.py, .env, .env.example, 3 scripts |
| Deprecation fixes | 3 | auth.py, main.py, tables.py |
| Service hardening | 3 | sandbox_service.py (rewrite), monitoring_service.py, llm_service.py |
| Frontend fixes | 4 | ChatBot.jsx, InterviewConsole.jsx, PortalView.jsx, RecruiterDashboard.jsx |
| Dead code removed | 3 | security.py, schema.sql, empty dirs |
