"""Tabelas do banco mapeadas com SQLModel. Espelham o schema criado em sqlite_database.py."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    # SQLite nao guarda fuso; o projeto padroniza em UTC sem tzinfo (igual ao script de seed).
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserRecord(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = "user"
    created_at: datetime = Field(default_factory=_utcnow)


class PredictionRecord(SQLModel, table=True):
    __tablename__ = "predictions"

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    text: str
    intent: str
    confidence: float
    model_version: str
    created_at: datetime = Field(default_factory=_utcnow)
