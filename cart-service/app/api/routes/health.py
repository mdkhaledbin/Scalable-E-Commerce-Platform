from fastapi import APIRouter

router = APIRouter(prefix="/carts", tags=["carts"])

@router.get("/", summary="Health check for cart-service", response_model=dict[str, str])
def health_check() -> dict[str, str]:
	return {"status": "healthy"}


    