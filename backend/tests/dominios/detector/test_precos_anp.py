"""Detector numa amostra real (preços de combustíveis da ANP em Goiás, D139): retrato.

Preços terminam em 9 de propósito (6,99): a R9 avisa e o "pode ser normal" fala de preços. A
ordem alterna gasolina e etanol em cada posto (R11), informativa porque as linhas seguem a data
da coleta. Nenhuma suspeita alta.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

RETRATO = {("R9", "atencao", ("Valor de Venda",)), ("R11", "info", ("Valor de Venda",))}


@pytest.fixture
def avisos(cliente: TestClient, precos_anp: str) -> list[dict[str, Any]]:
    corpo: dict[str, Any] = cliente.get(f"/api/datasets/{precos_anp}/detector").json()
    return list(corpo["avisos"])


def test_retrato_dos_alertas_da_anp(avisos: list[dict[str, Any]]) -> None:
    alertas = {(a["regra"], a["severidade"], tuple(a["colunas"])) for a in avisos}

    assert alertas == RETRATO


def test_precos_terminados_em_9_sao_explicados(avisos: list[dict[str, Any]]) -> None:
    (ultimo_digito,) = [aviso for aviso in avisos if aviso["regra"] == "R9"]

    assert "o 9 aparece" in ultimo_digito["resumo"]
    assert ultimo_digito["pode_ser_normal"].startswith("…são preços (ex.: 5,99)")
