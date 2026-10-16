"""Detector num cadastro com tipos variados e nada plantado (D131): retrato do comportamento.

Os alertas que aparecem são os esperados em dados assim: um valor em reais na ponta de uma cauda
muito longa (R7 atenção; as cercas ajustadas à assimetria tiram os demais, D136), valores das
pontas de contagens, do saldo, da temperatura e do valor de compra (R7 informativo) e a
temperatura diária, uma série no tempo (R11 informativo, D137). Descontos de uma tabela fixa
(5 valores) não vão para o último dígito (D134). Códigos, datas e categorias nunca viram alerta.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets
from app.dominios.detector.regras import r06_temporal
from app.dominios.detector.servico import ServicoDetector

NUMERICAS = {
    "valor_compra",
    "valor_reais",
    "desconto",
    "satisfacao",
    "itens",
    "saldo",
    "temperatura",
}
RETRATO = {
    ("R7", "atencao", ("valor_reais",)),
    ("R7", "info", ("itens",)),
    ("R7", "info", ("saldo",)),
    ("R7", "info", ("temperatura",)),
    ("R7", "info", ("valor_compra",)),
    ("R11", "info", ("temperatura",)),
}


@pytest.fixture
def resultado(cliente: TestClient, cadastro_variado: str) -> dict[str, Any]:
    corpo: dict[str, Any] = cliente.get(f"/api/datasets/{cadastro_variado}/detector").json()
    return corpo


def test_todas_as_regras_se_aplicam(resultado: dict[str, Any]) -> None:
    assert resultado["resumo"]["regras_verificadas"] == 11
    assert "R6" not in {item["regra"] for item in resultado["nao_aplicadas"]}


def test_sem_suspeita_alta_e_so_em_colunas_numericas(resultado: dict[str, Any]) -> None:
    avisos = resultado["avisos"]

    assert {aviso["severidade"] for aviso in avisos} <= {"atencao", "info"}
    assert {coluna for aviso in avisos for coluna in aviso["colunas"]} <= NUMERICAS


def test_retrato_dos_alertas(resultado: dict[str, Any]) -> None:
    alertas = {(a["regra"], a["severidade"], tuple(a["colunas"])) for a in resultado["avisos"]}

    assert alertas == RETRATO


def test_linha_do_tempo_e_o_dia_e_nao_o_nascimento(
    servico_datasets: ServicoDatasets, cadastro_variado: str
) -> None:
    tabela = ServicoDetector(servico_datasets, ServicoAnalise(servico_datasets)).tabela(
        cadastro_variado
    )

    linha_do_tempo = r06_temporal.linha_do_tempo(tabela)

    assert linha_do_tempo is not None
    assert linha_do_tempo.coluna == "dia"
