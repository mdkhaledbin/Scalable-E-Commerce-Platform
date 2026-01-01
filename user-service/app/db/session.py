"""Database engine and session configuration for the user service."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# SQLite needs a special argument to allow usage across threads when the app runs with Uvicorn workers.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session that is closed after the request ends."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
