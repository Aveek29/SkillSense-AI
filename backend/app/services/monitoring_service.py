from typing import List, Dict, Any, Optional
from app.services.groq_service import GroqAIService


class MonitoringInsightService:
    """Groq-powered monitoring insights for FinOps, anomaly analysis, and interview session summaries."""

    def __init__(self, groq: Optional[GroqAIService] = None):
        self.groq = groq or GroqAIService()

    def analyze_anomaly(self, instance_id: str, metric: str, value: str, score: float) -> Dict[str, Any]:
        return self.groq.analyze_anomaly_insight(instance_id, metric, value, score)

    def cost_optimization_tip(self, forecast_aggregate: float, daily_avg: float) -> Dict[str, Any]:
        return self.groq.generate_cost_optimization_tip(forecast_aggregate, daily_avg)

    def session_summary(self, name: str, domain: str, history: List[Dict]) -> Dict[str, Any]:
        return self.groq.generate_session_summary(name, domain, history)

    def enrich_anomalies(self, anomalies: List[Dict]) -> List[Dict]:
        for a in anomalies:
            insight = self.analyze_anomaly(
                a.get("instance", ""),
                a.get("metric", ""),
                a.get("value", ""),
                a.get("score", 0.5),
            )
            a["severity"] = insight.get("severity", "medium")
            a["hypothesis"] = insight.get("hypothesis", "")
            a["recommended_action"] = insight.get("recommended_action", "")
        return anomalies
