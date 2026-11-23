from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, select

from db import get_session
from models.auth import User
from models.predict import Intent, PredictionRead, PredictRequest, PredictResponse
from models.tables import PredictionRecord
from security.auth import get_current_user

router = APIRouter(tags=["predict"])

# Placeholder ate a entrega do modelo de classificacao de intencao.
STUB_INTENT = Intent.TECHNICAL_ISSUE
STUB_CONFIDENCE = 0.87
STUB_MODEL_VERSION = "stub-0.0.0"


@router.post("/predict", response_model=PredictResponse, summary="Classifica a intencao do ticket")
def predict(
    payload: PredictRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PredictResponse:
    # O dono vem sempre do token validado, nunca do corpo da requisicao.
    record = PredictionRecord(
        owner_id=user.id,
        text=payload.text,
        intent=STUB_INTENT.value,
        confidence=STUB_CONFIDENCE,
        model_version=STUB_MODEL_VERSION,
    )
    session.add(record)
    session.commit()

    return PredictResponse(
        intent=STUB_INTENT,
        confidence=STUB_CONFIDENCE,
        model_version=STUB_MODEL_VERSION,
    )


@router.get(
    "/predictions",
    response_model=list[PredictionRead],
    summary="Lista as predictions do usuario autenticado",
)
def list_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[PredictionRecord]:
    statement = (
        select(PredictionRecord)
        .where(PredictionRecord.owner_id == user.id)
        .order_by(col(PredictionRecord.id).desc())
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_owned_prediction(
    prediction_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PredictionRecord:
    """Controle de acesso por ownership (anti-BOLA).

    Toda rota que recebe o id de uma prediction deve depender desta funcao: ela so entrega o recurso
    se o usuario autenticado for o dono. Id inexistente e id de outro usuario produzem a mesma resposta
    (404), para nao revelar quais ids existem. Com 403, um atacante poderia enumerar ids alheios.
    """
    record = session.get(PredictionRecord, prediction_id)
    if record is None or record.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction nao encontrada")
    return record


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionRead,
    summary="Detalha uma prediction do usuario autenticado",
)
def get_prediction(prediction: PredictionRecord = Depends(get_owned_prediction)) -> PredictionRecord:
    return prediction
