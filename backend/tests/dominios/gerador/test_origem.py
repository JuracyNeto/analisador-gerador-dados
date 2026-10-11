import pytest
from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_origem_numerica_tem_media_desvio_e_faixa(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(
        "/api/gerador/origem", params={"dataset_id": dataset_id, "coluna": "peso_kg"}
    )

    assert resposta.status_code == 200
    origem = resposta.json()
    assert origem["tipo"] == "continua"
    assert origem["minimo"] < origem["media"] < origem["maximo"]
    assert origem["desvio"] > 0
    assert origem["so_preservar"] is False
    assert origem["sucesso"] is None


def test_origem_binaria_tem_sucesso_e_chance(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    origem = cliente.get(
        "/api/gerador/origem", params={"dataset_id": dataset_id, "coluna": "sexo"}
    ).json()

    assert (origem["sucesso"], origem["fracasso"]) == ("F", "M")
    assert 0 < origem["chance"] < 1


def test_origem_nominal_so_preserva(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    origem = cliente.get(
        "/api/gerador/origem", params={"dataset_id": dataset_id, "coluna": "cidade"}
    ).json()

    assert origem["so_preservar"] is True
    assert origem["media"] is None


def test_origem_identificador(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get("/api/gerador/origem", params={"dataset_id": dataset_id, "coluna": "id"})

    assert resposta.json()["codigo"] == "COLUNA_NAO_GERAVEL"


def test_origem_do_par(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    par = cliente.get(
        "/api/gerador/origem-par",
        params={"dataset_id": dataset_id, "x": "altura_m", "y": "peso_kg"},
    ).json()

    assert (par["x"], par["y"]) == ("altura_m", "peso_kg")
    assert -1 <= par["r"] <= 1
    assert par["desvio_x"] > 0


@pytest.mark.parametrize("caminho", ["/api/gerador/origem", "/api/gerador/origem-par"])
def test_origem_exige_parametros(cliente: TestClient, caminho: str) -> None:
    assert cliente.get(caminho).status_code == 422
