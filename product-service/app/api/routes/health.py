from fastapi import APIRouter

router = APIRouter(tags=['health'], prefix='/products')

@router.get("/", summary='Health check api', status_code=200)
def health_check() -> dict[str,str]:
    return {"status": "okay"}