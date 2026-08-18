from fastapi import APIRouter, Depends

from models.auth import User
from models.predict import Intent, PredictRequest, PredictResponse
from security.auth import get_current_user

router = APIRouter(tags=["predict"])

# Placeholder ate a entrega do modelo de classificacao de intencao.
STUB_INTENT = Intent.TECHNICAL_ISSUE
STUB_CONFIDENCE = 0.87
STUB_MODEL_VERSION = "stub-0.0.0"


@router.post("/predict", response_model=PredictResponse, summary="Classifica a intencao do ticket")
def predict(payload: PredictRequest, user: User = Depends(get_current_user)) -> PredictResponse:
    return PredictResponse(
        intent=STUB_INTENT,
        confidence=STUB_CONFIDENCE,
        model_version=STUB_MODEL_VERSION,
    )
