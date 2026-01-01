"""FastAPI application factory for the user service."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import api_router
from app.db.session import engine
from app.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
	Base.metadata.create_all(bind=engine)
	yield


def create_app() -> FastAPI:
	"""Instantiate and configure the FastAPI application."""

	load_dotenv()

	application = FastAPI(
		title="User Service for Ecommerce Platform",
		description="Manage customer accounts for the ecommerce ecosystem.",
		version="0.1.0",
		lifespan=lifespan,
	)
	application.include_router(api_router)
	return application


__all__ = ("create_app",)
