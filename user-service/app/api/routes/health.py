"""Health probes for the user service."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/", summary="Service health check")
def health() -> dict[str, str]:
    """Simple endpoint to verify the service is running."""

    return {"status": "ok"}
