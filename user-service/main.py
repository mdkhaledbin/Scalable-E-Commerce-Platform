"""WSGI/ASGI entrypoint exposing the FastAPI app instance."""

from app import create_app

app = create_app()

__all__ = ("app",)


