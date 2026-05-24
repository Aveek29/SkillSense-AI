import logging
from typing import List, Dict, Any, Optional

try:
    from groq import Groq
    from groq import BadRequestError, AuthenticationError, APIError
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from app.core.config import get_settings
from app.core.utils import clean_json_payload

logger = logging.getLogger(__name__)


class GroqAIService:
    """Groq-powered LLM service for interview assessment, grading, and infrastructure monitoring.

    Data flow:
      Local DSP/NLP (Librosa, spaCy) → Metrics dict → Groq LLM prompt
      → JSON response parsed → SQLite history_logs (nested speech_metrics + grades)
      → FastAPI → Vite dashboard
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"
        self.client = None

        if HAS_GROQ and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("GroqAI client initialized with model %s", self.model)
            except Exception as e:
                logger.warning("Groq client init failed: %s", e)
                self.client = None
        else:
            logger.info("GROQ_API_KEY not set — Groq disabled, will use fallback")

    def is_available(self) -> bool:
        return self.client is not None

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3,
                  max_tokens: int = 1024) -> Optional[str]:
        if not self.client:
            logger.debug("Groq client unavailable — skipping LLM call")
            return None
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            logger.debug("Groq LLM response received (%d chars)", len(content or ""))
            return content
        except BadRequestError as e:
            logger.error("Groq BadRequestError: %s", e)
            return None
        except AuthenticationError as e:
            logger.error("Groq AuthenticationError: check GROQ_API_KEY — %s", e)
            return None
        except APIError as e:
            logger.error("Groq APIError: %s", e)
            return None
        except Exception as e:
            logger.error("Groq unexpected error: %s", e)
            return None

    # ── Interview Assessment ──────────────────────────────────────────

    def generate_next_question(self, domain: str, skills: List[str],
                               history: List[Dict[str, Any]],
                               mode: str = "Technical") -> Dict[str, Any]:
        skills_str = ", ".join(skills) if skills else "General Software Architecture"
        history_formatted = ""
        for h in history:
            g = h.get("grades", h)
            history_formatted += (
                f"Q: {h.get('question', '')}\n"
                f"Score: {g.get('score_tech', 'N/A')}/10\n"
                f"Feedback: {g.get('feedback', '')}\n\n"
            )

        ec2_mentioned = any(
            "ec2" in h.get("transcript", "").lower() or "aws" in h.get("transcript", "").lower()
            for h in history
        )

        system = (
            f"You are an Expert conducting a {mode} assessment. "
            "Output valid JSON only, no markdown fences."
        )
        user = f"""
Mode: {mode}
Candidate Domain: {domain}
Parsed Skills: {skills_str}
EC2 Mentioned: {'yes' if ec2_mentioned else 'no'}

Conversation history:
{history_formatted}

Generate the NEXT interview question appropriate for {mode} mode. Rules:
- If EC2 was mentioned by candidate, ask a deep-dive on EC2 architecture, auto-scaling, or cost optimization
- If last score < 5.0 → easier question
- If last score >= 8.5 → harder, more complex
- First question → medium difficulty
- Must be specific to {domain}
- Be creative and dynamic — do NOT repeat the same question pattern

Respond in this exact JSON format:
{{"question_text": "...", "difficulty": "easy|medium|hard", "target_keywords": ["..."], "hints": "..."}}
"""
        result = self._call_llm(system, user)
        if result:
            try:
                return clean_json_payload(result)
            except Exception:
                logger.warning("Groq question generation fallback to static")

        return {
            "question_text": "Explain standard database scaling constraints when migrating from local monolithic models to cloud instances.",
            "difficulty": "medium",
            "target_keywords": ["horizontal scale", "sharding", "replicas", "pooling"],
            "hints": "Candidate should address scaling connection limitations"
        }

    def grade_response(self, domain: str, question: str, transcript: str,
                       metrics: dict, mode: str = "Technical") -> Dict[str, Any]:
        system = (
            f"You are an expert {mode} interviewer. Grade each response independently "
            "with fresh criteria — never reuse generic feedback. Be specific to the transcript "
            "content. Output valid JSON only, no markdown."
        )
        user = f"""
Mode: {mode}
Interview Domain: {domain}
Question: {question}
Candidate Transcript: "{transcript}"
Speaking Rate: {metrics.get('speaking_rate_wpm', 'N/A')} WPM
Fluency Score: {metrics.get('fluency_score', 'N/A')}/10

Score 0.0-10.0 on three axes:
- score_tech: technical accuracy, depth, correctness
- score_comm: clarity, structure, communication flow
- score_rel: relevance to the exact question asked

Write ONE specific feedback sentence that references something the candidate actually said.
Do NOT use template phrases like "good understanding" or "consider elaborating" — be concrete.

JSON:
{{"score_tech": 0.0, "score_comm": 0.0, "score_rel": 0.0, "feedback": "..."}}
"""
        result = self._call_llm(system, user)
        if result:
            try:
                return clean_json_payload(result)
            except Exception:
                logger.warning("Groq grading fallback to static")

        return {
            "score_tech": 7.0,
            "score_comm": 8.0,
            "score_rel": 7.5,
            "feedback": "Satisfactory response. Consider elaborating with more specific examples next time."
        }

    # ── Monitoring & Insights ─────────────────────────────────────────

    def analyze_anomaly_insight(self, instance_id: str, metric: str, value: str,
                                anomaly_score: float) -> Dict[str, Any]:
        system = "You are a FinOps monitoring analyst. Output valid JSON only."
        user = f"""
Cloud sandbox anomaly detected:
- Instance: {instance_id}
- Metric: {metric}
- Value: {value}
- Anomaly Score: {anomaly_score}

Analyze severity, hypothesize root cause, and recommend action.

JSON:
{{"severity": "low|medium|high|critical", "hypothesis": "...", "recommended_action": "..."}}
"""
        result = self._call_llm(system, user, temperature=0.2)
        if result:
            try:
                return clean_json_payload(result)
            except Exception:
                pass
        return {
            "severity": "medium",
            "hypothesis": "Possible resource contention or unexpected workload spike.",
            "recommended_action": "Review instance utilization history and adjust auto-scaling thresholds."
        }

    def generate_cost_optimization_tip(self, forecast_aggregate: float,
                                       daily_avg: float) -> Dict[str, Any]:
        system = "You are a FinOps cost optimization advisor. Output valid JSON only."
        user = f"""
Cloud spending data:
- Forecasted aggregate spend: ${forecast_aggregate}
- Daily average: ${daily_avg}

Provide one actionable cost optimization tip with estimated savings.

JSON:
{{"tip": "...", "estimated_savings_pct": 0.0, "effort": "low|medium|high"}}
"""
        result = self._call_llm(system, user, temperature=0.2)
        if result:
            try:
                return clean_json_payload(result)
            except Exception:
                pass
        return {
            "tip": "Consider switching from on-demand to reserved instances for baseline workloads.",
            "estimated_savings_pct": 15.0,
            "effort": "low"
        }

    def generate_session_summary(self, candidate_name: str, domain: str,
                                 history: List[Dict]) -> Dict[str, Any]:
        if not history:
            return {
                "summary": "No responses recorded.",
                "strengths": [],
                "areas_for_improvement": [],
                "hiring_recommendation": "Insufficient data"
            }

        tech_scores = []
        comm_scores = []
        questions = []
        for h in history:
            g = h.get("grades", h)
            tech_scores.append(g.get("score_tech", 0))
            comm_scores.append(g.get("score_comm", 0))
            questions.append(h.get("question", ""))

        avg_tech = sum(tech_scores) / len(tech_scores)
        avg_comm = sum(comm_scores) / len(comm_scores)
        overall = (avg_tech + avg_comm) / 2

        system = "You are a technical hiring manager. Output valid JSON only."
        user = f"""
Summarize this {domain} interview for {candidate_name}:
- Questions asked: {len(history)}
- Avg Technical: {avg_tech:.1f}/10
- Avg Communication: {avg_comm:.1f}/10
- Overall: {overall:.1f}/10

JSON:
{{"summary": "...", "strengths": ["..."], "areas_for_improvement": ["..."], "hiring_recommendation": "Strong Hire|Hire|Hold|Pass"}}
"""
        result = self._call_llm(system, user, temperature=0.3)
        if result:
            try:
                return clean_json_payload(result)
            except Exception:
                pass

        recommendation = (
            "Strong Hire" if overall >= 8
            else "Hire" if overall >= 6.5
            else "Hold" if overall >= 5
            else "Pass"
        )
        return {
            "summary": f"Candidate demonstrated {'strong' if overall >= 7 else 'adequate'} "
                       f"technical capability in {domain} across {len(history)} questions.",
            "strengths": ["Technical knowledge", "Problem-solving approach"],
            "areas_for_improvement": ["Depth of system design explanations"],
            "hiring_recommendation": recommendation
        }
