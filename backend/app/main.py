"""Ponto de entrada: monta a aplicação FastAPI (monólito em camadas por domínio, ADR 0007)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import saude
from app.core.config import obter_configuracao
from app.core.handlers import registrar_handlers

PREFIXO_API = "/api"


def create_app() -> FastAPI:
    """Fábrica da aplicação: middlewares, handlers e routers dos domínios."""
    config = obter_configuracao()
    app = FastAPI(title=config.nome_app, version=config.versao)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origens,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    registrar_handlers(app)
    app.include_router(saude.router, prefix=PREFIXO_API)
    return app


app = create_app()
