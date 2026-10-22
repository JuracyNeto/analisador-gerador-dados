"""Demonstração do M3 pela API: gerar k valores preservando a coluna, anexar e a R1 disparar.

`alturas_reais.txt` tem 400 linhas; com as 21 geradas, k = max(10, ⌊421/20⌋) = 21 e o bloco
anexado ocupa as linhas 401–421, com a média e o DP exatos do restante (spec 11, spec 12).
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.dominios.detector.apoio import exemplo_principal_limpo

GERADOS = 21


def _anexar(
    cliente: TestClient, dataset_id: str, coluna: str, semente: int, quantidade: int = GERADOS
) -> int:
    """Gera `quantidade` valores preservando a coluna e os anexa; devolve as linhas do arquivo."""
    pedido = {
        "origem": {"dataset_id": dataset_id, "coluna": coluna},
        "x": quantidade,
        "modo": "preservar",
        "semente": semente,
    }
    gerado = cliente.post("/api/gerador/univariado", json=pedido).json()
    anexado = cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar",
        json={"modo": "anexar", "dataset_id": dataset_id},
    )
    return int(anexado.json()["n_linhas"])


def _gerar_e_anexar(cliente: TestClient, coluna: str, semente: int) -> str:
    criado = cliente.post("/api/datasets/exemplo", params={"arquivo": "alturas_reais.txt"})
    dataset_id = str(criado.json()["dataset_id"])
    assert _anexar(cliente, dataset_id, coluna, semente) == 421
    return dataset_id


def _avisos(cliente: TestClient, dataset_id: str, regra: str) -> list[dict[str, Any]]:
    resposta = cliente.get(f"/api/datasets/{dataset_id}/detector", params={"regras": regra})
    assert resposta.status_code == 200
    avisos: list[dict[str, Any]] = resposta.json()["avisos"]
    return avisos


@pytest.mark.parametrize("semente", [5, 7, 14])
def test_pesos_gerados_e_anexados_disparam_o_bloco_alinhado(
    cliente: TestClient, semente: int
) -> None:
    dataset_id = _gerar_e_anexar(cliente, "peso_kg", semente)

    (aviso,) = _avisos(cliente, dataset_id, "R1")

    assert aviso["colunas"] == ["peso_kg"]
    assert aviso["severidade"] == "alta"
    assert aviso["resumo"].startswith("Um bloco de 21 linhas (401–421) tem média e desvio")
    assert aviso["exemplo"]["texto"].startswith("Linhas 401 a 421: média ")
    assert aviso["exemplo"]["linhas"] == list(range(401, 422))
    assert aviso["exemplo"]["total_linhas"] == 21
    assert aviso["figura"]["id"] == "blocos"


def test_alturas_em_centimetros_nao_disparam(cliente: TestClient) -> None:
    """Arredondado a 1 cm (DP 0,09 m), o bloco perde a média exata: o acaso chega tão perto."""
    dataset_id = _gerar_e_anexar(cliente, "altura_m", 0)

    assert _avisos(cliente, dataset_id, "R1") == []


@pytest.mark.parametrize("semente", [5, 7, 14])
def test_pesos_anexados_ao_exemplo_principal_limpo_disparam(
    cliente: TestClient, semente: int
) -> None:
    """Com 221 linhas e 21 anexadas, k = 12: o bloco é pego pelo fim do arquivo (D148)."""
    dataset_id = exemplo_principal_limpo(cliente)
    _anexar(cliente, dataset_id, "peso_kg", semente)

    (aviso,) = _avisos(cliente, dataset_id, "R1")

    assert aviso["resumo"].startswith("Um bloco de 21 linhas (")
    assert aviso["severidade"] == "alta"


@pytest.mark.parametrize(
    ("coluna", "semente"), [("peso_kg", 0), ("peso_kg", 2), ("idade", 0), ("altura_m", 0)]
)
def test_valores_anexados_nao_viram_duplicatas(
    cliente: TestClient, coluna: str, semente: int
) -> None:
    """As linhas anexadas só têm a coluna gerada; a R5 as via como quase iguais (achado D-b)."""
    dataset_id = exemplo_principal_limpo(cliente)
    _anexar(cliente, dataset_id, coluna, semente, quantidade=30)

    assert _avisos(cliente, dataset_id, "R5") == []
