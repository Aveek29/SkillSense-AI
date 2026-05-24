try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    HAS_ANOMALY_LIBS = True
except ImportError:
    HAS_ANOMALY_LIBS = False


class CloudResourceAnomalyDetector:
    """Isolation Forest anomaly detection engine for flagging abnormal VM resource patterns."""

    def __init__(self, contamination_rate: float = 0.05):
        if HAS_ANOMALY_LIBS:
            self.model = IsolationForest(contamination=contamination_rate, random_state=42)
        else:
            self.model = None

    def _rule_based_detection(self, metrics_log: list) -> list:
        """Fallback rule-based anomaly detector using simple thresholds."""
        for item in metrics_log:
            cpu = float(item.get("cpu_utilization", 0.0))
            ram = float(item.get("ram_utilization", 0.0))
            cost = float(item.get("daily_cost", 0.0))

            is_anomaly = False
            score = 0.1

            if cpu > 85.0 or ram > 80.0 or cost > 15.0:
                is_anomaly = True
                score = min(0.99, 0.65 + (cpu - 85.0) / 100.0 + (ram - 80.0) / 100.0)
            else:
                score = max(0.01, (cpu / 200.0) + (ram / 200.0))

            item["is_anomaly"] = is_anomaly
            item["anomaly_score"] = float(round(score, 4))

        return metrics_log

    def evaluate_resource_telemetry(self, metrics_log: list) -> list:
        """Run Isolation Forest predictions to flag anomalies in VM CPU, RAM, & cost patterns."""
        if not HAS_ANOMALY_LIBS:
            return self._rule_based_detection(metrics_log)

        try:
            df = pd.DataFrame(metrics_log)
            feature_columns = ['cpu_utilization', 'ram_utilization', 'network_egress_bytes', 'daily_cost']

            for col in feature_columns:
                if col not in df.columns:
                    df[col] = 0.0

            X = df[feature_columns].fillna(0.0).values

            if len(X) < 10:
                for item in metrics_log:
                    item["is_anomaly"] = False
                    item["anomaly_score"] = 0.0
                return metrics_log

            self.model.fit(X)
            predictions = self.model.predict(X)
            scores = self.model.decision_function(X)

            for i, item in enumerate(metrics_log):
                item["is_anomaly"] = True if predictions[i] == -1 else False
                item["anomaly_score"] = float(round(abs(scores[i]), 4))

            return metrics_log
        except Exception:
            return self._rule_based_detection(metrics_log)
