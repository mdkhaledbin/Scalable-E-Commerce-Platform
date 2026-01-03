from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
connect_args = {"check_same_thread":False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    url=DATABASE_URL,
    connect_args=connect_args,
    future=True,
    pool_pre_ping= True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db() -> Generator[Session,None,None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
 
