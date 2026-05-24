# Implementation Plan: Python Environment, System Verification & Setup Suite

## Overview
This plan outlines the complete setup, verification, and diagnostic suite for the SkillSense AI platform. All scripts and configurations are self-contained in the workspace root (`E:\SkillSense AI`) and are double-clickable on Windows.

## File Inventory

| File | Purpose | Status |
|------|---------|--------|
| `setup_and_fix.py` | Environment setup: venv creation, pip installs, spaCy model, DB seed | ✅ Created |
| `setup_env.bat` | Double-click launcher for setup_and_fix.py | ✅ Created |
| `verify_system.py` | Full-stack diagnostic: imports, DB, routes, frontend, credentials | ✅ Created |
| `verify_system.bat` | Double-click launcher for verify_system.py | ✅ Created |
| `.vscode/settings.json` | VS Code/Cursor workspace config for import resolution | ✅ Created |
| `groq_integration_spec.md` | Groq API + local DSP/NLP integration blueprint | ✅ Created |
| `dynamic_evaluation_spec.md` | Heuristic fallback grader formulas and code blueprints | ✅ Created |
| `full_stack_fixes_spec.md` | 404 fix, auto-provisioning, safe grade extraction spec | ✅ Created |
| `python_environment_prompt.md` | Troubleshooting guide for interpreter and package issues | ✅ Created |
| `implementation_plan.md` | This file — complete implementation overview | ✅ Created |

## Architecture Changes Applied

### 1. Backend: Safe Grade Extraction (`main.py`)
- Replaced `grades["score_tech"]` with `_safe_grades()` using `.get()` with fallbacks
- Handles both flat and nested grade JSON formats
- Eliminates 500 crashes from malformed LLM responses

### 2. Backend: Session Auto-Provisioning (`main.py`)
- When `interview_id` is not found in DB, automatically creates a guest user + session with that ID
- Prevents 404 errors when the frontend sends a UUID from a page refresh
- Creates `guest@fallback.local` user transparently

### 3. Backend: Dynamic Heuristic Grader (`llm_service.py`)
- `execute_local_heuristic_grader()` analyzes transcripts by keyword matching (8 domain keyword maps), WPM-based communication scoring, and architectural term relevance
- Falls back through: Groq → Gemini → heuristic grader
- Generates contextual feedback citing matched/missing keywords and pacing advice

### 4. Frontend: Removed Mock Fallback (`InterviewConsole.jsx`)
- Removed `catch` block that generated `Math.random()` mock scores
- Now shows real server error instead of silently faking data
- Raises error if `interviewId` is missing instead of generating random UUID

### 5. Frontend: Improved Error Handling (`PortalView.jsx`)
- Removed silent navigation to broken interview state on API failure
- Shows clear "Backend unreachable" message instead

## Verification Steps

1. Run `verify_system.bat` or `verify_system.py` to test all components
2. Start backend: `../../.venv/Scripts/uvicorn app.main:app --reload --port 8000` (from `backend/`)
3. Start frontend: `npm run dev` (from `frontend/`)
4. Open `http://localhost:5173` (or port shown in terminal)
5. Upload a PDF resume to start an interview
6. Submit answers and verify grades appear
