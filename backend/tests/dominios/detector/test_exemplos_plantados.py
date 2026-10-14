"""Os arquivos de demonstração disparam as regras esperadas (spec 12, spec 17, D124)."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


def _detector(cliente: TestClient, arquivo: str) -> dict[str, Any]:
    criado = cliente.post("/api/datasets/exemplo", params={"arquivo": arquivo}).json()
    resposta = cliente.get(f"/api/datasets/{criado['dataset_id']}/detector")
    assert resposta.status_code == 200
    corpo: dict[str, Any] = resposta.json()
    return corpo


def _por_regra(corpo: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    return {(a["regra"], tuple(a["colunas"])): a for a in corpo["avisos"]}


@pytest.fixture
def plantadas(cliente: TestClient) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    return _por_regra(_detector(cliente, "alturas_plantadas.txt"))


def test_alturas_reais_sem_alertas_de_atencao_ou_alta(cliente: TestClient) -> None:
    corpo = _detector(cliente, "alturas_reais.txt")

    assert {a["severidade"] for a in corpo["avisos"]} <= {"info"}
    assert corpo["resumo"]["regras_verificadas"] == 9


def test_bloco_alinhado_nas_alturas(plantadas: dict[Any, dict[str, Any]]) -> None:
    aviso = plantadas[("R1", ("altura_m",))]

    assert aviso["severidade"] == "alta"
    assert aviso["exemplo"]["linhas"] == list(range(181, 201))
    assert aviso["figura"]["id"] == "blocos"


@pytest.mark.parametrize(
    ("regra", "coluna", "severidade"),
    [
        ("R3", "peso_kg", "atencao"),
        ("R4", "altura_m", "atencao"),
        ("R10", "cintura_cm", "info"),
    ],
)
def test_regras_de_coluna_plantadas(
    plantadas: dict[Any, dict[str, Any]], regra: str, coluna: str, severidade: str
) -> None:
    assert plantadas[(regra, (coluna,))]["severidade"] == severidade


def test_inteiros_seguidos_nas_linhas_plantadas(plantadas: dict[Any, dict[str, Any]]) -> None:
    assert plantadas[("R3", ("peso_kg",))]["exemplo"]["linhas"] == list(range(61, 71))


def test_linhas_iguais_em_sequencia_dao_suspeita_alta(
    plantadas: dict[Any, dict[str, Any]],
) -> None:
    aviso = plantadas[("R5", ())]

    assert aviso["severidade"] == "alta"
    linhas = aviso["exemplo"]["linhas"]
    assert len(linhas) == 4
    assert linhas == list(range(linhas[0], linhas[0] + 4))


def test_vendas_com_correlacao_puxada_e_semanas_copiadas(cliente: TestClient) -> None:
    avisos = _por_regra(_detector(cliente, "vendas_correlacao_puxada.txt"))

    puxada = avisos[("R2", ("anuncios", "vendas"))]
    assert puxada["severidade"] == "alta"
    assert puxada["exemplo"]["linhas"][0] == 97
    copias = avisos[("R6", ())]
    assert copias["severidade"] == "alta"
    assert "9 das 60 linhas novas (15%)" in copias["resumo"]
