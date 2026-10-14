"""Demonstração do M3 pela API: gerar k valores preservando a coluna, anexar e a R1 disparar.

`alturas_reais.txt` tem 400 linhas; com as 21 geradas, k = max(10, ⌊421/20⌋) = 21 e o bloco
anexado ocupa as linhas 401–421, com a média e o DP exatos do restante (spec 11, spec 12).
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

GERADOS = 21


def _gerar_e_anexar(cliente: TestClient, coluna: str, semente: int) -> str:
    criado = cliente.post("/api/datasets/exemplo", params={"arquivo": "alturas_reais.txt"})
    dataset_id = str(criado.json()["dataset_id"])
    pedido = {
        "origem": {"dataset_id": dataset_id, "coluna": coluna},
        "x": GERADOS,
        "modo": "preservar",
        "semente": semente,
    }
    gerado = cliente.post("/api/gerador/univariado", json=pedido).json()
    anexado = cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar",
        json={"modo": "anexar", "dataset_id": dataset_id},
    )
    assert anexado.json()["n_linhas"] == 421
    return dataset_id


def _avisos_r1(cliente: TestClient, dataset_id: str) -> list[dict[str, Any]]:
    resposta = cliente.get(f"/api/datasets/{dataset_id}/detector", params={"regras": "R1"})
    assert resposta.status_code == 200
    avisos: list[dict[str, Any]] = resposta.json()["avisos"]
    return avisos


@pytest.mark.parametrize("semente", [5, 7, 14])
def test_pesos_gerados_e_anexados_disparam_o_bloco_alinhado(
    cliente: TestClient, semente: int
) -> None:
    dataset_id = _gerar_e_anexar(cliente, "peso_kg", semente)

    (aviso,) = _avisos_r1(cliente, dataset_id)

    assert aviso["colunas"] == ["peso_kg"]
    assert aviso["severidade"] == "alta"
    assert aviso["resumo"].startswith("Um bloco de 21 linhas (401–421) tem média e desvio")
    assert aviso["exemplo"]["texto"].startswith("Linhas 401 a 421: média ")
    assert aviso["figura"]["id"] == "blocos"


def test_alturas_em_centimetros_nao_disparam(cliente: TestClient) -> None:
    """Arredondado a 1 cm (DP 0,09 m), o bloco perde a média exata: o acaso chega tão perto."""
    dataset_id = _gerar_e_anexar(cliente, "altura_m", 0)

    assert _avisos_r1(cliente, dataset_id) == []
