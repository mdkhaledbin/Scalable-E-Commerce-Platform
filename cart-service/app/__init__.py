from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.db import engine
from app.models import Base
from app.api import api_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
def create_app() -> FastAPI:
    load_dotenv()
    
    app = FastAPI(
        title="Cart service for Ecommerce API Project",
        description="Manage users cart related service",
        version="0.1.0",
        lifespan=lifespan
    )
    app.include_router(api_router)
    
    return app

__all__ = ("create_app")


    