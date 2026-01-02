from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from app.models import Base
from app.db import engine
from app.api import api_router

@asynccontextmanager
async def lifespan(_:FastAPI):
    """Ensure database tables exist before the application starts serving."""
    Base.metadata.create_all(bind=engine)
    yield
    

def create_app() -> FastAPI:
    """Application factory that wires config, routers, and startup tasks."""
    load_dotenv()
    
    app = FastAPI(
        title="Product service for ecommerce app",
        description="Manage Products for the ecommerce project",
        version="0.1.0",
        lifespan=lifespan
    )
    app.include_router(api_router)
    return app

__all__ = ("create_app",)
    