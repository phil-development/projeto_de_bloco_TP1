"""Rate limiting com SlowAPI.

O limiter fica neste modulo (e nao no main.py) para que as rotas possam importa-lo sem import circular.
O contador e mantido em memoria, por processo, e a chave de cada cliente e o IP de origem da conexao.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    # Mensagem generica, no mesmo formato {"detail": ...} dos demais erros da API.
    # Retry-After fixo em 60 s: a janela do limite de login e de 1 minuto.
    return JSONResponse(
        status_code=429,
        content={"detail": "Muitas requisicoes. Tente novamente em instantes."},
        headers={"Retry-After": "60"},
    )
