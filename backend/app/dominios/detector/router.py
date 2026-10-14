"""Rotas do detector (spec 12, spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.dominios.detector import schemas
from app.dominios.detector.servico import ServicoDetector

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["detector"])


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
) -> ServicoDetector:
    return ServicoDetector(datasets, ServicoAnalise(datasets))


Servico = Annotated[ServicoDetector, Depends(_servico)]


def _codigos(
    regras: Annotated[
        str | None,
        Query(description="Códigos separados por vírgula (R1…R11); sem o campo, todas as regras"),
    ] = None,
) -> tuple[str, ...] | None:
    """ "R4,R7" → ("R4", "R7"); código desconhecido → 422 como os demais campos."""
    if regras is None:
        return None
    codigos = [codigo.strip() for codigo in regras.split(",")]
    try:
        return tuple(schemas.CODIGOS_REGRA.validate_python(codigos))
    except ValidationError as erro:
        detalhe = {"type": "literal_error", "loc": ("query", "regras"), "msg": "Regra desconhecida"}
        raise RequestValidationError([detalhe]) from erro


Codigos = Annotated[tuple[str, ...] | None, Depends(_codigos)]


@router.get("/detector", summary="Alertas de dados artificiais com explicação (spec 12)")
def detectar(servico: Servico, dataset_id: str, regras: Codigos) -> schemas.ResultadoDetector:
    return schemas.ResultadoDetector.model_validate(servico.analisar(dataset_id, regras))
