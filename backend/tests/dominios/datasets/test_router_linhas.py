import pytest
from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_linhas_por_intervalo(cliente: TestClient) -> None:
    resposta = cliente.get(f"/api/datasets/{_exemplo(cliente)}/linhas?de=10&ate=15")

    assert resposta.status_code == 200
    assert [linha["linha"] for linha in resposta.json()] == [10, 11, 12, 13, 14, 15]
    assert "peso_kg" in resposta.json()[0]["valores"]


def test_linhas_seguem_a_versao_atual(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    acoes = {"acoes": [{"problema": "duplicados", "acao": "remover"}]}
    cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=acoes)

    linhas = cliente.get(f"/api/datasets/{dataset_id}/linhas?de=43&ate=48").json()

    assert [linha["linha"] for linha in linhas] == [43, 44, 48]


@pytest.mark.parametrize("consulta", ["de=0&ate=500", "de=20&ate=10"])
def test_intervalo_invalido_da_400(cliente: TestClient, consulta: str) -> None:
    resposta = cliente.get(f"/api/datasets/{_exemplo(cliente)}/linhas?{consulta}")

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "INTERVALO_INVALIDO"
