"""
Seed Data Generator for SkillSense AI Platform.
Generates simulated candidate profiles, interview sessions, sandbox resources,
and time-series VM metrics for development and demo purposes.
"""
import uuid
import random
import datetime
import json

# ─────────────────────────────────────────────────────────────────────────
# Simulated Users
# ─────────────────────────────────────────────────────────────────────────
SEED_USERS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Alice Johnson",
        "email": "alice.johnson@techcorp.com",
        "password_hash": "$2b$12$placeholder_hash_alice_johnson_2024",
        "role": "candidate",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Bob Smith",
        "email": "bob.smith@devops.io",
        "password_hash": "$2b$12$placeholder_hash_bob_smith_2024",
        "role": "candidate",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Clara Mendes",
        "email": "clara.mendes@airesearch.org",
        "password_hash": "$2b$12$placeholder_hash_clara_mendes_2024",
        "role": "candidate",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "David Kim",
        "email": "david.kim@cloudeng.dev",
        "password_hash": "$2b$12$placeholder_hash_david_kim_2024",
        "role": "candidate",
    },
]

# ─────────────────────────────────────────────────────────────────────────
# Simulated Interview Sessions
# ─────────────────────────────────────────────────────────────────────────
DOMAINS = ["AI/ML Engineering", "Cloud DevOps", "Full Stack Web", "Systems Architecture"]
MODES = ["Technical", "HR"]


def generate_interview_history(num_questions: int = 5) -> list:
    """Generate realistic JSONB interview history logs."""
    questions = [
        "Explain horizontal scaling strategies for PostgreSQL.",
        "How would you implement a microservices event bus?",
        "Describe container orchestration with Kubernetes.",
        "Walk through a CI/CD pipeline for a FastAPI application.",
        "How does an Isolation Forest detect anomalies in time-series data?",
    ]
    history = []
    for i in range(min(num_questions, len(questions))):
        history.append({
            "question": questions[i],
            "transcript": f"Simulated candidate response for question {i + 1}...",
            "speaking_rate_wpm": round(random.uniform(110, 160), 2),
            "fluency_score": round(random.uniform(5.0, 9.5), 2),
            "score_tech": round(random.uniform(5.0, 9.8), 1),
            "score_comm": round(random.uniform(6.0, 9.5), 1),
            "score_rel": round(random.uniform(5.5, 9.2), 1),
            "feedback": f"Automated grading feedback for Q{i + 1}."
        })
    return history


def generate_seed_sessions() -> list:
    """Generate interview sessions linked to seed users."""
    sessions = []
    for user in SEED_USERS:
        session_id = str(uuid.uuid4())
        num_q = random.choice([3, 4, 5])
        status = "Completed" if num_q >= 5 else "In-Progress"
        sessions.append({
            "id": session_id,
            "candidate_id": user["id"],
            "domain": random.choice(DOMAINS),
            "mode": random.choice(MODES),
            "status": status,
            "history_logs": generate_interview_history(num_q),
        })
    return sessions


# ─────────────────────────────────────────────────────────────────────────
# Simulated Sandbox Resources & Metrics
# ─────────────────────────────────────────────────────────────────────────
INSTANCE_TIERS = ["t3.large", "t3.xlarge", "m5.large"]


def generate_sandbox_metrics(resource_id: str, days: int = 30) -> list:
    """Generate simulated daily VM telemetry with occasional anomalies."""
    metrics = []
    base_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    for day in range(days):
        ts = base_date + datetime.timedelta(days=day)

        # Normal metrics with occasional spikes
        is_spike = random.random() < 0.08  # ~8% chance of anomaly
        cpu = round(random.uniform(75, 99.9) if is_spike else random.uniform(15, 55), 2)
        ram = round(random.uniform(70, 98) if is_spike else random.uniform(20, 60), 2)
        egress = random.randint(500000, 5000000) if is_spike else random.randint(10000, 200000)
        cost = round(random.uniform(8, 25) if is_spike else random.uniform(1.5, 5.5), 2)

        metrics.append({
            "resource_id": resource_id,
            "cpu_utilization": cpu,
            "ram_utilization": ram,
            "network_egress_bytes": egress,
            "daily_cost": cost,
            "timestamp": ts.isoformat(),
            "is_anomaly": is_spike,
            "anomaly_score": round(random.uniform(0.7, 0.99), 4) if is_spike else round(random.uniform(0.01, 0.3), 4),
        })
    return metrics


def generate_seed_sandboxes(sessions: list) -> tuple:
    """Generate sandbox resources and their metrics linked to sessions."""
    sandboxes = []
    all_metrics = []

    for session in sessions:
        resource_id = f"i-{uuid.uuid4().hex[:16]}"
        tier = random.choice(INSTANCE_TIERS)
        sandboxes.append({
            "resource_id": resource_id,
            "user_id": session["candidate_id"],
            "interview_id": session["id"],
            "provider": "AWS",
            "instance_tier": tier,
            "region": "us-east-1",
            "status": "terminated" if session["status"] == "Completed" else "running",
            "hourly_rate": 0.0832 if tier == "t3.large" else 0.1664,
        })
        all_metrics.extend(generate_sandbox_metrics(resource_id, days=30))

    return sandboxes, all_metrics


# ─────────────────────────────────────────────────────────────────────────
# Main seed execution
# ─────────────────────────────────────────────────────────────────────────
def generate_all_seed_data() -> dict:
    """Generate complete seed dataset for the platform."""
    sessions = generate_seed_sessions()
    sandboxes, metrics = generate_seed_sandboxes(sessions)

    return {
        "users": SEED_USERS,
        "sessions": sessions,
        "sandboxes": sandboxes,
        "metrics": metrics,
    }


if __name__ == "__main__":
    seed = generate_all_seed_data()
    print(f"Generated {len(seed['users'])} users")
    print(f"Generated {len(seed['sessions'])} interview sessions")
    print(f"Generated {len(seed['sandboxes'])} sandbox resources")
    print(f"Generated {len(seed['metrics'])} metric data points")
    print("\nSample user:", json.dumps(seed["users"][0], indent=2))
    print("\nSample metric:", json.dumps(seed["metrics"][0], indent=2))
