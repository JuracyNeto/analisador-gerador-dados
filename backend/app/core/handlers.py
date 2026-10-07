"""Converte exceções em respostas JSON {codigo, mensagem, sugestao}."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.erros import ErroAplicacao

logger = logging.getLogger(__name__)


def _resposta(status: HTTPStatus, codigo: str, mensagem: str, sugestao: str) -> JSONResponse:
    conteudo = {"codigo": codigo, "mensagem": mensagem, "sugestao": sugestao}
    return JSONResponse(status_code=status, content=conteudo)


def _campos_invalidos(erro: Exception) -> str:
    if not isinstance(erro, RequestValidationError):
        return ""
    return ", ".join(str(item["loc"][-1]) for item in erro.errors())


def _tratar_erro_aplicacao(_: Request, erro: Exception) -> JSONResponse:
    if not isinstance(erro, ErroAplicacao):
        raise erro
    return JSONResponse(status_code=erro.status, content=erro.como_dict())


def _tratar_validacao(_: Request, erro: Exception) -> JSONResponse:
    return _resposta(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "ENTRADA_INVALIDA",
        f"Alguns campos não estão corretos: {_campos_invalidos(erro)}.",
        "Confira os valores informados e tente novamente.",
    )


def _tratar_inesperado(_: Request, erro: Exception) -> JSONResponse:
    logger.error("Erro inesperado", exc_info=erro)
    return _resposta(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "ERRO_INTERNO",
        "Algo deu errado do nosso lado.",
        "Tente novamente. Se continuar, reinicie o servidor.",
    )


def registrar_handlers(app: FastAPI) -> None:
    """Registra os tratadores de erro centralizados (sem try/except nos routers)."""
    app.add_exception_handler(ErroAplicacao, _tratar_erro_aplicacao)
    app.add_exception_handler(RequestValidationError, _tratar_validacao)
    app.add_exception_handler(Exception, _tratar_inesperado)
