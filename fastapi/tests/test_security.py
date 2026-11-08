"""Testes dos headers de seguranca, do CORS (allowlist) e do rate limit do /auth/token.

O fixture `client` e o reset dos contadores do SlowAPI vem de conftest.py.
"""

import pytest
from fastapi.testclient import TestClient

from config import ALLOWED_ORIGINS, LOGIN_RATE_LIMIT, parse_allowed_origins
from main import app

ALLOWED_ORIGIN = ALLOWED_ORIGINS[0]
EVIL_ORIGIN = "https://evil.example"
LIMIT = int(LOGIN_RATE_LIMIT.split("/")[0])

SECURITY_HEADERS = (
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "content-security-policy",
)


def bad_login(client: TestClient):
    return client.post("/auth/token", data={"username": "admin", "password": "senha-errada"})


# --- Headers de seguranca -----------------------------------------------------------------------


def test_security_headers_on_api_response(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["strict-transport-security"].startswith("max-age=")
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    csp = response.headers["content-security-policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_security_headers_on_error_response(client):
    response = client.get("/predictions")  # sem token -> 401
    assert response.status_code == 401
    for header in SECURITY_HEADERS:
        assert header in response.headers


def test_docs_page_uses_relaxed_csp_but_blocks_framing(client):
    response = client.get("/docs")
    assert response.status_code == 200
    csp = response.headers["content-security-policy"]
    assert "cdn.jsdelivr.net" in csp
    assert "frame-ancestors 'none'" in csp
    assert response.headers["x-frame-options"] == "DENY"


# --- CORS ---------------------------------------------------------------------------------------


def test_cors_allows_listed_origin(client):
    response = client.get("/health", headers={"Origin": ALLOWED_ORIGIN})
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_cors_does_not_allow_unlisted_origin(client):
    response = client.get("/health", headers={"Origin": EVIL_ORIGIN})
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_for_listed_origin(client):
    response = client.options(
        "/predict",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "access-control-allow-credentials" not in response.headers


def test_cors_preflight_for_unlisted_origin_is_refused(client):
    response = client.options(
        "/predict",
        headers={"Origin": EVIL_ORIGIN, "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_wildcard_origin_is_refused_in_config():
    with pytest.raises(ValueError):
        parse_allowed_origins("*")
    with pytest.raises(ValueError):
        parse_allowed_origins("https://app.example,*")


def test_origin_parsing_trims_spaces_and_trailing_slash():
    assert parse_allowed_origins(" https://a.example/ , https://b.example ") == [
        "https://a.example",
        "https://b.example",
    ]


# --- Rate limiting em /auth/token ---------------------------------------------------------------


def test_login_is_limited_to_10_requests_per_minute(client):
    for _ in range(LIMIT):
        assert bad_login(client).status_code == 401

    blocked = bad_login(client)
    assert blocked.status_code == 429
    assert blocked.json() == {"detail": "Muitas requisicoes. Tente novamente em instantes."}
    assert blocked.headers["retry-after"] == "60"
    for header in SECURITY_HEADERS:  # o 429 tambem recebe os headers de seguranca
        assert header in blocked.headers


def test_correct_password_is_also_blocked_after_the_limit(client):
    for _ in range(LIMIT):
        bad_login(client)

    response = client.post("/auth/token", data={"username": "admin", "password": "Infnet@2025"})
    assert response.status_code == 429


def test_limit_is_per_client(client):
    for _ in range(LIMIT):
        bad_login(client)
    assert bad_login(client).status_code == 429

    other_client = TestClient(app, client=("203.0.113.7", 50000))  # outro IP de origem
    assert bad_login(other_client).status_code == 401


def test_other_routes_are_not_rate_limited(client):
    for _ in range(LIMIT + 5):
        assert client.get("/health").status_code == 200
