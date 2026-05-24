# Python Environment Setup & Troubleshooting Master Prompt

This document contains a **Master Troubleshooting Prompt** and **Step-by-Step Editor Guide** that you can copy and paste into any AI model or IDE assistant to quickly resolve Python package conflicts, virtual environment (venv) problems, and interpreter path errors.

---

## 1. Copy-Pasteable AI Prompt

Copy the text block below and send it to your AI coding assistant to diagnose, debug, or solve specific Python issues:

```text
I am working on the "SkillSense AI" project, a Unified Interview Assessment and Cloud Cost Optimization platform. I need help troubleshooting and resolving Python environment, interpreter, or dependency issues. 

Here are the system specifications:
- Project Location: e:\SkillSense AI\skillsense-ai
- Backend Framework: FastAPI
- Core Backend Dependencies: fastapi, uvicorn, pydantic, sqlalchemy, scikit-learn, prophet, spacy, librosa, boto3
- Database: SQLite (local dev) or PostgreSQL

Please analyze and provide the exact steps to resolve the following issue:
[INSERT YOUR SPECIFIC ERROR MESSAGE OR DESCRIPTION HERE]

In your response, please cover:
1. Exact command-line or shell steps to resolve it in PowerShell/cmd on Windows.
2. How to verify that the virtual environment (venv) is active and using the correct path.
3. How to check for and fix package conflicts (e.g., conflicting pydantic, numpy, or scikit-learn versions).
4. The exact settings to check in my editor (VS Code, PyCharm, or Cursor) to clear red squiggly import errors.
```

---

## 2. Step-by-Step IDE Interpreter Integration Guide

Often, red squiggly lines or `ImportError` occur because the code editor is not pointing to the correct Python virtual environment (`.venv` or `venv`). Follow these simple steps to configure your editor:

### A. For VS Code / Cursor
1. Open your workspace folder: `e:\SkillSense AI`.
2. Open the Command Palette: Press `Ctrl + Shift + P`.
3. Search for and select: **`Python: Select Interpreter`**.
4. You will see a list of detected Python installations:
   - Select the one associated with your virtual environment, typically labeled:
     `Python 3.x.x ('.venv': venv) - .\venv\Scripts\python.exe` or `.\.venv\Scripts\python.exe`.
   - If it is not listed, click **`Enter interpreter path...`**, then **`Find...`** and navigate to:
     `e:\SkillSense AI\skillsense-ai\backend\venv\Scripts\python.exe` (or your root virtual environment path).
5. Open a new terminal in VS Code (`Ctrl + ~`), and it will automatically activate the virtual environment!

### B. For JetBrains PyCharm
1. Open PyCharm and load the project folder `e:\SkillSense AI`.
2. Go to **Settings** (`Ctrl + Alt + S`) -> **Project: SkillSense AI** -> **Python Interpreter**.
3. Click the gear icon / dropdown in the top-right and select **Add Interpreter** -> **Local...**.
4. Select **Existing Environment**.
5. Click the `...` button and browse to:
   `e:\SkillSense AI\skillsense-ai\backend\venv\Scripts\python.exe` (or `e:\SkillSense AI\.venv\Scripts\python.exe`).
6. Click **OK** and **Apply**. PyCharm will index the virtual environment, clearing all unresolved import warnings.

---

## 3. Recommended Manual Diagnostic Commands

If you choose to run diagnostic commands in your terminal, here are the safest and most effective Windows commands:

| Task | PowerShell / Command Prompt |
| :--- | :--- |
| **Verify active Python path** | `where.exe python` |
| **Verify active Python version** | `python --version` |
| **Check installed pip packages** | `pip list` |
| **Check for package dependency issues** | `pip check` |
| **Download the required spaCy model** | `python -m spacy download en_core_web_sm` |
| **Manually seed the SQLite database** | `python skillsense-ai/backend/database/seed_db.py` |
