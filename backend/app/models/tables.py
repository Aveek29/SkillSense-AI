from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import TypeDecorator, CHAR
import datetime
import uuid

Base = declarative_base()

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise CHAR(36) in other databases like SQLite.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            try:
                return str(uuid.UUID(value))
            except (ValueError, AttributeError):
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class DBUser(Base):
    """Candidate and Recruiter user accounts."""
    __tablename__ = 'users'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="candidate", nullable=False)  # "candidate" or "recruiter"
    aws_credential_secret_b64 = Column(String(500), nullable=True)  # Encrypted with AES-256-GCM
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    interviews = relationship("DBInterviewSession", back_populates="candidate", cascade="all, delete")
    resources = relationship("DBSandboxResource", back_populates="owner", cascade="all, delete")


class DBInterviewSession(Base):
    """Dynamic interview sessions with JSONB/JSON history logs."""
    __tablename__ = 'interview_sessions'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    candidate_id = Column(GUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    domain = Column(String(100), nullable=False)   # AI/ML, Cloud, Web
    mode = Column(String(50), nullable=False)       # Technical, HR
    status = Column(String(50), default="In-Progress", nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Database-agnostic JSON column (maps to JSONB on PG, TEXT on SQLite)
    history_logs = Column(JSON, default=lambda: [], nullable=False)
    skills = Column(JSON, default=lambda: [], nullable=False)

    candidate = relationship("DBUser", back_populates="interviews")
    sandbox = relationship("DBSandboxResource", uselist=False, back_populates="interview", cascade="all, delete")


class DBSandboxResource(Base):
    """AWS EC2 sandbox instances provisioned per interview session."""
    __tablename__ = 'sandbox_resources'

    resource_id = Column(String(150), primary_key=True)  # AWS Instance ID
    user_id = Column(GUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    interview_id = Column(GUID, ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    provider = Column(String(50), default="AWS", nullable=False)
    instance_tier = Column(String(100), default="t3.large", nullable=False)
    region = Column(String(100), default="us-east-1", nullable=False)
    status = Column(String(50), default="running", nullable=False)
    hourly_rate = Column(Numeric(10, 4), default=0.0832, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    owner = relationship("DBUser", back_populates="resources")
    interview = relationship("DBInterviewSession", back_populates="sandbox")
    metrics = relationship("DBSandboxMetric", back_populates="resource", cascade="all, delete")


class DBSandboxMetric(Base):
    """Time-series VM telemetry with Isolation Forest anomaly scoring."""
    __tablename__ = 'sandbox_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(150), ForeignKey('sandbox_resources.resource_id', ondelete='CASCADE'), nullable=False)
    cpu_utilization = Column(Numeric(5, 2), nullable=False)
    ram_utilization = Column(Numeric(5, 2), nullable=False)
    network_egress_bytes = Column(Integer, default=0, nullable=False)
    daily_cost = Column(Numeric(10, 2), default=0.00, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    # Anomaly scoring fields populated by Isolation Forest
    is_anomaly = Column(Boolean, default=False, nullable=False)
    anomaly_score = Column(Numeric(5, 4), default=0.0000, nullable=False)

    resource = relationship("DBSandboxResource", back_populates="metrics")
