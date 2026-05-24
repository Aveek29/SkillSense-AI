import sys
import os
import datetime

# Add the parent directory to Python path so we can import app modules
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import SessionLocal, engine
from app.models.tables import Base, DBUser, DBInterviewSession, DBSandboxResource, DBSandboxMetric
from database.seed_data import generate_all_seed_data

def seed():
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if database is already seeded
        if db.query(DBUser).first():
            print("Database already contains data. Skipping seeding.")
            return

        print("Generating seed data...")
        data = generate_all_seed_data()
        
        print(f"Seeding {len(data['users'])} users...")
        for u in data['users']:
            user = DBUser(
                id=u['id'],
                name=u['name'],
                email=u['email'],
                password_hash=u['password_hash'],
                role=u.get('role', 'candidate'),
            )
            db.add(user)
        db.commit()

        print(f"Seeding {len(data['sessions'])} interview sessions...")
        for s in data['sessions']:
            session = DBInterviewSession(
                id=s['id'],
                candidate_id=s['candidate_id'],
                domain=s['domain'],
                mode=s['mode'],
                status=s['status'],
                history_logs=s['history_logs']
            )
            db.add(session)
        db.commit()

        print(f"Seeding {len(data['sandboxes'])} sandbox resources...")
        for sb in data['sandboxes']:
            sandbox = DBSandboxResource(
                resource_id=sb['resource_id'],
                user_id=sb['user_id'],
                interview_id=sb['interview_id'],
                provider=sb['provider'],
                instance_tier=sb['instance_tier'],
                region=sb['region'],
                status=sb['status'],
                hourly_rate=sb['hourly_rate']
            )
            db.add(sandbox)
        db.commit()

        print(f"Seeding {len(data['metrics'])} sandbox metrics...")
        for m in data['metrics']:
            ts_str = m['timestamp']
            # Parse standard ISO format timestamp
            ts = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            metric = DBSandboxMetric(
                resource_id=m['resource_id'],
                cpu_utilization=m['cpu_utilization'],
                ram_utilization=m['ram_utilization'],
                network_egress_bytes=m['network_egress_bytes'],
                daily_cost=m['daily_cost'],
                timestamp=ts,
                is_anomaly=m['is_anomaly'],
                anomaly_score=m['anomaly_score']
            )
            db.add(metric)
        db.commit()

        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
