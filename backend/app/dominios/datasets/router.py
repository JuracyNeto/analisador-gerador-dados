"""Rotas HTTP do domínio datasets (spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.dominios.datasets import schemas
from app.dominios.datasets.schemas import (
    AlteracaoTipo,
    DatasetCriado,
    Diagnostico,
    PaginaDataset,
    PedidoLeitura,
    PedidoLimpeza,
    ResultadoLimpeza,
    TipoColuna,
)
from app.dominios.datasets.servico import (
    AcaoLimpeza,
    Limites,
    OpcoesLeitura,
    ServicoDatasets,
    obter_servico_datasets,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])

Servico = Annotated[ServicoDatasets, Depends(obter_servico_datasets)]
TAMANHO_MAXIMO_PAGINA = 500


def _opcoes_leitura(
    separador: Annotated[str | None, Form()] = None,
    decimal: Annotated[Literal[",", "."] | None, Form()] = None,
    codificacao: Annotated[str | None, Form()] = None,
    aba: Annotated[str | None, Form()] = None,
    linha_cabecalho: Annotated[int | None, Form(ge=0)] = None,
) -> OpcoesLeitura:
    """Campos opcionais do formulário que sobrescrevem a detecção (spec 01)."""
    return OpcoesLeitura(separador, decimal, codificacao, aba, linha_cabecalho)


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


@router.post("/{dataset_id}/leitura", summary="Lê de novo o arquivo com outras opções")
def reler(servico: Servico, dataset_id: str, pedido: PedidoLeitura) -> DatasetCriado:
    opcoes = OpcoesLeitura(**pedido.model_dump())
    return DatasetCriado.model_validate(servico.reler(dataset_id, opcoes))


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


def _limites(limite: schemas.Limites | None) -> Limites | None:
    return Limites(limite.min, limite.max) if limite else None


def _acao(acao: schemas.AcaoLimpeza) -> AcaoLimpeza:
    limites = _limites(acao.limites)
    return AcaoLimpeza(acao.problema, acao.acao, acao.coluna, acao.valor, limites, acao.grupo)


def _limites_por_coluna(
    limites: Annotated[
        str | None,
        Query(description='Limites por coluna em JSON: {"idade": {"min": 1, "max": 110}}'),
    ] = None,
) -> dict[str, Limites]:
    try:
        lidos = schemas.LIMITES_POR_COLUNA.validate_json(limites or "{}")
    except ValidationError as erro:
        detalhe = {"type": "json_invalid", "loc": ("query", "limites"), "msg": "JSON inválido"}
        raise RequestValidationError([detalhe]) from erro
    return {coluna: Limites(faixa.min, faixa.max) for coluna, faixa in lidos.items()}


LimitesPorColuna = Annotated[dict[str, Limites], Depends(_limites_por_coluna)]


@router.get("/{dataset_id}/diagnostico", summary="Problemas encontrados (não altera nada)")
def diagnosticar(servico: Servico, dataset_id: str, limites: LimitesPorColuna) -> Diagnostico:
    return Diagnostico.model_validate(servico.diagnosticar(dataset_id, limites))


@router.post("/{dataset_id}/limpeza", summary="Aplica ações de limpeza na versão atual")
def limpar(servico: Servico, dataset_id: str, pedido: PedidoLimpeza) -> ResultadoLimpeza:
    acoes = [_acao(acao) for acao in pedido.acoes]
    return ResultadoLimpeza.model_validate(servico.limpar(dataset_id, acoes))


@router.post("/{dataset_id}/limpeza/desfazer", summary="Desfaz toda a limpeza")
def desfazer_limpeza(servico: Servico, dataset_id: str) -> ResultadoLimpeza:
    return ResultadoLimpeza.model_validate(servico.desfazer_limpeza(dataset_id))
