"""Rotas HTTP do domínio analise (spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.dominios.analise.schemas import Analise, Posicao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets

router = APIRouter(prefix="/datasets/{dataset_id}/colunas/{coluna}", tags=["analise"])

MIN_CLASSES = 3
MAX_CLASSES = 30


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
) -> ServicoAnalise:
    return ServicoAnalise(datasets)


Servico = Annotated[ServicoAnalise, Depends(_servico)]


@router.get("/analise", summary="Análise univariada da coluna (specs 04–07)")
def analisar(
    servico: Servico,
    dataset_id: str,
    coluna: str,
    classes: Annotated[int | None, Query(ge=MIN_CLASSES, le=MAX_CLASSES)] = None,
    sucesso: Annotated[str | None, Query(description="Categoria de sucesso (binária)")] = None,
) -> Analise:
    return Analise.model_validate(servico.analisar(dataset_id, coluna, classes, sucesso))


@router.get("/posicao", summary='"Onde está meu valor?" (spec 06)')
def posicao(
    servico: Servico,
    dataset_id: str,
    coluna: str,
    valor: float,
    tipo: Literal["quartil", "decil", "percentil"] = "quartil",
) -> Posicao:
    return Posicao.model_validate(servico.posicao(dataset_id, coluna, valor, tipo))
