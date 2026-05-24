# SkillSense AI: Dynamic Evaluation & Intelligent Fallback Implementation Specification

This document provides the complete structural analysis, architectural mapping, and code blueprints to replace the static dummy responses with a highly dynamic, context-aware local heuristic evaluation engine. 

---

## 1. Root Cause & Behavioral Analysis

### A. The Observed Issue (Screenshot Breakdown)
As shown in the console screenshot for **Question 2 (Hard)**: *"How would you design a microservices event bus for real-time data streaming?"*:
* The candidate's response transcript was submitted.
* The frontend displayed mock scores (**9.3 Technical, 9.0 Communication, 6.6 Relevance**) and a hardcoded feedback string.
* **Why did this happen?**
  1. The external Groq/Gemini API calls either timed out, failed auth, or returned an unexpected nested JSON format.
  2. The backend `main.py` contains a critical indexing vulnerability where it accesses `grades["score_tech"]` directly. If the API fails or returns a nested JSON schema (e.g., `{"grades": {"score_tech": ...}}`), a `KeyError` is raised, crashing the API route with a **500 Internal Server Error**.
  3. The React frontend catch block in `InterviewConsole.jsx` intercepted this failure and triggered its own internal mock generator, returning random scores and the static string: *"Good architectural understanding demonstrated..."*.

```
[Candidate Submission] ──> [FastAPI Submit Endpoint] ──> [External LLM API (Groq/Gemini)]
                                                                    │
                                                           (API Fails / Key Schema Mismatch)
                                                                    │
                                                                    ▼
[React Mock Fallback]  <──  [Crashes with 500 error]  <──  [Backend KeyError in main.py]
 (Dummy Scores & Text)
```

### B. The Target Solution
To make the fallback completely dynamic and intelligent (so it never returns static dummy responses even in offline/simulation mode), we establish an **Intelligent Local Heuristic Grader** that analyzes candidate transcripts dynamically based on custom keywords, speaking rates (WPM), and voice metrics.

---

## 2. Dynamic Grading Dictionary & Taxonomy Mapping

The heuristic grader operates on a predefined matrix matching each assessment question to technical keywords, weights, and domain concepts:

| Question Reference | Expected Domain Keywords | Minimum Baseline | Technical Difficulty |
| :--- | :--- | :--- | :--- |
| **Q1: Database Scaling** | `horizontal scale`, `sharding`, `replicas`, `pooling`, `monolithic`, `migration` | 2 keywords | Medium |
| **Q2: Microservices Event Bus** | `Kafka`, `event-driven`, `pub/sub`, `throughput`, `partitions`, `consumer`, `broker` | 2 keywords | Hard |
| **Q3: Kubernetes Orchestration** | `pods`, `services`, `ingress`, `HPA`, `scaling`, `container`, `yaml`, `docker` | 2 keywords | Medium |
| **Q4: CI/CD Pipelines** | `GitHub Actions`, `Docker`, `canary`, `blue-green`, `deployment`, `testing`, `automation` | 2 keywords | Hard |
| **Q5: Isolation Forest** | `path length`, `contamination`, `unsupervised`, `telemetry`, `outlier`, `anomaly`, `trees` | 2 keywords | Medium |

---

## 3. Heuristic Evaluation Formulas & Feedback Trees

When external APIs are uninitialized or offline, the local grader evaluates transcripts using these mathematical scoring parameters:

### A. Technical Score (`score_tech`)
* **Base Score**: `4.5` (if transcript length is greater than 10 words).
* **Keyword Match Credit**: Add `1.5` points for each unique domain keyword mentioned in the transcript.
* **Length Penalty**: If transcript length is less than 10 words, technical score is capped between `2.0` and `4.0` (considered a non-response).
* **Maximum Cap**: `10.0`.

$$\text{Technical Score} = \min\left(10.0, 4.5 + (1.5 \times \text{Matched KeywordsCount})\right)$$

### B. Communication Score (`score_comm`)
* Graded out of `10.0` based on acoustic metrics from local DSP analysis (WPM and pauses):
  - **Optimal Speaking Speed**: If WPM is between `110.0` and `150.0`, baseline is set to `9.0`.
  - **Pacing Penalty**: If WPM is rapid (`>150.0`) or slow (`<110.0`), apply penalty:
    $$\text{comm\_score} = 9.0 - \left(0.04 \times \lvert 130.0 - \text{WPM}\rvert\right)$$
  - **Fluency Adjuster**: Add `0.1` for each decimal increment of voice fluency index.

### C. Relevance Score (`score_rel`)
* Baseline score: `5.0`.
* Add `1.2` points for each unique domain keyword.
* Add `0.5` points for each unique general architectural term matched (e.g. *scale, design, performance, reliability, deployment, latency*).
* Capped at `10.0`.

---

## 4. Architectural Code Blueprints (Implementation Plan)

Below are the exact code replacements designed to fix this issue cleanly. **Do not apply these files directly to the codebase yet; use these blueprints as the definitive implementation reference.**

### A. Backend Route Safeguard (`backend/app/main.py`)
Replace the direct indexing in the `submit-answer` endpoint with secure `.get()` and fallback logic to guarantee zero 500 crashes:

```python
# SECURE JSONB HISTORY COLUMN WRITING IN main.py
grades = llm_orchestrator.grade_response(session.domain, question_text, transcript, metrics)

# Safe dictionary parsing with structural key fallbacks
score_tech = grades.get("score_tech") or grades.get("grades", {}).get("score_tech", 7.0)
score_comm = grades.get("score_comm") or grades.get("grades", {}).get("score_comm", 7.5)
score_rel = grades.get("score_rel") or grades.get("grades", {}).get("score_rel", 7.0)
feedback = grades.get("feedback") or grades.get("grades", {}).get("feedback", "Good technical analysis.")

logs.append({
    "question_number": entry_number,
    "question": question_text,
    "transcript": transcript,
    "speech_metrics": {
        "audio_duration_sec": metrics.get("audio_duration_sec", 0.0),
        "speaking_rate_wpm": metrics.get("speaking_rate_wpm", 0.0),
        "pause_count": metrics.get("pause_count", 0),
        "filler_words_count": metrics.get("filler_words_count", 0),
        "filler_ratio": metrics.get("filler_ratio", 0.0),
        "fluency_score": metrics.get("fluency_score", 0.0),
    },
    "grades": {
        "score_tech": round(float(score_tech), 1),
        "score_comm": round(float(score_comm), 1),
        "score_rel": round(float(score_rel), 1),
        "feedback": feedback,
    }
})
```

### B. Dynamic Heuristic Grader Core (`backend/app/services/llm_service.py`)
Add this dynamic local evaluator to `llm_service.py` to calculate custom evaluations based on candidate input instead of returning a static string:

```python
# INTELLIGENT HEURISTIC FALLBACK GRADER
def execute_local_heuristic_grader(self, question: str, transcript: str, metrics: dict) -> dict:
    """Computes dynamic, highly relevant grades and feedback based on transcript keywords and pacing."""
    text = transcript.lower()
    words = text.split()
    wpm = metrics.get("speaking_rate_wpm", 130.0)
    fluency = metrics.get("fluency_score", 8.0)
    
    # 1. Custom Keywords Mapping
    question_keywords = {
        "scaling": ["horizontal", "sharding", "replica", "monolithic", "pooling", "migration"],
        "microservices": ["kafka", "event", "bus", "streaming", "pub", "sub", "broker", "partition", "consumer"],
        "kubernetes": ["pod", "service", "ingress", "hpa", "container", "yaml", "docker", "orchestration"],
        "pipeline": ["github", "action", "docker", "canary", "blue", "green", "deploy", "ci", "cd", "test"],
        "forest": ["path", "length", "contamination", "unsupervised", "outlier", "anomaly", "telemetry", "tree"]
    }
    
    # 2. Match relevant keyword patterns
    matched_q = "scaling"
    for k in question_keywords.keys():
        if k in question.lower():
            matched_q = k
            break
            
    target_kws = question_keywords[matched_q]
    matched_kws = [kw for kw in target_kws if kw in text]
    missing_kws = [kw for kw in target_kws if kw not in text]
    
    # 3. Dynamic Technical Scoring
    if len(words) < 10:
        score_tech = round(2.0 + (len(words) * 0.2), 1)
    else:
        score_tech = min(10.0, 4.5 + (1.5 * len(matched_kws)))
        
    # 4. Dynamic Communication Scoring
    if 110.0 <= wpm <= 150.0:
        score_comm = min(10.0, 9.0 + (fluency - 8.0) * 0.5)
    else:
        score_comm = max(4.0, 9.0 - (0.04 * abs(130.0 - wpm)) + (fluency - 8.0) * 0.2)
        
    # 5. Dynamic Relevance Scoring
    arch_terms = ["scale", "design", "performance", "reliability", "latency", "load", "network", "thread"]
    matched_arch = [term for term in arch_terms if term in text]
    
    score_rel = min(10.0, 5.0 + (1.2 * len(matched_kws)) + (0.5 * len(matched_arch)))
    if len(words) < 10:
        score_rel = max(1.0, score_rel - 4.0)
        
    # 6. Dynamic Contextual Feedback Tree
    feedback_phrases = []
    
    if score_tech >= 8.0:
        feedback_phrases.append(
            f"Excellent technical articulation! Your response cleanly integrated standard "
            f"principles, specifically addressing target parameters: {', '.join(matched_kws)}."
        )
    elif score_tech >= 5.0:
        feedback_phrases.append(
            f"Solid baseline explanation. You correctly highlighted: {', '.join(matched_kws)}. "
            f"To achieve enterprise depth, consider expanding on: {', '.join(missing_kws[:3])}."
        )
    else:
        feedback_phrases.append(
            f"Your response was quite brief. Focus on explaining standard domain concepts such as "
            f"{', '.join(target_kws[:3])} to demonstrate core systems planning skills."
        )
        
    # Pacing advice
    if wpm > 155.0:
        feedback_phrases.append(
            f"Your speaking rate was fast ({round(wpm, 1)} WPM). Try to incorporate deliberate "
            f"pauses between technical thoughts to improve recruiter clarity."
        )
    elif wpm < 95.0:
        feedback_phrases.append(
            f"Your pacing was measured ({round(wpm, 1)} WPM). Consider keeping key concepts tightly "
            f"linked to prevent technical momentum losses."
        )
    else:
        feedback_phrases.append("Your speech pacing and professional delivery rate were outstanding.")
        
    return {
        "score_tech": round(score_tech, 1),
        "score_comm": round(score_comm, 1),
        "score_rel": round(score_rel, 1),
        "feedback": " ".join(feedback_phrases)
    }
```

---

## 5. Continuity Checklist for Live Verification

To verify that the system runs dynamically after applying changes, the recruiter can follow these test actions:

- [ ] **Submit Short Answers**: Submit an answer with less than 5 words (e.g. *"it is good"*). Check if the AI grades technical and relevance scores as low (2.0 to 4.0) and generates brief-response warnings.
- [ ] **Submit Targeted Keyword Answers**: Submit an answer using multiple correct keywords (e.g. for microservices event bus, write: *"We can deploy a Kafka broker with multiple partitions and consumer groups to establish high-throughput pub/sub real-time streams"*). Check if scores rise above `8.5` and matched keywords are highlighted in the feedback.
- [ ] **Test Speech Pace Variables**: Submit answers with deliberate rapid speech vs very slow speech, and check if communication scores reflect pacing penalties.
- [ ] **Verify SQLite Column Writers**: Open SQLite databases after submitting 5 questions, select `history_logs`, and verify that all customized grade keys (`score_tech`, `score_comm`, `score_rel`, `feedback`) are saved exactly as returned.

---
> [!TIP]
> By adopting this dynamic heuristic grading fallback, you protect the hiring engine from external API interruptions, providing candidates with a premium, responsive assessment experience at all times.
