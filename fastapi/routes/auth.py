from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from config import LOGIN_RATE_LIMIT
from db import get_session
from models.auth import Token
from security.auth import authenticate_user, create_access_token
from security.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token, summary="Autentica o usuario e emite um JWT")
@limiter.limit(LOGIN_RATE_LIMIT)  # anti brute force: 10 requisicoes por minuto por cliente
def login(
    request: Request,  # exigido pelo SlowAPI para identificar o cliente; precisa se chamar "request"
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expires_in = create_access_token(user.username)
    return Token(access_token=access_token, expires_in=expires_in)
