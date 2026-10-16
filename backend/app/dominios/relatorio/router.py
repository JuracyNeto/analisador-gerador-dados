"""Rota do relatório HTML (spec 13, spec 14). Sem lógica: valida → serviço → HTML."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.core.config import obter_configuracao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.dominios.detector.servico import ServicoDetector
from app.dominios.gerador.servico import (
    Gerado,
    RepositorioGerados,
    ServicoGerador,
    obter_repositorio_gerados,
)
from app.dominios.relatorio.servico import SECOES_PADRAO, PedidoRelatorio, Secao, ServicoRelatorio

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["relatorio"])


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
    gerados: Annotated[RepositorioGerados[Gerado], Depends(obter_repositorio_gerados)],
) -> ServicoRelatorio:
    analise = ServicoAnalise(datasets)
    gerador = ServicoGerador(datasets, analise, gerados, obter_configuracao())
    return ServicoRelatorio(datasets, analise, gerador, ServicoDetector(datasets, analise))


def _pedido(
    secoes: Annotated[list[Secao] | None, Query(description="Seções do relatório")] = None,
    colunas: Annotated[list[str] | None, Query(description="Colunas analisadas")] = None,
    offline: Annotated[
        bool, Query(description="Embute o plotly.js (funciona sem internet)")
    ] = False,
    gerado: Annotated[
        str | None, Query(description="Geração mostrada na seção Gerador (sem ela, a seção sai)")
    ] = None,
) -> PedidoRelatorio:
    return PedidoRelatorio(
        secoes=tuple(secoes) if secoes else SECOES_PADRAO,
        colunas=tuple(colunas) if colunas else None,
        offline=offline,
        gerado=gerado,
    )


@router.get("/relatorio", response_class=HTMLResponse, summary="Relatório em HTML")
def gerar_relatorio(
    servico: Annotated[ServicoRelatorio, Depends(_servico)],
    dataset_id: str,
    pedido: Annotated[PedidoRelatorio, Depends(_pedido)],
) -> HTMLResponse:
    return HTMLResponse(servico.gerar(dataset_id, pedido))
