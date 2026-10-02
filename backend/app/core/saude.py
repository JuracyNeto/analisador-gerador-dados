"""Endpoint de verificação de saúde da API."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Configuracao, obter_configuracao

router = APIRouter(tags=["sistema"])


class Saude(BaseModel):
    status: str
    versao: str


@router.get("/saude", summary="Verifica se a API está no ar")
def verificar_saude(config: Annotated[Configuracao, Depends(obter_configuracao)]) -> Saude:
    return Saude(status="ok", versao=config.versao)
