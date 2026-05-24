@echo off
title SkillSense AI Setup & Diagnostics Engine
echo =====================================================================
echo    SkillSense AI Unified Environment Setup ^& Diagnostics Engine
echo =====================================================================
echo.
echo Searching for system Python installation...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo and ensure you check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found! Launching setup_and_fix.py...
echo.
python setup_and_fix.py

echo.
echo =====================================================================
echo Setup script execution has completed.
echo =====================================================================
echo.
pause
