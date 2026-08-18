from fastapi import FastAPI

from config import API_TITLE, API_VERSION
from routes import api_router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="API de classificacao de intencao de tickets de suporte ao cliente.",
)

app.include_router(api_router)
