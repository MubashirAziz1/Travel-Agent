from fastapi import APIRouter
from schemas.health import HealthResponse

router = APIRouter()

@router.get("/health",response_model= HealthResponse, tags = ["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status= 'ok',
        version= ' 0.0.1',
        environment = 'Development' 
    )