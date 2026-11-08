from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from db import get_session
from models.auth import User
from models.tables import UserRecord

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais invalidas ou expiradas",
    headers={"WWW-Authenticate": "Bearer"},
)

# Hash descartavel: quando o usuario nao existe, o bcrypt roda mesmo assim e o tempo de resposta
# nao revela se o username e valido.
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt())


def _get_user_record(session: Session, username: str) -> UserRecord | None:
    return session.exec(select(UserRecord).where(UserRecord.username == username)).first()


def _to_user(record: UserRecord) -> User:
    return User(id=record.id, username=record.username, role=record.role)


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    record = _get_user_record(session, username)
    stored_hash = record.password_hash.encode() if record else _DUMMY_HASH
    password_ok = bcrypt.checkpw(password.encode(), stored_hash)
    if record is None or not password_ok:
        return None
    return _to_user(record)


def create_access_token(subject: str) -> tuple[str, int]:
    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires_in


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise credentials_exception

    username = payload.get("sub")
    if not isinstance(username, str):
        raise credentials_exception

    # O usuario e relido do banco a cada requisicao: um usuario removido perde o acesso
    # mesmo que o token ainda nao tenha expirado.
    record = _get_user_record(session, username)
    if record is None:
        raise credentials_exception
    return _to_user(record)
