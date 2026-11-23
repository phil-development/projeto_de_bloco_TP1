from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from config import ALLOWED_ORIGINS, API_TITLE, API_VERSION, DATABASE_PATH
from routes import api_router
from security.headers import SecurityHeadersMiddleware
from security.rate_limit import limiter, rate_limit_exceeded_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_engine criaria um arquivo vazio se ele nao existisse; falhar aqui da uma mensagem clara.
    if not DATABASE_PATH.exists():
        raise RuntimeError(
            f"Banco nao encontrado em {DATABASE_PATH}. Rode 'python sqlite_database.py' dentro de fastapi/."
        )
    yield


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="API de classificacao de intencao de tickets de suporte ao cliente.",
    lifespan=lifespan,
)

# Rate limiting (SlowAPI): o limiter precisa estar em app.state e o 429 tem handler proprio.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Ordem dos middlewares: o ultimo adicionado e o mais externo. Os cabecalhos de seguranca ficam por fora
# do CORS para tambem cobrirem respostas de preflight e respostas de erro (401, 422, 429).
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # allowlist explicita, sem "*"
    allow_credentials=False,  # a autenticacao e por header Authorization (Bearer), nao por cookie
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(api_router)
