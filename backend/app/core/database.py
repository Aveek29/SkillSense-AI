from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# Determine engine kwargs based on database type
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.DEBUG,
}

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread=False for FastAPI async
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL connection pooling for concurrent interview sessions
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)

# Session factory for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
