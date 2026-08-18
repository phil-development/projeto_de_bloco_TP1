import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from models.auth import User
from security.users import ADMIN_PASSWORD_HASH, ADMIN_USERNAME

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais invalidas ou expiradas",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(username: str, password: str) -> User | None:
    username_ok = hmac.compare_digest(username.encode(), ADMIN_USERNAME.encode())
    password_ok = bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH)
    if username_ok and password_ok:
        return User(username=ADMIN_USERNAME)
    return None


def create_access_token(subject: str) -> tuple[str, int]:
    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), expires_in


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise credentials_exception

    username = payload.get("sub")
    if username != ADMIN_USERNAME:
        raise credentials_exception
    return User(username=username)
