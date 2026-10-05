"""Rotas HTTP do domínio datasets (spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile, status

from app.dominios.datasets.schemas import (
    AlteracaoTipo,
    DatasetCriado,
    PaginaDataset,
    TipoColuna,
)
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets, obter_servico_datasets

router = APIRouter(prefix="/datasets", tags=["datasets"])

Servico = Annotated[ServicoDatasets, Depends(obter_servico_datasets)]
TAMANHO_MAXIMO_PAGINA = 500


def _opcoes_leitura(
    separador: Annotated[str | None, Form()] = None,
    decimal: Annotated[Literal[",", "."] | None, Form()] = None,
    codificacao: Annotated[str | None, Form()] = None,
    aba: Annotated[str | None, Form()] = None,
    tem_cabecalho: Annotated[bool | None, Form()] = None,
) -> OpcoesLeitura:
    """Campos opcionais do formulário que sobrescrevem a detecção (spec 01)."""
    return OpcoesLeitura(separador, decimal, codificacao, aba, tem_cabecalho)


Opcoes = Annotated[OpcoesLeitura, Depends(_opcoes_leitura)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Importa um arquivo de dados")
def importar(servico: Servico, arquivo: UploadFile, opcoes: Opcoes) -> DatasetCriado:
    nome = arquivo.filename or "arquivo"
    return DatasetCriado.model_validate(servico.importar(arquivo.file.read(), nome, opcoes))


@router.post(
    "/exemplo",
    status_code=status.HTTP_201_CREATED,
    summary="Importa o arquivo de exemplo (pesquisa_saude.txt)",
)
def importar_exemplo(servico: Servico) -> DatasetCriado:
    return DatasetCriado.model_validate(servico.importar_exemplo())


@router.get("/{dataset_id}", summary="Resumo do dataset e linhas paginadas")
def obter_pagina(
    servico: Servico,
    dataset_id: str,
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamanho: Annotated[int, Query(ge=1, le=TAMANHO_MAXIMO_PAGINA)] = 20,
    versao: Literal["atual", "original"] = "atual",
) -> PaginaDataset:
    return PaginaDataset.model_validate(servico.pagina(dataset_id, pagina, tamanho, versao))


@router.delete(
    "/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Descarta o dataset"
)
def remover(servico: Servico, dataset_id: str) -> Response:
    servico.remover(dataset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{dataset_id}/colunas", summary="Tipo de cada coluna, com o motivo")
def listar_colunas(servico: Servico, dataset_id: str) -> list[TipoColuna]:
    return [TipoColuna.model_validate(c) for c in servico.colunas(dataset_id)]


@router.patch("/{dataset_id}/colunas/{coluna}", summary="Corrige o tipo de uma coluna")
def alterar_tipo(
    servico: Servico, dataset_id: str, coluna: str, alteracao: AlteracaoTipo
) -> TipoColuna:
    novo = servico.alterar_tipo(dataset_id, coluna, alteracao.tipo, alteracao.categorias_ordem)
    return TipoColuna.model_validate(novo)
