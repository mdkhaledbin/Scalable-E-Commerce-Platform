from fastapi import APIRouter, status

router = APIRouter(prefix="/orders/health", tags=["health"])


@router.get("", summary="Health check", response_model=dict[str, str], status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    return {"status": "order-service is running"}

