# Walkthrough: Python Environment Setup and System Verification Suite

## 🚀 Accomplishments

### 1. Created Unified Integration Specification: `groq_integration_spec.md`
Comprehensive blueprint mapping audio/resume flow into the grading pipeline, including:
- Architecture flowchart for Groq API + local Python DSP/NLP pipeline
- Librosa acoustic metrics and spaCy profile schema mappings
- Groq API prompt structure with model specifications and parameters
- Output JSON payload format for SQLite `history_logs`
- Continuity checklist for error-free data flow

### 2. Created Dynamic Fallback Evaluation: `dynamic_evaluation_spec.md`
Blueprint for replacing static mock fallback with intelligent local heuristic grading:
- Vulnerability analysis of `KeyError` risks in `main.py`
- Scoring formulas for `score_tech`, `score_comm`, `score_rel` based on keywords, WPM, and voice metrics
- Feedback generation tree that cites matched/missing keywords and pacing advice
- Code replacement blueprints for `main.py` and `llm_service.py`

### 3. Created Full-Stack Fixes Specification: `full_stack_fixes_spec.md`
Blueprint to resolve 404 session lookup failures and dynamic grader fallback bugs:
- Session lookup vulnerability audit (random UUID on page refresh → 404)
- Auto-provisioning session workflow to intercept missing sessions
- Consolidated code replacements for both 404 fix and dynamic grader

### 4. Created Workspace Settings: `.vscode/settings.json`
VS Code / Cursor configuration to clear all static import warnings:
- Extra search paths pointing to `skillsense-ai/backend` as source root
- Auto-binding to `.venv` Python interpreter

### 5. Created Setup & Verification Engine: `setup_and_fix.py`
Self-contained Python script for automated environment setup:
- Python 3.8+ validation
- Virtual environment detection/provisioning
- Pip installs from `requirements.txt` with error logging
- spaCy English NER model download
- Database seeding

### 6. Created Full-System Verification Engine: `verify_system.py`
Advanced validation engine testing the entire stack:
- Environment integrity and package scanning
- Backend module imports validation
- SQLite database schema and record counting
- API route testing via FastAPI TestClient (health, forecast, anomalies)
- Frontend Vite proxy and npm configuration audit
- External API credential probing (Groq, Gemini, AWS)
- Color-coded diagnostics dashboard output

### 7. Created Double-Click Launchers: `setup_env.bat` & `verify_system.bat`
Windows Batch files for one-click setup and verification.

## Fixes Applied

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| 404 on submit-answer | Random UUID from page refresh not in DB | Auto-provision session in `main.py` |
| 500 on submit-answer | KeyError on `grades["score_tech"]` | Safe `.get()` with fallbacks via `_safe_grades()` |
| Static mock scores | Frontend catch block with `Math.random()` | Removed mock fallback; shows real errors |
| No error on upload fail | PortalView silently navigated with random ID | Shows "Backend unreachable" message |
| 0/0/0 grades on short answers | Heuristic grader not wired as fallback | `execute_local_heuristic_grader()` in `llm_service.py` |

## Usage Instructions

1. **Setup Environment**: Double-click `setup_env.bat`
2. **Verify System**: Double-click `verify_system.bat`
3. **Review Specs**: Open `groq_integration_spec.md`, `dynamic_evaluation_spec.md`, `full_stack_fixes_spec.md`
4. **Start Backend**: From Git Bash in `skillsense-ai/backend/`:
   ```bash
   ../../.venv/Scripts/uvicorn app.main:app --reload --port 8000
   ```
5. **Start Frontend**: From Git Bash in `skillsense-ai/frontend/`:
   ```bash
   npm run dev
   ```
6. **Open Browser**: Navigate to `http://localhost:5173`
7. **IDE Setup**: Restart VS Code/Cursor after `setup_env.bat` runs to clear import warnings

## Key Design Decisions

- **Groq as primary LLM**: `llama-3.3-70b-versatile` at temperature 0.3 for grading
- **Heuristic fallback**: 8 keyword domain maps (database, microservice, kubernetes, pipeline, isolation, container, cloud, security)
- **WPM scoring**: Optimal range 110-150 WPM; penalty formula `9.0 - 0.04 * |130 - WPM|`
- **Auto-provisioning**: Creates `guest@fallback.local` user + session on unknown interview_id
