# SkillSense AI — Project Report

## Executive Summary

SkillSense AI is an enterprise-grade unified interview assessment and cloud sandbox optimization platform. It combines **speech analytics**, **NLP-powered resume parsing**, **AI-driven evaluation** (via Groq LLM), **Prophet time-series forecasting**, and **Isolation Forest anomaly detection** into a single coherent system with a modern React frontend.

The platform enables recruiters to conduct AI-graded technical interviews with live speech analysis, provision cloud sandbox environments for candidates, monitor infrastructure costs, and detect anomalies — all from a single interface.

---

## 1. Project Overview

### 1.1 Purpose
SkillSense AI addresses the fragmented nature of technical hiring by unifying:
- Resume screening and skill extraction
- Live AI-graded interviews with speech analytics
- Cloud sandbox provisioning for coding assessments
- FinOps monitoring and cost forecasting
- Anomaly detection on infrastructure telemetry

### 1.2 Key Features
| Feature | Description |
|---------|-------------|
| AI-Powered Interview Grading | 3-axis scoring (Technical, Communication, Relevance) using Groq LLM |
| Resume Intelligence | Automated skill extraction using spaCy NER with custom EntityRuler |
| Speech Analytics | Real-time fluency, pacing, filler-word detection via Librosa DSP |
| Dynamic Question Generation | Adaptive difficulty based on candidate performance |
| Cloud Sandbox Provisioning | AWS EC2 instances per interview session with lifecycle management |
| FinOps Forecasting | Prophet time-series predictions for cloud spending |
| Anomaly Detection | Isolation Forest on VM CPU/RAM/cost telemetry |
| Bilingual AI Chat | Hindi/English candidate assistance via Groq |
| Multi-Theme Design | 5 glass-morphism themes with CSS custom properties |

### 1.3 Target Users
| User Role | Capabilities |
|-----------|-------------|
| Candidate | Upload resume, start interview, respond to questions, view assessment report |
| Recruiter | View candidate assessments, monitor sandbox VMs, analyze costs, review anomalies |
| Admin | Manage users, configure interview modes, review system health |

---

## 2. System Architecture

### 2.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React 18)                   │
│  PortalView → InterviewConsole → ReportDashboard        │
│  RecruiterDashboard (FinOps + Anomaly Monitoring)       │
│  ChatBot (Bilingual Hindi/English)                      │
│  ThemeSwitcher (5 themes)                               │
└──────────────────────┬──────────────────────────────────┘
                       │ Vite Proxy (:3000 → :8000)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 Backend (FastAPI + Uvicorn)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ Auth     │  │ Candidate│  │ Recruiter / FinOps    │  │
│  │ Router   │  │ Router   │  │ Router                │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │
│       │              │                    │              │
│  ┌────▼──────────────▼────────────────────▼───────────┐ │
│  │              Service Layer (7 services)             │ │
│  │  LLMOrchestratorService (Groq → Gemini → Fallback) │ │
│  │  EnterpriseResumeParser (spaCy NER)                │ │
│  │  AudioProcessingEngine (Librosa DSP)               │ │
│  │  SandboxProvisionerService (AWS EC2 / Mock)        │ │
│  │  FinOpsForecaster (Prophet)                        │ │
│  │  CloudResourceAnomalyDetector (Isolation Forest)   │ │
│  │  MonitoringInsightService (Groq-powered insights)  │ │
│  └────────────────────┬───────────────────────────────┘ │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐ │
│  │          Data Layer (SQLAlchemy ORM)                │ │
│  │  users │ interview_sessions │ sandbox_resources     │ │
│  │        │ sandbox_metrics                           │ │
│  └────────────────────┬───────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────┘
                        ▼
              ┌─────────────────┐
              │  SQLite (Dev)   │
              │  PostgreSQL     │
              │  (Production)   │
              └─────────────────┘
```

### 2.2 Tech Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend Framework | FastAPI + Uvicorn | Async REST API server |
| Database ORM | SQLAlchemy | Database-agnostic ORM (SQLite dev / PostgreSQL prod) |
| Authentication | JWT (python-jose) + bcrypt (passlib) | Token-based auth with role-based access |
| LLM Primary | Groq (llama-3.3-70b-versatile) | AI grading, question generation, monitoring insights |
| LLM Fallback | Google Gemini Pro | Secondary LLM provider |
| NLP | spaCy + EntityRuler | Resume skill extraction via Named Entity Recognition |
| Audio DSP | Librosa + NumPy | Speech fluency analysis (WPM, pauses, fillers) |
| Forecasting | Facebook Prophet | Time-series cloud cost prediction |
| Anomaly Detection | Isolation Forest (scikit-learn) | VM resource anomaly detection |
| Cloud Infrastructure | boto3 (AWS EC2) | Sandbox provisioning (with mock fallback) |
| Frontend Framework | React 18 + Vite 5 | Single-page application |
| Charts | ApexCharts (react-apexcharts) | Radar, bar, area visualizations |
| Design System | CSS Custom Properties | 5 glass-morphism themes |
| Containerization | Docker + docker-compose | Multi-stage builds, PostgreSQL 16 |

### 2.3 Project Structure
```
SkillSense AI/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings (env loading)
│   │   │   ├── auth.py             # JWT, bcrypt, dependency injection
│   │   │   ├── database.py         # SQLAlchemy engine & session
│   │   │   └── utils.py            # LLM JSON response parser
│   │   ├── models/
│   │   │   └── tables.py           # 4 ORM models (GUID type support)
│   │   ├── routers/
│   │   │   └── auth.py             # Register, login, profile, users
│   │   ├── services/
│   │   │   ├── groq_service.py     # Groq LLM client (primary)
│   │   │   ├── llm_service.py      # Multi-provider orchestrator
│   │   │   ├── parser_service.py   # spaCy resume parser
│   │   │   ├── audio_service.py    # Librosa audio DSP
│   │   │   ├── sandbox_service.py  # AWS EC2 provisioner
│   │   │   ├── forecasting_service.py  # Prophet forecaster
│   │   │   ├── anomaly_service.py  # Isolation Forest detector
│   │   │   └── monitoring_service.py   # Groq monitoring facade
│   │   └── main.py                 # FastAPI entry (15 API routes)
│   ├── database/
│   │   ├── seed_data.py            # Demo data generator
│   │   └── seed_db.py              # ORM database seeder
│   ├── .env                        # Runtime configuration
│   ├── .env.example                # Environment template
│   ├── requirements.txt            # 24 Python dependencies
│   └── Dockerfile                  # Multi-stage Python 3.11
├── frontend/                       # React application
│   ├── src/
│   │   ├── views/
│   │   │   ├── PortalView.jsx      # Landing + candidate form
│   │   │   ├── InterviewConsole.jsx    # Live interview UI
│   │   │   ├── RecruiterDashboard.jsx  # Analytics dashboard
│   │   │   └── ReportDashboard.jsx     # Assessment report
│   │   ├── components/
│   │   │   ├── ChatBot.jsx         # Bilingual draggable chat
│   │   │   ├── Button.jsx          # Memoized button
│   │   │   ├── AudioWaveform.jsx   # Canvas audio visualizer
│   │   │   ├── WebcamStream.jsx    # Camera feed
│   │   │   ├── CostTrendChart.jsx  # ApexCharts area chart
│   │   │   ├── SandboxMetricCard.jsx   # VM metrics card
│   │   │   └── ThemeSwitcher.jsx   # 5-theme dropdown
│   │   ├── assets/index.css        # 408-line design system
│   │   └── App.jsx                 # SPA shell + routing
│   ├── package.json                # React 18 + Vite 5
│   └── vite.config.js              # Proxy to backend :8000
├── scripts/
│   ├── setup_and_fix.py            # Environment setup
│   ├── verify_system.py            # System verification
│   ├── verify_groq_integration.py  # Groq API integration test
│   └── _autotest.py                # Raw API test
├── docker-compose.yml              # PostgreSQL 16 + API
├── render.yaml                     # Render.com deployment
└── .vscode/settings.json           # IDE configuration
```

---

## 3. Data Flow Architecture

### 3.1 Candidate Interview Flow
```
PortalView
    │
    ├─ POST /upload-resume
    │   ├─ EnterpriseResumeParser.parse_resume_document(pdf_bytes)
    │   │   └─ spaCy NER → candidate_skills list
    │   ├─ DBUser created/fetched
    │   ├─ DBInterviewSession created (domain, mode, skills)
    │   ├─ SandboxProvisionerService.provision_developer_sandbox()
    │   │   └─ AWS EC2 run_instances / mock fallback
    │   ├─ DBSandboxResource created
    │   └─ LLMOrchestratorService.generate_next_question()
    │       └─ Groq → Gemini → fallback question bank
    │
    └─► InterviewConsole
         │
         ├─ POST /submit-answer (×5 questions)
         │   ├─ AudioProcessingEngine.compute_speech_fluency()
         │   │   └─ Librosa: WPM, pauses, fillers, fluency score
         │   ├─ LLMOrchestratorService.grade_response()
         │   │   └─ Groq → Gemini → heuristic 3-axis grading
         │   ├─ history_logs.append(question, transcript, metrics, grades)
         │   ├─ Auto-terminates sandbox at Q5
         │   └─ Returns next_question (adaptive difficulty)
         │
         └─► ReportDashboard
              ├─ Competency radar (5 axes: Tech, Comm, Rel, Fluency, Pace)
              ├─ Per-question score bar chart
              └─ Detailed question-by-question analysis
```

### 3.2 Recruiter Analytics Flow
```
RecruiterDashboard
    │
    ├─ POST /recruiter/sandbox/anomalies
    │   ├─ CloudResourceAnomalyDetector.evaluate_resource_telemetry()
    │   │   └─ Isolation Forest → anomaly scores + labels
    │   └─ MonitoringInsightService.enrich_anomalies()
    │       └─ Groq: severity, hypothesis, recommended_action
    │
    ├─ POST /recruiter/sandbox/forecast
    │   └─ FinOpsForecaster.generate_expenditure_predictions()
    │       └─ Prophet: 30-day daily cost projections
    │
    └─ POST /monitoring/cost-tip
        └─ MonitoringInsightService.cost_optimization_tip()
            └─ Groq: actionable savings recommendation
```

### 3.3 AI Chat Flow
```
ChatBot (Hindi/English)
    └─ POST /chat
        ├─ Groq bilingual chat (same language as user)
        └─ Context-aware (last 10 messages)
```

---

## 4. Service Layer Details

### 4.1 LLMOrchestratorService
Multi-provider orchestration with 3-tier fallback:
1. **Groq** (primary) — llama-3.3-70b-versatile via REST API
2. **Gemini** (secondary) — gemini-pro via google-generativeai
3. **Heuristic** (fallback) — domain-specific question bank + keyword scoring

**Capabilities:**
- `generate_next_question()` — Adaptive difficulty based on score history
- `grade_response()` — 3-axis scoring (Technical, Communication, Relevance)
- `execute_local_heuristic_grader()` — Keyword-matching fallback grader

### 4.2 EnterpriseResumeParser
- **Primary:** spaCy NER with custom EntityRuler (25 technical skill patterns)
- **Fallback:** Regex keyword matching against skill taxonomy
- **Output:** `{candidate_skills, candidate_email, candidate_phone}`

### 4.3 AudioProcessingEngine
- **Primary:** Librosa DSP — RMS energy, silence detection, WPM, filler counting
- **Fallback:** Transcript-only statistical estimation
- **Metrics:** audio_duration_sec, speaking_rate_wpm, pause_count, filler_words_count, filler_ratio, fluency_score

### 4.4 SandboxProvisionerService
- **Primary:** AWS EC2 (boto3) — run_instances with encryption, IMDSv2, tags
- **Fallback:** Mock instance IDs with realistic cost estimates
- **Features:** Cost tracking, instance status checking, graceful error handling

### 4.5 FinOpsForecaster
- **Primary:** Facebook Prophet — additive seasonal time-series model
- **Fallback:** Linear trend with weekly factors + noise
- **Output:** 30-day daily cost projections with confidence intervals

### 4.6 CloudResourceAnomalyDetector
- **Primary:** Isolation Forest (contamination=0.05)
- **Fallback:** Rule-based threshold detection (CPU>85%, RAM>80%, Cost>$15)
- **Output:** anomaly_score (0-1), is_anomaly boolean per metric

### 4.7 MonitoringInsightService
Groq-powered insight generation:
- `session_summary()` — Interview performance summary + hiring recommendation
- `cost_optimization_tip()` — Actionable savings advice
- `enrich_anomalies()` — Severity, hypothesis, and remediation for detected anomalies

---

## 5. Database Schema

### 5.1 Entity Relationship
```
users (1) ──── (many) interview_sessions
users (1) ──── (many) sandbox_resources
interview_sessions (1) ──── (1) sandbox_resources
sandbox_resources (1) ──── (many) sandbox_metrics
```

### 5.2 Models

| Model | Key Fields | Purpose |
|-------|-----------|---------|
| **DBUser** | id (UUID), name, email, password_hash, role, aws_credential_secret_b64, created_at | User accounts (candidate/recruiter) |
| **DBInterviewSession** | id (UUID), candidate_id (FK), domain, mode, status, history_logs (JSON), skills (JSON), started_at, completed_at | Interview sessions with AI grading history |
| **DBSandboxResource** | resource_id (Instance ID PK), user_id (FK), interview_id (FK), provider, instance_tier, region, status, hourly_rate | AWS EC2 sandbox instances |
| **DBSandboxMetric** | id (auto), resource_id (FK), cpu_utilization, ram_utilization, network_egress_bytes, daily_cost, is_anomaly, anomaly_score, timestamp | Time-series VM telemetry |

### 5.3 Database Support
- **Development:** SQLite (`database/skillsense_dev.db`) — zero-config
- **Production:** PostgreSQL 16 via docker-compose — connection pooling (10+20)
- **ORM:** SQLAlchemy with database-agnostic JSON column (JSONB on PG, TEXT on SQLite)
- **GUID:** Custom `GUID` type — PostgreSQL UUID or CHAR(36) for SQLite

---

## 6. Authentication & Security

### 6.1 Authentication System
| Component | Implementation |
|-----------|---------------|
| Password Hashing | bcrypt via passlib (12 rounds) |
| JWT Tokens | HS256, configurable expiry (default 60 min) |
| Role-Based Access | `require_role("recruiter")` dependency |
| Optional Auth | `get_optional_user` — works with/without token |
| Required Auth | `get_current_user` — 401 if missing/invalid |

### 6.2 Security Measures
| Area | Implementation |
|------|---------------|
| CORS | Configurable origins (default: localhost:3000,5173) |
| AES-256-GCM | Schema ready for AWS credential encryption |
| Input Validation | Pydantic schemas on all request bodies |
| File Upload | PDF-only validation, temp file cleanup after processing |
| EC2 Hardening | IMDSv2 required, encrypted EBS, tagged instances |
| Secrets | `.env` file excluded from version control |

### 6.3 API Endpoints
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/health` | GET | None | System health check |
| `/api/v1/modes` | GET | None | Available interview modes |
| `/api/v1/auth/register` | POST | None | User registration |
| `/api/v1/auth/login` | POST | None | User login (returns JWT) |
| `/api/v1/auth/profile` | GET | Required | User profile |
| `/api/v1/auth/users` | GET | Recruiter | List all users |
| `/api/v1/candidate/upload-resume` | POST | Optional | Start interview session |
| `/api/v1/candidate/submit-answer` | POST | Optional | Submit answer + get next question |
| `/api/v1/recruiter/sandbox/forecast` | POST | Recruiter | Prophet cost forecast |
| `/api/v1/recruiter/sandbox/anomalies` | POST | Recruiter | Isolation Forest analysis |
| `/api/v1/monitoring/session-summary` | POST | Optional | Groq session summary |
| `/api/v1/monitoring/cost-tip` | POST | Optional | Groq cost optimization tip |
| `/api/v1/chat` | POST | Optional | Bilingual AI chat |

---

## 7. Frontend Design System

### 7.1 Themes
5 glass-morphism themes via CSS custom properties:

| Theme | Primary Color | Character |
|-------|--------------|-----------|
| Slate Dark (default) | Indigo (#785aff) | Deep, professional |
| Neon Cyberpunk | Hot Pink (#be185d) | Vibrant, energetic |
| Emerald Horizon | Forest Green (#047857) | Natural, calm |
| Sunset Fusion | Warm Orange (#c2410c) | Warm, inviting |
| Ocean Mist | Deep Blue (#0369a1) | Cool, focused |

### 7.2 Component Library
| Component | Features |
|-----------|----------|
| Button | 3 variants (primary, outline, danger), 3 sizes, icon support, memoized |
| ChatBot | Draggable, bilingual (Hindi/English), voice input, auto-scroll |
| AudioWaveform | Canvas-based, real-time visualization, static fallback |
| WebcamStream | Camera toggle, live indicator, graceful error handling |
| CostTrendChart | ApexCharts area, gradient fill, dark theme |
| SandboxMetricCard | CPU/RAM progress bars, anomaly alert banner |
| ThemeSwitcher | Dropdown with color preview, click-outside dismiss |

### 7.3 Design Principles
- **Glass morphism:** `backdrop-filter: blur()` with semi-transparent backgrounds
- **CSS custom properties:** Theme-aware via `var(--primary)`, `var(--bg-card)`, etc.
- **Responsive:** CSS Grid with `auto-fill` and `minmax` for adaptive layouts
- **Animations:** `animate-fade-in`, `animate-slide-left`, `pulseGlow` keyframes
- **Accessibility:** Semantic HTML, ARIA labels, keyboard navigation

---

## 8. Deployment

### 8.1 Local Development
```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev                    # Port 3000, proxies to :8000
```

### 8.2 Docker
```bash
docker-compose up --build      # PostgreSQL 16 + API
```

### 8.3 Production (Render.com)
- `render.yaml` configured for auto-deploy from git
- PostgreSQL add-on for persistent data
- Environment variables via Render dashboard

### 8.4 Scripts
| Script | Purpose |
|--------|---------|
| `setup_and_fix.py` | Full environment setup (venv, deps, spaCy model, DB seed) |
| `verify_system.py` | Comprehensive system verification (8 sections) |
| `verify_groq_integration.py` | Groq API integration testing (6 steps) |
| `_autotest.py` | Raw HTTP API test for submit-answer endpoint |

---

## 9. Graceful Degradation

Every service operates with a real→fallback chain. The system runs fully functional without any external API keys or cloud credentials:

| Service | Primary | Fallback | Trigger |
|---------|---------|----------|---------|
| LLM Grading | Groq API | Gemini → heuristic keyword scoring | No API key |
| Question Generation | Groq API | Gemini → domain question bank | No API key |
| Resume Parsing | spaCy NER | Regex keyword matching | No spaCy model |
| Audio DSP | Librosa | Transcript-only statistical estimation | No librosa |
| Forecasting | Facebook Prophet | Linear trend with weekly factors | No prophet |
| Anomaly Detection | Isolation Forest | Rule-based threshold detection | No scikit-learn |
| AI Chat | Groq API | Static offline message | No API key |
| Cloud Sandbox | AWS EC2 (boto3) | Mock instance IDs + cost estimates | No AWS creds |
| Monitoring | Groq API | Predefined insight templates | No API key |

---

## 10. Future Scope

### 10.1 Short-Term Enhancements
| Area | Enhancement | Impact |
|------|------------|--------|
| Authentication | Add login/register UI in frontend | Complete auth flow for candidates and recruiters |
| Real Audio Recording | WebRTC recording with actual audio upload | Replace placeholder blobs with real speech analysis |
| Session History | Load past interviews from database | Candidates can review previous attempts |
| Live Telemetry | WebSocket-based sandbox metrics streaming | Real-time CPU/RAM updates on RecruiterDashboard |
| Export Reports | PDF export of assessment reports | Shareable candidate evaluation documents |

### 10.2 Medium-Term Features
| Area | Enhancement | Impact |
|------|------------|--------|
| Multi-Modal Interviews | Video interview support with facial expression analysis | Richer candidate assessment |
| Collaborative Scoring | Multiple recruiter reviews per candidate | Reduced bias, consensus hiring |
| Question Bank API | Dynamic question bank with version control | Scalable, community-contributed questions |
| Integration Layer | ATS integrations (Greenhouse, Lever, Workday) | Enterprise adoption |
| Analytics Dashboard | Historical hiring metrics, time-to-hire, success rates | Data-driven recruiting decisions |

### 10.3 Long-Term Vision
| Area | Enhancement | Impact |
|------|------------|--------|
| Adaptive AI Interviewer | Real-time conversation flow (not just Q&A) | Natural interview experience |
| Skills Graph | Knowledge graph of candidate skills vs job requirements | Precise skill-gap analysis |
| Global Sandbox | Multi-region AWS/GCP/Azure sandbox provisioning | Low-latency global access |
| Enterprise SSO | SAML/OIDC integration for enterprise auth | Enterprise security compliance |
| Mobile App | React Native companion app | Interview on mobile devices |
| API Marketplace | Public API for third-party integrations | Platform ecosystem |

### 10.4 Infrastructure Improvements
| Area | Enhancement | Impact |
|------|------------|--------|
| Caching Layer | Redis for session data and LLM response caching | Reduced latency, lower API costs |
| Message Queue | Celery/RabbitMQ for async task processing | Non-blocking grading pipeline |
| Observability | OpenTelemetry tracing, Prometheus metrics | Production monitoring |
| CI/CD Pipeline | GitHub Actions for automated testing and deployment | Reliable releases |
| Load Testing | k6/Locust benchmarks for concurrent interviews | Scalability validation |

---

## 11. Audit Summary

### 11.1 Codebase Statistics
| Metric | Count |
|--------|-------|
| Python files | 26 |
| JSX components | 13 |
| CSS design system | 408 lines |
| API endpoints | 15 |
| Backend services | 7 |
| Database models | 4 |
| Themes | 5 |
| Dependencies (Python) | 24 |
| Dependencies (JS) | 8 |

### 11.2 Architecture Quality
| Aspect | Assessment |
|--------|-----------|
| Separation of Concerns | Clean service layer, router layer, and data layer separation |
| Graceful Degradation | Every service has real→fallback chain; runs without external deps |
| Type Safety | Pydantic schemas, SQLAlchemy models, TypeScript-like prop patterns |
| Error Handling | Try/except with fallback at every service boundary |
| Configuration | Centralized via pydantic-settings, `.env` support |
| Scalability | Stateless API, PostgreSQL-ready, Docker support |

### 11.3 Known Limitations
| Limitation | Current State | Recommended Fix |
|-----------|--------------|-----------------|
| No login UI | Frontend lacks auth flow | Add login/register views |
| Placeholder audio | InterviewConsole sends blob placeholder | Implement WebRTC recording |
| Hardcoded demo data | RecruiterDashboard has mock candidates | Fetch from API endpoints |
| No rate limiting | API has no request throttling | Add SlowAPI or nginx rate limiting |
| No API versioning | Single `/api/v1/` prefix | Plan for `/api/v2/` migration path |
| No logging framework | Basic `print` and `logging` | Structured logging with correlation IDs |
