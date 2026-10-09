"""Rotas HTTP do domínio analise (specs 10 e 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.dominios.analise.schemas import Analise, Bivariada, MatrizCorrelacao, Posicao, Previsao
from app.dominios.analise.servico import OpcoesAnalise, ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["analise"])

MIN_CLASSES = 3
MAX_CLASSES = 30
MAX_TENTATIVAS = 10_000


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
) -> ServicoAnalise:
    return ServicoAnalise(datasets)


Servico = Annotated[ServicoAnalise, Depends(_servico)]


def _opcoes(
    classes: Annotated[int | None, Query(ge=MIN_CLASSES, le=MAX_CLASSES)] = None,
    sucesso: Annotated[str | None, Query(description="Categoria de sucesso (binária)")] = None,
    tentativas: Annotated[
        int | None,
        Query(ge=1, le=MAX_TENTATIVAS, description="Nº de tentativas da Binomial (discreta)"),
    ] = None,
) -> OpcoesAnalise:
    return OpcoesAnalise(classes, sucesso, tentativas)


@router.get("/colunas/{coluna}/analise", summary="Análise univariada da coluna (specs 04–09)")
def analisar(
    servico: Servico,
    dataset_id: str,
    coluna: str,
    opcoes: Annotated[OpcoesAnalise, Depends(_opcoes)],
) -> Analise:
    return Analise.model_validate(servico.analisar(dataset_id, coluna, opcoes))


@router.get("/colunas/{coluna}/posicao", summary='"Onde está meu valor?" (spec 06)')
def posicao(
    servico: Servico,
    dataset_id: str,
    coluna: str,
    valor: float,
    tipo: Literal["quartil", "decil", "percentil"] = "quartil",
) -> Posicao:
    return Posicao.model_validate(servico.posicao(dataset_id, coluna, valor, tipo))


ColunaX = Annotated[str, Query(description="Coluna X (explica)")]
ColunaY = Annotated[str, Query(description="Coluna Y (é explicada)")]


@router.get("/bivariada", summary="Correlação e regressão de duas colunas (spec 10)")
def bivariada(servico: Servico, dataset_id: str, x: ColunaX, y: ColunaY) -> Bivariada:
    return Bivariada.model_validate(servico.bivariada(dataset_id, x, y))


@router.get("/bivariada/prever", summary="Prever Y para um valor de X (spec 10)")
def prever(servico: Servico, dataset_id: str, x: ColunaX, y: ColunaY, valor: float) -> Previsao:
    return Previsao.model_validate(servico.prever(dataset_id, x, y, valor))


@router.get("/correlacoes", summary="Matriz de correlação das colunas numéricas (spec 10)")
def correlacoes(servico: Servico, dataset_id: str) -> MatrizCorrelacao:
    return MatrizCorrelacao.model_validate(servico.correlacoes(dataset_id))
