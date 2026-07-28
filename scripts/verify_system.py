#!/usr/bin/env python3
"""
SkillSense AI - System Verification & Diagnostics Engine
========================================================
Verifies all backend services, database connectivity, API routes,
frontend config, and external API credential readiness.
"""
import os
import sys
import json
import platform
import subprocess
import importlib
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
VENV_DIR = BACKEND_DIR / ".venv"
FRONTEND_DIR = ROOT_DIR / "frontend"

# Re-run under the correct venv if currently running outside it
_venv_python = None
for _vp in [BACKEND_DIR / ".venv", ROOT_DIR / ".venv", ROOT_DIR / "venv"]:
    _py = _vp / "Scripts" / "python.exe"
    if _py.exists():
        _venv_python = _py
        break
if _venv_python and Path(sys.executable).resolve() != _venv_python.resolve():
    import subprocess as _sp
    sys.exit(_sp.run([str(_venv_python), __file__] + sys.argv[1:]).returncode)

os.chdir(str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "app"))

# Suppress SQLAlchemy engine debug logging during verification
import logging as _logging
_logging.getLogger("sqlalchemy.engine").setLevel(_logging.WARNING)
_logging.getLogger("sqlalchemy.pool").setLevel(_logging.WARNING)
os.environ["DEBUG"] = "False"


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.ENDC}")


def check(label, status, detail=""):
    icon = f"{Colors.GREEN}[PASS]{Colors.ENDC}" if status else f"{Colors.FAIL}[FAIL]{Colors.ENDC}"
    print(f"  {icon}  {label}")
    if detail:
        print(f"         {detail}")


def warn(label, detail=""):
    print(f"  {Colors.WARNING}[WARN]{Colors.ENDC}  {label}")
    if detail:
        print(f"         {detail}")


def main():
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("="*60)
    print("  SkillSense AI - System Verification & Diagnostics Engine")
    print("="*60)
    print(f"{Colors.ENDC}")
    print(f"  Platform    : {platform.system()} {platform.release()}")
    print(f"  Python      : {sys.version.split()[0]}")
    print(f"  Root        : {ROOT_DIR}")
    print()

    # ── 1. Virtual Environment & Dependencies ──────────────────────
    section("1. Virtual Environment & Dependencies")

    venv_python = None
    for candidate in [BACKEND_DIR / ".venv", ROOT_DIR / ".venv", ROOT_DIR / "venv"]:
        py = candidate / "Scripts" / "python.exe"
        if py.exists():
            venv_python = py
            check(f"Active venv found: {candidate.relative_to(ROOT_DIR)}", True)
            break

    if not venv_python:
        check("Active virtual environment", False, "No .venv or venv found")
    else:
        try:
            result = subprocess.run([str(venv_python), "-m", "pip", "list", "--format=json"],
                                    capture_output=True, text=True, timeout=30)
            pkgs = json.loads(result.stdout)
            pkg_names = {p["name"].lower() for p in pkgs}
            required = ["fastapi", "uvicorn", "sqlalchemy", "spacy", "pydantic",
                        "pandas", "numpy", "scipy", "scikit-learn", "prophet",
                        "librosa", "boto3", "pymupdf", "cryptography", "passlib",
                        "python-jose", "pytest"]
            missing = [r for r in required if r not in pkg_names]
            if missing:
                check("Core dependencies installed", False, f"Missing: {', '.join(missing)}")
            else:
                check("Core dependencies installed", True, f"{len(pkgs)} total packages")
        except Exception as e:
            check("Package check", False, str(e))

    # ── 2. Backend Module Imports ─────────────────────────────────
    section("2. Backend Module Imports")

    modules = [
        ("app.core.config", ["get_settings", "Settings"]),
        ("app.core.database", ["engine", "SessionLocal"]),
        ("app.core.auth", ["hash_password", "verify_password", "create_access_token", "get_current_user", "get_optional_user"]),
        ("app.models.tables", ["Base", "DBUser", "DBInterviewSession", "DBSandboxResource", "DBSandboxMetric"]),
        ("app.services.parser_service", ["EnterpriseResumeParser"]),
        ("app.services.audio_service", ["AudioProcessingEngine"]),
        ("app.services.llm_service", ["LLMOrchestratorService"]),
        ("app.services.sandbox_service", ["SandboxProvisionerService"]),
        ("app.services.forecasting_service", ["FinOpsForecaster"]),
        ("app.services.anomaly_service", ["CloudResourceAnomalyDetector"]),
    ]

    for mod_path, symbols in modules:
        try:
            mod = importlib.import_module(mod_path)
            for sym in symbols:
                assert hasattr(mod, sym), f"{mod_path} missing {sym}"
            check(f"{mod_path} ({len(symbols)} symbols)", True)
        except Exception as e:
            check(f"{mod_path}", False, str(e))

    # ── 3. Service Functionality Tests ─────────────────────────────
    section("3. Service Functionality Tests")

    # Parser
    try:
        from app.services.parser_service import EnterpriseResumeParser
        parser = EnterpriseResumeParser()
        result = parser.parse_resume_document(b"%%PDF mock - Alice, alice@test.com, Python, AWS, Docker")
        skills = result["candidate_skills"]
        check("Resume Parser - skill extraction", True, f"found {len(skills)} skills: {skills[:4]}")
    except Exception as e:
        check("Resume Parser", False, str(e))

    # Audio
    try:
        from app.services.audio_service import AudioProcessingEngine
        audio = AudioProcessingEngine()
        result = audio.compute_speech_fluency("nonexistent.wav",
                                              "This is a sample candidate response for testing.")
        check("Audio Service - fluency metrics", True,
              f"WPM={result['speaking_rate_wpm']}, score={result['fluency_score']}")
    except Exception as e:
        check("Audio Service", False, str(e))

    # LLM (fallback)
    try:
        from app.services.llm_service import LLMOrchestratorService
        llm = LLMOrchestratorService()
        q = llm.generate_next_question("Cloud DevOps", ["Docker", "K8s", "AWS"], [])
        check("LLM Service - question generation (fallback)", True,
              f"difficulty={q['difficulty']}")
    except Exception as e:
        check("LLM Service", False, str(e))

    # Sandbox (mock mode)
    try:
        from app.services.sandbox_service import SandboxProvisionerService
        sandbox = SandboxProvisionerService()
        s_result = sandbox.provision_developer_sandbox("u-1", "i-1")
        check("Sandbox Service - provisioning (mock)", True,
              f"resource_id={s_result['resource_id']}")
        t_result = sandbox.terminate_developer_sandbox(s_result["resource_id"])
        check("Sandbox Service - termination (mock)", True)
    except Exception as e:
        check("Sandbox Service", False, str(e))

    # Forecasting
    try:
        from app.services.forecasting_service import FinOpsForecaster
        from datetime import datetime, timedelta
        forecaster = FinOpsForecaster(forecast_days=7)
        sample = [
            {"timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
             "daily_cost": round(2.0 + i * 0.1, 2)}
            for i in range(20, 0, -1)
        ]
        f_result = forecaster.generate_expenditure_predictions(sample)
        check("Forecasting Service - Prophet/time-series", True,
              f"aggregate=${f_result['forecasted_aggregate_spend']}")
    except Exception as e:
        check("Forecasting Service", False, str(e))

    # Anomaly Detection
    try:
        from app.services.anomaly_service import CloudResourceAnomalyDetector
        detector = CloudResourceAnomalyDetector()
        metrics = [
            {"cpu_utilization": 30 + i * 2, "ram_utilization": 40 + i,
             "network_egress_bytes": 100000, "daily_cost": 2.5}
            for i in range(15)
        ]
        a_result = detector.evaluate_resource_telemetry(metrics)
        anomalies = sum(1 for m in a_result if m.get("is_anomaly"))
        check("Anomaly Detector - Isolation Forest/rule-based", True,
              f"{len(a_result)} items, {anomalies} anomalies flagged")
    except Exception as e:
        check("Anomaly Detector", False, str(e))

    # ── 4. Database Connectivity ──────────────────────────────────
    section("4. Database Connectivity & Seeding")

    try:
        from app.core.database import SessionLocal
        from app.models.tables import DBUser, DBInterviewSession, DBSandboxResource, DBSandboxMetric
        db = SessionLocal()
        user_count = db.query(DBUser).count()
        session_count = db.query(DBInterviewSession).count()
        sandbox_count = db.query(DBSandboxResource).count()
        metric_count = db.query(DBSandboxMetric).count()
        bad_sessions = db.query(DBInterviewSession).filter(DBInterviewSession.history_logs.is_(None)).count()
        if bad_sessions:
            warn(f"{bad_sessions} sessions have NULL history_logs", "Run: python database/seed_db.py")
        db.close()
        check("SQLite connection", True, f"DB: database/skillsense_dev.db")
        check("Users table", True, f"{user_count} records")
        check("Sessions table", True, f"{session_count} records")
        check("Sandbox Resources table", True, f"{sandbox_count} records")
        check("Sandbox Metrics table", True, f"{metric_count} records")
    except Exception as e:
        check("Database connectivity", False, str(e))

    # ── 5. FastAPI Application & Routes ────────────────────────────
    section("5. FastAPI Application & Routes")

    try:
        from app.main import app
        routes = [r for r in app.routes if hasattr(r, "path") and r.path.startswith("/api")]
        check(f"FastAPI app loaded", True, f"{len(routes)} API routes registered")
        for r in routes:
            methods = ", ".join(r.methods) if hasattr(r, "methods") else "GET"
            print(f"         {methods:8s} {r.path}")
    except Exception as e:
        check("FastAPI app", False, str(e))

    # ── 6. Frontend Configuration ──────────────────────────────────
    section("6. Frontend Configuration")

    if FRONTEND_DIR.exists():
        check("Frontend directory exists", True)

        pkg_json = FRONTEND_DIR / "package.json"
        if pkg_json.exists():
            try:
                with open(pkg_json) as f:
                    pkg = json.load(f)
                deps = list(pkg.get("dependencies", {}).keys())
                dev_deps = list(pkg.get("devDependencies", {}).keys())
                check("package.json loaded", True, f"{len(deps)} deps, {len(dev_deps)} devDeps")
            except Exception as e:
                check("package.json", False, str(e))
        else:
            check("package.json", False)

        vite_config = FRONTEND_DIR / "vite.config.js"
        if vite_config.exists():
            try:
                with open(vite_config) as f:
                    content = f.read()
                if "proxy" in content and "localhost:8000" in content:
                    check("Vite proxy config", True, "API proxy -> localhost:8000")
                else:
                    warn("Vite proxy config", "No proxy to backend found")
            except Exception as e:
                check("vite.config.js", False, str(e))
        else:
            check("vite.config.js", False)

        node_modules = FRONTEND_DIR / "node_modules"
        if node_modules.exists():
            check("node_modules installed", True)
        else:
            warn("node_modules not installed", "Run: cd frontend && npm install")

    else:
        check("Frontend directory", False)

    # ── 7. External API Credentials ────────────────────────────────
    section("7. External API Credential Status")

    # Load .env file into process env for credential detection
    env_file = BACKEND_DIR / ".env"
    if env_file.exists():
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except Exception:
            pass

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    aws_key = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    if groq_key:
        check("GROQ_API_KEY", True, "[set] - Groq AI grading, monitoring & insights enabled")
    elif gemini_key:
        check("GEMINI_API_KEY", True, "[set] - LLM grading & question gen enabled")
    else:
        warn("GROQ_API_KEY not set", "LLM will use fallback mock responses (set GROQ_API_KEY in .env)")

    if openai_key:
        check("OPENAI_API_KEY", True, "[set]")
    else:
        warn("OPENAI_API_KEY not set", "Optional - not used by default")

    if aws_key and aws_secret:
        check("AWS credentials", True, "[set] - EC2 sandbox provisioning enabled")
    else:
        warn("AWS credentials not set", "Sandbox will use mock provisioning")

    # ── 8. Syntax Integrity ────────────────────────────────────────
    section("8. Python Syntax Integrity Check")

    py_files = list(BACKEND_DIR.rglob("*.py"))
    py_files = [f for f in py_files if "venv" not in str(f) and "__pycache__" not in str(f)]
    errors = 0
    for pf in py_files:
        try:
            with open(pf, "r", encoding="utf-8") as f:
                compile(f.read(), str(pf), "exec")
        except SyntaxError as se:
            print(f"  {Colors.FAIL}[ERR]{Colors.ENDC}  {pf.relative_to(ROOT_DIR)} L{se.lineno}: {se.msg}")
            errors += 1

    if errors == 0:
        check(f"All {len(py_files)} Python files", True, "0 syntax errors")
    else:
        check("Python syntax check", False, f"{errors} files with errors")

    # ── SUMMARY ────────────────────────────────────────────────────
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}")
    print("  SYSTEM VERIFICATION COMPLETE")
    print(f"{'='*60}{Colors.ENDC}")
    print()
    print(f"  Backend server: cd backend && uvicorn app.main:app --reload --port 8000")
    print(f"  Frontend dev  : cd frontend && npm run dev")
    print(f"  VS Code       : Ctrl+Shift+P -> Python: Select Interpreter")
    print()


if __name__ == "__main__":
    main()
