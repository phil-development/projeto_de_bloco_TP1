import os
from pathlib import Path

SECRET_KEY = os.getenv("SECRET_KEY", "3f9a1c7e5b2d48a69e0c1f7b4d8a2e6c0b5f9d3a7e1c4b8f2a6d0e9c3b7f1a5d")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

API_TITLE = "Customer Support Intent API"
API_VERSION = "0.1.0"

# Banco SQLite criado por sqlite_database.py. DATABASE_PATH permite apontar para outro arquivo (ex.: testes).
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).resolve().parent / "database.db"))
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# --- CORS -------------------------------------------------------------------------------------------
# Allowlist explicita de origens (front-ends autorizados a chamar a API pelo navegador).
# Em outro ambiente, defina ALLOWED_ORIGINS com origens separadas por virgula, ex.:
#   ALLOWED_ORIGINS="https://app.exemplo.com,https://admin.exemplo.com"
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"


def parse_allowed_origins(raw: str) -> list[str]:
    """Converte a string de origens em lista e recusa curingas: a allowlist precisa ser explicita."""
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if any("*" in origin for origin in origins):
        raise ValueError("ALLOWED_ORIGINS nao aceita curinga ('*'): liste cada origem explicitamente.")
    return origins


ALLOWED_ORIGINS = parse_allowed_origins(os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS))

# --- Cabecalhos de seguranca ----------------------------------------------------------------------
HSTS_MAX_AGE_SECONDS = 31_536_000  # 1 ano

# --- Rate limiting ------------------------------------------------------------------------------------
# Limite do endpoint de login, por cliente (IP). Sintaxe do SlowAPI/limits: "<n>/<minute|hour|...>".
LOGIN_RATE_LIMIT = "10/minute"
