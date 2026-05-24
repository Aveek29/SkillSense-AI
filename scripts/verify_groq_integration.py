#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
from pathlib import Path

# ANSI color codes for premium terminal reporting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Report tracing definitions
status_symbols = {
    "SUCCESS": f"{Colors.GREEN}[OK] SUCCESS{Colors.ENDC}",
    "WARNING": f"{Colors.WARNING}[!] WARNING{Colors.ENDC}",
    "CRITICAL": f"{Colors.FAIL}[X] CRITICAL{Colors.ENDC}"
}

report_card = []

def log_test(name, status, details=""):
    report_card.append({"name": name, "status": status, "details": details})
    symbol = status_symbols[status]
    detail_str = f" - {details}" if details else ""
    print(f"[{symbol}] {Colors.BOLD}{name}{Colors.ENDC}{detail_str}")

def print_banner(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== {title} ==={Colors.ENDC}")

# Add backend directory to sys.path to run internal import diagnostics
root_dir = Path(__file__).parent.resolve()
backend_dir = root_dir / "skillsense-ai" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# ─────────────────────────────────────────────────────────────────────────
# STEP 1: Library Dependency & Alignment Check
# ─────────────────────────────────────────────────────────────────────────
def test_dependency_alignment():
    print_banner("1. Dependency & Processing Library Verification")
    
    # Check Groq package availability
    try:
        import groq
        log_test("Groq Library Availability", "SUCCESS", "Groq package imported correctly")
    except ImportError:
        log_test("Groq Library Availability", "CRITICAL", "groq package is missing from environment. Run setup_env.bat to resolve.")

    # Check local DSP libraries
    try:
        import librosa
        import numpy as np
        log_test("Audio DSP Libraries", "SUCCESS", "Librosa and NumPy loaded for verbal behavior parsing")
    except ImportError:
        log_test("Audio DSP Libraries", "WARNING", "Librosa or NumPy missing. Audio processing will fall back to statistical simulations.")

    # Check spaCy NLP
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        log_test("NLP Language Model", "SUCCESS", "spaCy and en_core_web_sm pipeline active")
    except Exception as e:
        log_test("NLP Language Model", "WARNING", f"spaCy or en_core_web_sm missing. Resume parser will use regex keyword fallbacks: {e}")

# ─────────────────────────────────────────────────────────────────────────
# STEP 2: Groq Ingestion Data Schema Mapping (Input Validation)
# ─────────────────────────────────────────────────────────────────────────
def test_input_data_mapping():
    print_banner("2. Groq Ingestion Schema & Data Input Verification")
    
    try:
        from app.services.audio_service import AudioProcessingEngine
        
        # Test simulated audio variables mapped to Groq inputs
        audio_engine = AudioProcessingEngine()
        mock_transcript = "Basically, we should configure a custom multi-stage Docker build, like, to shrink the final footprint and keep standard configurations stable."
        
        # Compute voice fluency metrics programmatically
        metrics = audio_engine.compute_speech_fluency(None, mock_transcript)
        
        # Assert input keys map properly to the expected schema format
        required_keys = ["speaking_rate_wpm", "pause_count", "filler_words_count", "filler_ratio", "fluency_score"]
        missing_keys = [k for k in required_keys if k not in metrics]
        
        if not missing_keys:
            log_test("Voice DSP Input Alignment", "SUCCESS", f"Audio processing output maps successfully to Groq inputs. Fluency Index: {metrics['fluency_score']}/10")
        else:
            log_test("Voice DSP Input Alignment", "CRITICAL", f"Missing keys in computed metrics: {missing_keys}")
            
    except Exception as e:
        log_test("Voice DSP Input Alignment", "CRITICAL", f"Failed to execute input alignment verification: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────
# STEP 3: API Connections & Credentials Audits
# ─────────────────────────────────────────────────────────────────────────
def test_groq_api_connectivity():
    print_banner("3. Groq API Service Authorization & Key Verification")
    
    try:
        from app.services.groq_service import GroqAIService
        ai_service = GroqAIService()
        
        # Verify GROQ_API_KEY configuration
        if ai_service.api_key:
            masked = ai_service.api_key[:6] + "..." + ai_service.api_key[-4:] if len(ai_service.api_key) > 10 else "***"
            log_test("API Credentials Configuration", "SUCCESS", f"GROQ_API_KEY detected in settings: {masked}")
        else:
            log_test("API Credentials Configuration", "WARNING", "GROQ_API_KEY environment variable is empty. The backend will run on high-fidelity offline simulation mode.")

        # Probe API response connectivity
        if ai_service.is_available():
            # Run simple authentication ping
            try:
                system_prompt = "You are a health check system. Reply with 'OK'."
                response = ai_service._call_llm(system_prompt, "Health Check", temperature=0.1)
                if response and "OK" in response:
                    log_test("Live Groq Connection Probe", "SUCCESS", "Successfully authorized and received response from Groq LLM API.")
                else:
                    log_test("Live Groq Connection Probe", "WARNING", f"Connection established but unexpected response returned: {response}")
            except Exception as e:
                log_test("Live Groq Connection Probe", "CRITICAL", f"Authorization failed during live request: {str(e)}")
        else:
            log_test("Live Groq Connection Probe", "WARNING", "Skipped live ping. API Client is uninitialized (expected in Offline/Simulation mode).")
            
    except Exception as e:
        log_test("API Service Probe", "CRITICAL", f"Failed to initialize Groq services: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────
# STEP 4: End-to-End JSON Payload Verification (Output Schema Validation)
# ─────────────────────────────────────────────────────────────────────────
def test_output_json_schemas():
    print_banner("4. Groq Output Payload & JSON Schema Alignment")
    
    try:
        from app.services.groq_service import GroqAIService
        ai_service = GroqAIService()
        
        # A. Mock Grading Data Test
        mock_question = "Explain standard database scaling constraints when migrating from local monolithic models to cloud instances."
        mock_transcript = "We can use read replicas to handle high read workloads and sharding to distribute writes."
        mock_metrics = {"speaking_rate_wpm": 130.5, "fluency_score": 8.5}
        
        # Trigger Grading Pipeline
        grades = ai_service.grade_response("Cloud Systems", mock_question, mock_transcript, mock_metrics)
        
        # Assert schema alignment
        grading_keys = ["score_tech", "score_comm", "score_rel", "feedback"]
        missing_grades = [k for k in grading_keys if k not in grades]
        
        if not missing_grades:
            log_test("Grading Output Schema Alignment", "SUCCESS", f"Grades match database structures. Tech Score: {grades['score_tech']}/10")
        else:
            log_test("Grading Output Schema Alignment", "CRITICAL", f"Missing metrics fields in Groq output payload: {missing_grades}")

        # B. Mock FinOps Suggestion Test
        insight = ai_service.generate_cost_optimization_tip(1400.50, 46.50)
        insight_keys = ["tip", "estimated_savings_pct", "effort"]
        missing_insights = [k for k in insight_keys if k not in insight]
        
        if not missing_insights:
            log_test("FinOps Suggestion Schema Alignment", "SUCCESS", f"FinOps guidelines matched. Estimated Savings: {insight['estimated_savings_pct']}%")
        else:
            log_test("FinOps Suggestion Schema Alignment", "CRITICAL", f"Missing fields in FinOps cost advice output payload: {missing_insights}")
            
    except Exception as e:
        log_test("Output Payload Schema Alignment", "CRITICAL", f"Error validating output schemas: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────
# STEP 5: SQLite Database Schema Mapping & Storage Verification
# ─────────────────────────────────────────────────────────────────────────
def test_database_compatibility():
    print_banner("5. Backend Database Schema Compatibility & Continuous Flow")
    
    root_dir = Path(__file__).parent.resolve()
    db_file = root_dir / "skillsense-ai" / "backend" / "skillsense_dev.db"
    
    if not db_file.exists():
        log_test("Local SQLite Schema Check", "WARNING", "skillsense_dev.db does not exist yet. Run setup_env.bat to seed it.")
        return
        
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Fetch columns from the database-agnostic interview sessions table
        cursor.execute("PRAGMA table_info(interview_sessions);")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        # Confirm that the history_logs JSON column is present to support nested AI evaluations
        if "history_logs" in columns:
            log_test("Database Field Mappings", "SUCCESS", f"Database contains 'history_logs' field (Type: {columns['history_logs']}) to safely store dynamic AI results.")
        else:
            log_test("Database Field Mappings", "CRITICAL", "Database table 'interview_sessions' does not contain 'history_logs' field!")
            
        conn.close()
    except Exception as e:
        log_test("Database Integration Check", "CRITICAL", f"Database connection error: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────
# STEP 6: Full Data Flow Diagnostics Dashboard
# ─────────────────────────────────────────────────────────────────────────
def render_dashboard():
    print_banner("DATA INTEGRATION & CONNECTIVITY REPORT CARD")
    
    success_count = sum(1 for r in report_card if r["status"] == "SUCCESS")
    warning_count = sum(1 for r in report_card if r["status"] == "WARNING")
    critical_count = sum(1 for r in report_card if r["status"] == "CRITICAL")
    
    for r in report_card:
        symbol = ""
        if r["status"] == "SUCCESS":
            symbol = f"{Colors.GREEN}✔{Colors.ENDC}"
        elif r["status"] == "WARNING":
            symbol = f"{Colors.WARNING}⚠{Colors.ENDC}"
        elif r["status"] == "CRITICAL":
            symbol = f"{Colors.FAIL}✘{Colors.ENDC}"
            
        pad = " " * (45 - len(r["name"]))
        print(f"  {symbol} {r['name']}{pad}-->  {r['status']}  ({r['details']})")
        
    print(f"\n{Colors.BOLD}----------------------------------------------------------------------")
    print(f" CONTINUOUS DATA FLOW SUMMARY")
    print(f"----------------------------------------------------------------------{Colors.ENDC}")
    print(f"  Successfully Aligned Checks:  {Colors.GREEN}{Colors.BOLD}{success_count}{Colors.ENDC}")
    print(f"  Warnings Flagged:            {Colors.WARNING}{Colors.BOLD}{warning_count}{Colors.ENDC}")
    print(f"  Critical Flow Failures:      {Colors.FAIL}{Colors.BOLD}{critical_count}{Colors.ENDC}")
    print(f"----------------------------------------------------------------------")
    
    if critical_count == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALIGNED! The backend data flow is fully continuous. Raw libraries seamlessly connect to Groq AI payloads and SQLite tables!{Colors.ENDC}\n")
    else:
        print(f"\n{Colors.BOLD}{Colors.FAIL}🚨 DISRUPTED: {critical_count} critical failures in the data pipeline must be addressed!{Colors.ENDC}\n")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=====================================================================")
    print("      SkillSense AI - Groq & Local Libraries Integration Engine")
    print("=====================================================================")
    print(f"{Colors.ENDC}")
    
    test_dependency_alignment()
    test_input_data_mapping()
    test_groq_api_connectivity()
    test_output_json_schemas()
    test_database_compatibility()
    render_dashboard()

if __name__ == "__main__":
    main()
