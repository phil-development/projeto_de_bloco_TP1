"""Cria e popula o banco SQLite da API (fastapi/database.db) usando apenas o modulo sqlite3.

Uso, de dentro da pasta fastapi/:

    python sqlite_database.py            # cria o que faltar e semeia os dados se o banco estiver vazio
    python sqlite_database.py --reset    # apaga o arquivo e recria tudo do zero

Este script e o unico lugar do projeto que usa SQL direto. A API consulta o banco exclusivamente
via SQLModel (ver db.py e models/tables.py), sem SQL raw.
"""

import argparse
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from config import DATABASE_PATH

# Valores aceitos pelo enum Intent em models/predict.py.
INTENTS = (
    "Technical issue",
    "Billing inquiry",
    "Cancellation request",
    "Product inquiry",
    "Refund request",
)

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id      INTEGER NOT NULL REFERENCES users (id),
    text          TEXT    NOT NULL CHECK (length(text) BETWEEN 3 AND 2000),
    intent        TEXT    NOT NULL CHECK (intent IN ({", ".join(repr(i) for i in INTENTS)})),
    confidence    REAL    NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    model_version TEXT    NOT NULL,
    created_at    TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_predictions_owner_id ON predictions (owner_id);
"""

# Hashes bcrypt (senha em claro nunca e armazenada).
# admin    -> "Infnet@2025"   (mesmo hash que ficava em security/users.py no TP1)
# analista -> "Analista@2025"
SEED_USERS = (
    ("admin", "$2b$12$amXiNVuFpoj.05sIx9E.BeoPI.xU.osMtVU.1/NvfJRngJ5EreFMm", "admin"),
    ("analista", "$2b$12$R4xiCxmxZliY9LFV5kpVfOamNsI/sPe1dimuUi2.yO5J1E1oJXkly", "user"),
)

# (username do dono, texto, intencao, confianca, horas atras). Dados de exemplo, nao saida de modelo.
SEED_PREDICTIONS = (
    ("admin", "My laptop stopped charging after the last update.", "Technical issue", 0.91, 30),
    ("admin", "I was charged twice for the same subscription this month.", "Billing inquiry", 0.88, 26),
    ("analista", "Please cancel my account effective immediately.", "Cancellation request", 0.95, 12),
    ("analista", "I want my money back, the product arrived damaged.", "Refund request", 0.84, 6),
    ("analista", "Does the premium plan include offline mode?", "Product inquiry", 0.79, 1),
)

SEED_MODEL_VERSION = "seed-fixture"
# Mesmo formato que o SQLAlchemy/SQLModel usa ao ler e gravar datetime no SQLite (UTC, sem fuso).
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def seed_users(conn: sqlite3.Connection) -> None:
    now = utc_now().strftime(DATETIME_FORMAT)
    conn.executemany(
        "INSERT OR IGNORE INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        [(username, password_hash, role, now) for username, password_hash, role in SEED_USERS],
    )


def seed_predictions(conn: sqlite3.Connection) -> bool:
    """Insere as predictions de exemplo apenas se a tabela estiver vazia (evita duplicar a cada execucao)."""
    if conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0] > 0:
        return False

    owner_ids = dict(conn.execute("SELECT username, id FROM users").fetchall())
    now = utc_now()
    rows = [
        (
            owner_ids[username],
            text,
            intent,
            confidence,
            SEED_MODEL_VERSION,
            (now - timedelta(hours=hours_ago)).strftime(DATETIME_FORMAT),
        )
        for username, text, intent, confidence, hours_ago in SEED_PREDICTIONS
    ]
    conn.executemany(
        "INSERT INTO predictions (owner_id, text, intent, confidence, model_version, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    return True


def print_summary(conn: sqlite3.Connection) -> None:
    print(f"Banco: {DATABASE_PATH}")
    rows = conn.execute(
        "SELECT u.id, u.username, u.role, COUNT(p.id) "
        "FROM users u LEFT JOIN predictions p ON p.owner_id = u.id "
        "GROUP BY u.id ORDER BY u.id"
    ).fetchall()
    for user_id, username, role, total in rows:
        print(f"  usuario #{user_id} {username!r} ({role}): {total} prediction(s)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria e popula o banco SQLite da API.")
    parser.add_argument("--reset", action="store_true", help="apaga o banco existente antes de recriar")
    args = parser.parse_args()

    if args.reset and DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        print(f"Banco anterior removido: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        create_schema(conn)
        with conn:  # uma unica transacao para o seed: ou entra tudo ou nada
            seed_users(conn)
            seeded = seed_predictions(conn)
        print_summary(conn)
        if not seeded:
            print("Predictions ja existiam; seed de predictions ignorado (use --reset para recriar).")
    finally:
        conn.close()

    try:
        os.chmod(DATABASE_PATH, 0o600)  # o arquivo guarda hashes de senha: so o dono le/escreve
    except OSError:
        pass  # em alguns sistemas de arquivos (ex.: Windows) o chmod nao se aplica


if __name__ == "__main__":
    main()