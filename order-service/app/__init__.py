from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.models import Base
from app.db import engine
from app.api import api_router

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(_:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
def create_app() -> FastAPI:
    load_dotenv()
    
    app = FastAPI(
        title="Order service for Ecommerce API Project",
        description="Manage users order related service",
        version="0.1.0",
        lifespan=lifespan
    )
    
    app.include_router(api_router)
    
    return app

__all__ = ("create_app",)
    
    