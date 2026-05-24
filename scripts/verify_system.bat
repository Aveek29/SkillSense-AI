@echo off
title SkillSense AI - System Verification Engine
echo =====================================================================
echo    SkillSense AI - System Verification ^& Diagnostics Engine
echo =====================================================================
echo.

REM Try backend .venv first, then root alternatives, then system python
if exist "skillsense-ai\backend\.venv\Scripts\python.exe" (
    echo [INFO] Using backend/.venv interpreter...
    skillsense-ai\backend\.venv\Scripts\python.exe verify_system.py
    goto :done
)

if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using root .venv interpreter...
    .venv\Scripts\python.exe verify_system.py
    goto :done
)

if exist "skillsense-ai\backend\venv\Scripts\python.exe" (
    echo [INFO] Using backend/venv interpreter...
    skillsense-ai\backend\venv\Scripts\python.exe verify_system.py
    goto :done
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Using system Python interpreter...
    python verify_system.py
    goto :done
)

echo [ERROR] No Python interpreter found.
echo Please install Python 3.8+ from https://www.python.org/downloads/
echo and ensure you check "Add Python to PATH" during installation.

:done
echo.
echo =====================================================================
echo Verification script execution has completed.
echo =====================================================================
echo.
pause
