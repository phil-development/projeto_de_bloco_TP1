"""Engine e sessao SQLModel. Todas as consultas da API passam por aqui, sem SQL raw.

O schema e criado por sqlite_database.py; a API nao chama create_all.
"""

from collections.abc import Iterator

from sqlmodel import Session, create_engine

from config import DATABASE_URL

# check_same_thread=False: o FastAPI executa rotas sincronas em threads de um pool.
# Cada requisicao abre a propria Session (get_session), entao nenhuma conexao e compartilhada.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
