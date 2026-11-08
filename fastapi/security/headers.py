"""Middleware que adiciona os cabecalhos de seguranca HTTP a todas as respostas da API."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import HSTS_MAX_AGE_SECONDS

# A API so devolve JSON: nenhuma origem de script, estilo, imagem ou frame e necessaria.
API_CSP = "default-src 'none'; frame-ancestors 'none'"

# O Swagger UI (/docs) e o ReDoc (/redoc) carregam scripts e estilos de um CDN e usam scripts inline,
# entao a politica restritiva acima os quebraria. Esta versao libera so o necessario para essas paginas
# e continua proibindo ser embutida em frames. Em producao, o ideal e desabilitar /docs e /redoc.
DOCS_CSP = (
    "default-src 'none'; "
    "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com 'unsafe-inline'; "
    "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.redoc.ly; "
    "font-src https://fonts.gstatic.com; "
    "connect-src 'self'; "
    "worker-src blob:; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = {"/docs", "/docs/oauth2-redirect", "/redoc"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = f"max-age={HSTS_MAX_AGE_SECONDS}; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = DOCS_CSP if request.url.path in DOCS_PATHS else API_CSP
        return response
