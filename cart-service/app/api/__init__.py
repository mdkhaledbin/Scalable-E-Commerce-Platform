from fastapi import APIRouter
from app.api.routes import health, cart

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(cart.router)

__all__ = ("api_router")
