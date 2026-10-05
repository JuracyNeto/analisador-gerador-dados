"""Rota do relatório HTML (spec 13, spec 14). Sem lógica: valida → serviço → HTML."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.dominios.relatorio.servico import SECOES_M1, PedidoRelatorio, Secao, ServicoRelatorio

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["relatorio"])


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
) -> ServicoRelatorio:
    return ServicoRelatorio(datasets, ServicoAnalise(datasets))


def _pedido(
    secoes: Annotated[list[Secao] | None, Query(description="Seções do mini relatório")] = None,
    colunas: Annotated[list[str] | None, Query(description="Colunas analisadas")] = None,
    offline: Annotated[
        bool, Query(description="Embute o plotly.js (funciona sem internet)")
    ] = False,
) -> PedidoRelatorio:
    return PedidoRelatorio(
        secoes=tuple(secoes) if secoes else SECOES_M1,
        colunas=tuple(colunas) if colunas else None,
        offline=offline,
    )


@router.get("/relatorio", response_class=HTMLResponse, summary="Mini relatório em HTML")
def gerar_relatorio(
    servico: Annotated[ServicoRelatorio, Depends(_servico)],
    dataset_id: str,
    pedido: Annotated[PedidoRelatorio, Depends(_pedido)],
) -> HTMLResponse:
    return HTMLResponse(servico.gerar(dataset_id, pedido))
