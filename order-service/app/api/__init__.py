from fastapi import APIRouter

from app.api.routes import health_router, order_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(order_router)

__all__ = ("api_router", "health_router", "order_router")