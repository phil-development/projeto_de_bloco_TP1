from fastapi import APIRouter

from config import API_VERSION
from models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Verifica se a API esta ativa")
def health() -> HealthResponse:
    return HealthResponse(version=API_VERSION)
