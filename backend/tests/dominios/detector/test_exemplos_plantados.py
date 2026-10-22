"""Os arquivos de demonstração disparam as regras esperadas (spec 12, spec 17, D124)."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.dominios.detector.apoio import exemplo_principal_limpo


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


def test_pesquisa_saude_limpa_sem_bloco_alinhado(cliente: TestClient) -> None:
    """O exemplo principal depois da limpeza: altura_m tem só 41 valores distintos (empates)."""
    dataset_id = exemplo_principal_limpo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/detector", params={"regras": "R1"})

    assert resposta.json()["avisos"] == []
    assert resposta.json()["resumo"]["regras_verificadas"] == 1


def test_faltantes_preenchidos_nao_viram_valores_redondos(cliente: TestClient) -> None:
    """A mediana entra nas casas da coluna (68,8, não 68,75): pesos não "terminam em 0" (D146)."""
    dataset_id = cliente.post("/api/datasets/exemplo").json()["dataset_id"]
    diagnostico = cliente.get(f"/api/datasets/{dataset_id}/diagnostico").json()
    acoes = [{"problema": "duplicados", "acao": "remover"}] + [
        {"problema": "faltantes", "acao": "preencher_mediana", "coluna": item["coluna"]}
        for item in diagnostico["faltantes"]
        if item["sugeridos"]["mediana"] is not None
    ]
    log = cliente.post(f"/api/datasets/{dataset_id}/limpeza", json={"acoes": acoes}).json()["log"]

    resposta = cliente.get(f"/api/datasets/{dataset_id}/detector", params={"regras": "R4,R9"})

    assert any("peso_kg com a mediana" in entrada["frase"] for entrada in log)
    assert resposta.json()["avisos"] == []


def test_bloco_alinhado_nos_pesos(plantadas: dict[Any, dict[str, Any]]) -> None:
    """Em pesos (0,1 kg), o bloco acertado não empata com os embaralhamentos (D142)."""
    aviso = plantadas[("R1", ("peso_kg",))]

    assert aviso["severidade"] == "alta"
    assert aviso["exemplo"]["linhas"] == list(range(181, 201))
    assert aviso["exemplo"]["texto"] == (
        "Linhas 181 a 200: média 71,26 (restante 71,26) · desvio padrão 12,01 (restante 12,01)"
    )
    assert aviso["detalhes"]["valor"] == "dᵤ = 0 · dₛ = 0"
    assert aviso["detalhes"]["p_valor"] == 0.0
    assert aviso["figura"]["id"] == "blocos"


def test_alturas_em_centimetros_sem_bloco_alinhado(
    plantadas: dict[Any, dict[str, Any]],
) -> None:
    """Em cm, ~1% dos embaralhamentos empata com o melhor bloco possível (spec 12)."""
    assert ("R1", ("altura_m",)) not in plantadas


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
    # As semanas estão em ordem (série no tempo): a R2 fica em atenção (D137).
    assert puxada["severidade"] == "atencao"
    assert "as linhas seguem a coluna data" in puxada["pode_ser_normal"]
    assert puxada["exemplo"]["linhas"][0] == 97
    copias = avisos[("R6", ())]
    assert copias["severidade"] == "alta"
    assert "9 das 60 linhas novas (15%)" in copias["resumo"]
