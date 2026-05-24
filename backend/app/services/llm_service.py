import os
from typing import List, Dict, Any, Optional

from app.services.groq_service import GroqAIService
from app.core.utils import clean_json_payload

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

INTERVIEW_MODES = {
    "Technical": {
        "label": "Technical",
        "description": "Core engineering, framework details, syntax, and problem-solving",
        "wpm_range": (110, 150),
        "scoring_focus": "Technical depth, accuracy, code quality"
    },
    "HR & Cultural": {
        "label": "HR & Cultural",
        "description": "Communication, team dynamics, background, and cultural fit",
        "wpm_range": (120, 160),
        "scoring_focus": "Clarity, collaboration, values alignment"
    },
    "Behavioral & Leadership": {
        "label": "Behavioral & Leadership",
        "description": "Situational judgement, ownership, conflict resolution, STAR methodology",
        "wpm_range": (100, 145),
        "scoring_focus": "Structured storytelling, leadership indicators, decision-making"
    },
    "System Design & Architecture": {
        "label": "System Design & Architecture",
        "description": "High-level system scalability, microservices, databases, trade-offs",
        "wpm_range": (90, 140),
        "scoring_focus": "Scalability, reliability, design trade-offs, CAP theorem"
    },
    "Coding & Algorithms": {
        "label": "Coding & Algorithms",
        "description": "Space/time complexity, logic structure, problem-solving, data structures",
        "wpm_range": (100, 150),
        "scoring_focus": "Algorithm efficiency, code structure, optimization thinking"
    },
    "Hybrid (AI Adaptive)": {
        "label": "Hybrid (AI Adaptive)",
        "description": "Unified assessment dynamically tailored to resume skills and prior answers",
        "wpm_range": (100, 150),
        "scoring_focus": "Cross-functional adaptability, custom skill-based evaluation"
    },
}


class LLMOrchestratorService:
    """Multi-provider LLM orchestration: Groq (primary) -> Gemini (secondary) -> heuristic fallback."""

    def __init__(self):
        self.groq = GroqAIService()

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = None
        if HAS_GENAI and self.gemini_api_key and not self.groq.is_available():
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception:
                self.gemini_model = None

    @staticmethod
    def get_mode_info(mode: str) -> dict:
        return INTERVIEW_MODES.get(mode, INTERVIEW_MODES["Technical"])

    def _gemini_generate(self, prompt: str) -> str:
        if not self.gemini_model:
            return ""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception:
            return ""

    def _extract_score(self, entry: dict, key: str, default: float = 0.0) -> float:
        if key in entry:
            return entry.get(key, default)
        return entry.get("grades", {}).get(key, default)

    def _extract_feedback(self, entry: dict) -> str:
        if "feedback" in entry:
            return entry.get("feedback", "")
        return entry.get("grades", {}).get("feedback", "")

    def generate_next_question(self, domain: str, skills: List[str], history: List[Dict[str, Any]], mode: str = "Technical") -> Dict[str, Any]:
        if self.groq.is_available():
            return self.groq.generate_next_question(domain, skills, history, mode)

        skills_str = ", ".join(skills) if skills else "General Software Architecture"
        history_formatted = "".join(
            f"Q: {h.get('question')}\nScore: {self._extract_score(h, 'score_tech')}/10\n"
            f"Feedback: {self._extract_feedback(h)}\n\n"
            for h in history
        )
        mode_info = self.get_mode_info(mode)

        prompt = f"""
Act as an Expert conducting a {mode} assessment.
{mode_info['description']}
Candidate Domain: {domain}
Parsed Skills: {skills_str}

Conversation history:
{history_formatted}

Generate the next question appropriate for {mode} mode. Adjust difficulty dynamically:
- If last answer score was < 5.0, lower difficulty.
- If last answer score was >= 8.5, push harder constraints.

OUTPUT SCHEMA:
{{
  "question_text": "Single clear question text",
  "difficulty": "easy" | "medium" | "hard",
  "target_keywords": ["list", "of", "keywords"],
  "hints": "evaluation grading target details"
}}
"""
        gemini_text = self._gemini_generate(prompt)
        if gemini_text:
            try:
                return clean_json_payload(gemini_text)
            except Exception:
                pass

        return self._fallback_question_generator(domain, skills, history, mode)

    def _fallback_question_generator(self, domain: str, skills: list, history: list, mode: str = "Technical") -> dict:
        domain = domain.lower() if domain else ""
        skills_lower = [s.lower() for s in skills] if skills else []
        asked_count = len(history)
        mode_lower = mode.lower()

        question_bank = {
            "ai": [
                {"q": "Explain the bias-variance tradeoff in machine learning models. How do you detect and mitigate overfitting in a high-dimensional dataset?", "d": "medium", "k": ["overfitting", "regularization", "cross-validation", "bias", "variance", "underfitting"], "h": "Discuss regularization techniques like L1/L2 and cross-validation strategies"},
                {"q": "Describe the architecture of a transformer model. How does self-attention enable parallel processing compared to RNNs?", "d": "hard", "k": ["attention", "transformer", "encoder", "decoder", "self-attention", "positional", "embedding"], "h": "Focus on the attention mechanism and how it differs from sequential RNN processing"},
                {"q": "How would you design a real-time ML inference pipeline for processing streaming data with sub-100ms latency requirements?", "d": "hard", "k": ["streaming", "inference", "latency", "batch", "model", "serving", "optimization"], "h": "Consider model quantization, ONNX runtime, and edge deployment strategies"},
            ],
            "cloud": [
                {"q": "Design a multi-region active-active architecture on AWS with disaster recovery. How do you handle data consistency across regions?", "d": "hard", "k": ["multi-region", "active-active", "disaster", "recovery", "consistency", "route53", "global"], "h": "Consider DynamoDB Global Tables, Aurora Global Database, and Route53 routing"},
                {"q": "Explain AWS EC2 auto-scaling strategies. How would you configure target tracking scaling policies for a variable web workload?", "d": "medium", "k": ["autoscaling", "ec2", "target", "tracking", "scaling", "policy", "cloudwatch", "alarm"], "h": "Discuss step scaling vs target tracking, cooldown periods, and warm-up"},
                {"q": "How do you optimize cloud costs across compute, storage, and network services? Compare reserved, spot, and on-demand instances.", "d": "medium", "k": ["cost", "reserved", "spot", "on-demand", "savings", "plan", "optimization"], "h": "Compare pricing models and discuss scenarios where each is most cost-effective"},
            ],
            "database": [
                {"q": "Explain standard database scaling constraints when migrating from local monolithic models to cloud instances.", "d": "medium", "k": ["horizontal scale", "sharding", "replicas", "pooling", "migration", "monolithic"], "h": "Address read replicas, connection pooling, and sharding strategies"},
                {"q": "Compare SQL and NoSQL databases for a real-time analytics platform handling 10M writes per second. How do you ensure consistency?", "d": "hard", "k": ["sql", "nosql", "consistency", "partition", "cap", "eventual", "strong"], "h": "Discuss the CAP theorem and how different databases make tradeoffs"},
                {"q": "Design a database migration strategy from a self-hosted PostgreSQL instance to Amazon Aurora with zero downtime.", "d": "hard", "k": ["migration", "aurora", "postgresql", "downtime", "replication", "dms"], "h": "Consider AWS DMS, read replicas, and blue/green deployment cuts"},
            ],
            "kubernetes": [
                {"q": "Describe container orchestration with Kubernetes. How do you manage service discovery and ingress for microservices?", "d": "medium", "k": ["pod", "service", "ingress", "deployment", "k8s", "container", "orchestration"], "h": "Discuss kube-proxy, CoreDNS, and Ingress controllers"},
                {"q": "How would you implement a canary deployment strategy in Kubernetes with traffic splitting and automated rollback?", "d": "hard", "k": ["canary", "deployment", "rollback", "traffic", "split", "helm", "istio"], "h": "Consider service mesh (Istio/Linkerd) and progressive delivery tools like Argo Rollouts"},
            ],
            "microservice": [
                {"q": "How would you design a microservices event bus for real-time data streaming? Compare Kafka, RabbitMQ, and Amazon SQS.", "d": "hard", "k": ["kafka", "event", "bus", "streaming", "pub", "sub", "broker", "partition", "consumer"], "h": "Discuss throughput, partitioning, consumer groups, and exactly-once semantics"},
                {"q": "Explain distributed tracing in microservices. How do you identify latency bottlenecks across service boundaries?", "d": "medium", "k": ["tracing", "distributed", "latency", "jaeger", "opentelemetry", "span", "trace"], "h": "Discuss OpenTelemetry, trace context propagation, and sampling strategies"},
            ],
        }

        matched_bank = "database"
        for key in question_bank:
            if key in domain:
                matched_bank = key
                break
        for skill in skills_lower:
            for key in question_bank:
                if key in skill:
                    matched_bank = key
                    break

        bank = question_bank[matched_bank]
        asked_texts = {h.get("question", "").lower()[:40] for h in history}
        available = [q for q in bank if q["q"].lower()[:40] not in asked_texts]
        if not available:
            available = bank

        if history:
            last = history[-1]
            last_score = 0.0
            grades = last.get("grades", last)
            for key in ("score_tech", "score_comm", "score_rel"):
                val = grades.get(key)
                if val is not None:
                    last_score = max(last_score, float(val))
            if last_score < 5.0:
                available = [q for q in available if q["d"] == "medium" or q["d"] == "easy"]
            elif last_score >= 8.5:
                available = [q for q in available if q["d"] == "hard"]
            if not available:
                available = bank
        else:
            available = [q for q in available if q["d"] == "medium"]
            if not available:
                available = bank

        chosen = available[asked_count % len(available)]
        return {
            "question_text": chosen["q"],
            "difficulty": chosen["d"],
            "target_keywords": chosen["k"],
            "hints": chosen["h"],
        }

    def execute_local_heuristic_grader(self, question: str, transcript: str, metrics: dict, mode: str = "Technical") -> Dict[str, Any]:
        text = transcript.lower()
        words = text.split()
        wpm = metrics.get("speaking_rate_wpm", 130.0)
        fluency = metrics.get("fluency_score", 8.0)
        mode_lower = mode.lower()

        keyword_map = {
            "technical": ["horizontal", "sharding", "replica", "monolithic", "pooling", "migration", "index", "partition", "api", "endpoint", "pipeline"],
            "hr": ["team", "collaborate", "culture", "value", "communicate", "stakeholder", "feedback", "goal", "align", "growth", "mentor"],
            "behavioral": ["situation", "task", "action", "result", "star", "conflict", "resolve", "owner", "initiative", "challenge", "impact", "outcome", "responsibility"],
            "system design": ["scale", "load", "balance", "replica", "cache", "cdn", "queue", "failover", "consistency", "partition", "throughput", "latency", "cap", "shard"],
            "coding": ["complexity", "array", "hash", "pointer", "recursion", "iterate", "optimize", "o(1)", "o(n)", "sort", "search", "tree", "graph", "dynamic", "memoize"],
            "hybrid": ["adapt", "integrate", "cross-functional", "end-to-end", "pipeline", "automation", "efficiency", "scale", "design", "optimize"],
        }

        technical_keywords = keyword_map["technical"]
        if "hr" in mode_lower or "cultural" in mode_lower:
            primary_set = keyword_map["hr"]
            technical_keywords = keyword_map["hr"]
        elif "behavioral" in mode_lower or "leadership" in mode_lower:
            primary_set = keyword_map["behavioral"]
            technical_keywords = keyword_map["behavioral"]
        elif "design" in mode_lower and "system" in mode_lower:
            primary_set = keyword_map["system design"]
            technical_keywords = keyword_map["system design"]
        elif "coding" in mode_lower or "algorithm" in mode_lower:
            primary_set = keyword_map["coding"]
            technical_keywords = keyword_map["coding"]
        elif "hybrid" in mode_lower:
            primary_set = keyword_map["hybrid"]
            technical_keywords = keyword_map["hybrid"]
        else:
            primary_set = keyword_map["technical"]

        matched_domain = "database"
        for topic in primary_set:
            if topic in question.lower():
                matched_domain = topic
                break

        target_kws = primary_set
        matched_kws = [kw for kw in target_kws if kw in text]
        missing_kws = [kw for kw in target_kws if kw not in text]

        if len(words) < 10:
            score_tech = round(2.0 + (len(words) * 0.2), 1)
        else:
            score_tech = round(min(10.0, 4.5 + (1.5 * len(matched_kws))), 1)

        mode_info = self.get_mode_info(mode)
        wpm_low, wpm_high = mode_info["wpm_range"]
        wpm_optimal = (wpm_low + wpm_high) / 2.0
        if wpm_low <= wpm <= wpm_high:
            score_comm = round(min(10.0, 9.0 + (fluency - 8.0) * 0.5), 1)
        else:
            penalty = 0.04 * abs(wpm_optimal - wpm)
            score_comm = round(max(1.0, min(10.0, 9.0 - penalty + (fluency - 8.0) * 0.2)), 1)

        arch_terms = ["scale", "design", "performance", "reliability", "latency", "load", "network", "thread", "memory", "cache", "optimize", "efficient"]
        matched_arch = [t for t in arch_terms if t in text]
        score_rel = round(min(10.0, 5.0 + (1.2 * len(matched_kws)) + (0.5 * len(matched_arch))), 1)
        if len(words) < 10:
            score_rel = round(max(1.0, score_rel - 4.0), 1)

        parts = []
        if score_tech >= 8.0:
            parts.append(f"Excellent articulation for {mode} mode. Your response clearly addressed targeted parameters: {', '.join(matched_kws)}.")
        elif score_tech >= 5.0:
            parts.append(f"Solid baseline explanation for {mode} mode. You correctly highlighted: {', '.join(matched_kws)}. Consider expanding on: {', '.join(missing_kws[:3])}.")
        else:
            parts.append(f"The response was brief for {mode} mode. Focus on core concepts like {', '.join(target_kws[:3])} to demonstrate appropriate depth.")

        if wpm > wpm_high + 10:
            parts.append(f"Speaking rate was fast ({round(wpm, 1)} WPM for {mode} mode). Adding deliberate pauses improves clarity.")
        elif wpm < wpm_low - 10:
            parts.append(f"Pacing was measured ({round(wpm, 1)} WPM for {mode} mode). Try keeping key concepts tightly linked.")
        else:
            parts.append(f"Speech pacing and delivery rate are well-suited for {mode} assessment.")

        return {
            "score_tech": score_tech,
            "score_comm": score_comm,
            "score_rel": score_rel,
            "feedback": " ".join(parts),
        }

    def grade_response(self, domain: str, question: str, transcript: str, metrics: dict, mode: str = "Technical") -> Dict[str, Any]:
        if self.groq.is_available():
            try:
                result = self.groq.grade_response(domain, question, transcript, metrics, mode)
                if isinstance(result, dict) and "score_tech" in result:
                    return result
            except Exception:
                pass

        prompt = f"""
Evaluate this candidate response for a {mode} assessment.
Question: {question}
Transcript: "{transcript}"
Words Per Minute: {metrics.get('speaking_rate_wpm')}
Voice Fluency Index: {metrics.get('fluency_score')}/10

Output detailed grade scores along 3 axes on a 0.0 to 10.0 scale, tailored to {mode} mode.

OUTPUT SCHEMA:
{{
  "score_tech": 0.0,
  "score_comm": 0.0,
  "score_rel": 0.0,
  "feedback": "constructive professional feedback"
}}
"""
        gemini_text = self._gemini_generate(prompt)
        if gemini_text:
            try:
                return clean_json_payload(gemini_text)
            except Exception:
                pass

        return self.execute_local_heuristic_grader(question, transcript, metrics, mode)
