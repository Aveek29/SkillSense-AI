#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# ANSI colors for rich console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_step(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== [STEP] {title} ==={Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}[!] {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}[X] {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"[INFO] {msg}")

def check_python_version():
    print_step("Checking System Python Version")
    version = sys.version_info
    print_info(f"Active System Python: {platform.python_version()} ({sys.executable})")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("SkillSense AI requires Python 3.8 or higher.")
        sys.exit(1)
    print_success("Python version is compatible.")

def setup_virtual_environment():
    print_step("Configuring Virtual Environment (venv)")

    root_dir = Path(__file__).parent.parent.resolve()
    venv_paths = [
        root_dir / "backend" / ".venv",
        root_dir / ".venv",
        root_dir / "venv",
    ]

    active_venv = None
    for vp in venv_paths:
        if vp.exists() and (vp / "Scripts" / "python.exe").exists():
            active_venv = vp
            break

    if active_venv:
        print_success(f"Existing virtual environment found at: {active_venv}")
    else:
        active_venv = root_dir / "backend" / ".venv"
        print_info(f"No active virtual environment found. Creating one at: {active_venv}")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(active_venv)], check=True)
            print_success("Virtual environment created successfully.")
        except Exception as e:
            print_error(f"Failed to create virtual environment: {e}")
            sys.exit(1)

    is_windows = platform.system() == "Windows"
    if is_windows:
        venv_python = active_venv / "Scripts" / "python.exe"
        venv_pip = active_venv / "Scripts" / "pip.exe"
    else:
        venv_python = active_venv / "bin" / "python"
        venv_pip = active_venv / "bin" / "pip"

    if not venv_python.exists():
        print_error(f"Virtual environment python executable not found at {venv_python}")
        sys.exit(1)

    return venv_python, venv_pip, active_venv

def upgrade_pip_and_tools(venv_python):
    print_step("Upgrading core packaging libraries (pip, setuptools, wheel)")
    try:
        subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
        print_success("Successfully upgraded pip, setuptools, and wheel.")
    except Exception as e:
        print_warning(f"Could not upgrade pip/setuptools/wheel automatically: {e}. Attempting package installation anyway.")

def install_dependencies(venv_python, venv_pip):
    print_step("Installing Package Dependencies")
    root_dir = Path(__file__).parent.parent.resolve()
    req_file = root_dir / "backend" / "requirements.txt"

    if not req_file.exists():
        print_error(f"Could not find backend requirements.txt at: {req_file}")
        sys.exit(1)

    print_info(f"Installing requirements from {req_file}...")
    try:
        subprocess.run([str(venv_pip), "install", "-r", str(req_file)], check=True)
        print_success("Dependencies installed successfully.")
    except Exception as e:
        print_error(f"Error occurred during pip install: {e}")
        print_info("Retrying installation with --prefer-binary flag to prevent C-compilation issues on Windows...")
        try:
            subprocess.run([str(venv_pip), "install", "--prefer-binary", "-r", str(req_file)], check=True)
            print_success("Dependencies installed successfully on fallback.")
        except Exception as e2:
            print_error(f"Fallback installation failed: {e2}")
            print_warning("Please review requirements.txt and resolve any compiler issues (e.g. installing Visual Studio C++ Build Tools).")
            sys.exit(1)

def download_spacy_model(venv_python):
    print_step("Downloading spaCy NLP Language Model (en_core_web_sm)")
    print_info("Downloading English pipeline 'en_core_web_sm' for resume parsing...")
    try:
        subprocess.run([str(venv_python), "-m", "spacy", "download", "en_core_web_sm"], check=True)
        print_success("spaCy model downloaded successfully.")
    except Exception as e:
        print_warning(f"Could not download spaCy en_core_web_sm automatically: {e}")
        print_info("The parser will automatically fall back to standard regex-based keyword parsing if spaCy model is missing.")

def run_database_seeder(venv_python):
    print_step("Seeding the SQLite Database")
    root_dir = Path(__file__).parent.parent.resolve()
    backend_dir = root_dir / "backend"
    seeder_script = backend_dir / "database" / "seed_db.py"

    if not seeder_script.exists():
        print_warning(f"Seeder script not found at {seeder_script}. Skipping database seeding.")
        return

    print_info(f"Running database seeder: {seeder_script}...")
    try:
        subprocess.run([str(venv_python), "database/seed_db.py"], cwd=str(backend_dir), check=True)
        print_success("Local SQLite database initialized and seeded successfully.")
    except Exception as e:
        print_error(f"Failed to seed SQLite database: {e}")

def validate_python_files():
    print_step("Validating Python Code Integrity (Syntax Compile Check)")
    root_dir = Path(__file__).parent.parent.resolve()
    backend_app_dir = root_dir / "backend" / "app"

    if not backend_app_dir.exists():
        print_warning(f"Backend app folder not found at {backend_app_dir}. Skipping syntax check.")
        return

    python_files = list(backend_app_dir.glob("**/*.py"))
    print_info(f"Found {len(python_files)} python source files in app/ directory.")

    errors_found = 0
    for pf in python_files:
        try:
            with open(pf, "r", encoding="utf-8") as f:
                content = f.read()
            compile(content, str(pf), "exec")
        except SyntaxError as se:
            print_error(f"Syntax Error in {pf.relative_to(root_dir)} at line {se.lineno}: {se.msg}")
            errors_found += 1
        except Exception as e:
            print_error(f"Unable to read or compile {pf.relative_to(root_dir)}: {e}")
            errors_found += 1

    if errors_found == 0:
        print_success("All Python source code files compiled and verified with zero syntax errors!")
    else:
        print_warning(f"Completed compilation checks with {errors_found} syntax errors. Please fix these files before starting the server.")

def create_env_file():
    """Create or update .env file with recommended defaults."""
    print_step("Configuring Environment Variables (.env)")
    root_dir = Path(__file__).parent.parent.resolve()
    env_path = root_dir / "backend" / ".env"

    if env_path.exists():
        print_info(f"Existing .env found at {env_path} -- checking for missing keys...")
        with open(env_path, "r") as f:
            content = f.read()
    else:
        content = ""

    defaults = {
        "DEBUG": "False",
        "DATABASE_URL": "sqlite:///./database/skillsense_dev.db",
        "GROQ_API_KEY": "",
        "GEMINI_API_KEY": "",
    }

    added = 0
    with open(env_path, "a") as f:
        for key, val in defaults.items():
            if key not in content:
                f.write(f"\n{key}={val}")
                added += 1

    if added:
        print_success(f"Added {added} missing environment variables to .env")
    else:
        print_success("All recommended env vars already present")


def display_summary(venv_python, active_venv):
    print_step("SkillSense AI Python Environment Setup Complete!")
    print(f"\n{Colors.BOLD}{Colors.GREEN}Your virtual environment is fully configured and ready!{Colors.ENDC}")
    print(f"----------------------------------------------------------------------")
    print(f"Virtual Env Path:   {active_venv}")
    print(f"Python Interpreter: {venv_python}")
    print(f"----------------------------------------------------------------------")
    print(f"\n{Colors.BOLD}Next Steps to run the platform:{Colors.ENDC}")
    print(f"1. Open a terminal / PowerShell window.")
    print(f"2. Activate the virtual environment:")
    if platform.system() == "Windows":
        print(f"   {Colors.BLUE}cd backend{Colors.ENDC}")
        print(f"   {Colors.BLUE}.venv\\Scripts\\Activate.ps1{Colors.ENDC} (PowerShell) or {Colors.BLUE}.venv\\Scripts\\activate.bat{Colors.ENDC} (Command Prompt)")
    else:
        print(f"   {Colors.BLUE}cd backend{Colors.ENDC}")
        print(f"   {Colors.BLUE}source .venv/bin/activate{Colors.ENDC}")
    print(f"3. Run the development API Server:")
    print(f"   {Colors.BLUE}uvicorn app.main:app --reload --port 8000{Colors.ENDC}")
    print(f"----------------------------------------------------------------------")
    print(f"To configure VS Code / Cursor to use this interpreter:")
    print(f"  - Press {Colors.BOLD}Ctrl+Shift+P{Colors.ENDC}")
    print(f"  - Search for: {Colors.BOLD}Python: Select Interpreter{Colors.ENDC}")
    print(f"  - Select the one pointing to: {Colors.UNDERLINE}{venv_python}{Colors.ENDC}")
    print(f"----------------------------------------------------------------------\n")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=====================================================================")
    print("    SkillSense AI Unified Environment Setup & Diagnostics Engine")
    print("=====================================================================")
    print(f"{Colors.ENDC}")

    check_python_version()
    venv_python, venv_pip, active_venv = setup_virtual_environment()
    upgrade_pip_and_tools(venv_python)
    install_dependencies(venv_python, venv_pip)
    download_spacy_model(venv_python)
    create_env_file()
    run_database_seeder(venv_python)
    validate_python_files()
    display_summary(venv_python, active_venv)

if __name__ == "__main__":
    main()
