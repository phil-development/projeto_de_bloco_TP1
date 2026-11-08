"""Configuracao compartilhada dos testes.

Rodar de dentro de fastapi/ (precisa de: pip install pytest httpx):

    python -m pytest tests -v

Os testes usam uma COPIA de database.db em pasta temporaria; o banco real nao e alterado.
Pressupoe o seed de sqlite_database.py.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

FASTAPI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FASTAPI_DIR))

# O banco de teste precisa ser definido antes de importar config/main.
_tmp_dir = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = str(Path(_tmp_dir) / "database.db")
shutil.copy(FASTAPI_DIR / "database.db", os.environ["DATABASE_PATH"])

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402
from security.rate_limit import limiter  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
    shutil.rmtree(_tmp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Zera os contadores do SlowAPI antes de cada teste: varios testes fazem login e, sem isso,
    o limite de 10/min do /auth/token faria testes nao relacionados falharem com 429."""
    limiter.reset()
    yield
