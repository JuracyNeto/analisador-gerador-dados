from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_analise_de_coluna_continua(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/colunas/altura_m/analise")

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert (corpo["tipo"], corpo["n"], corpo["n_faltantes"]) == ("continua", 229, 1)
    assert corpo["frequencias"]["k_sturges"] == 9
    assert corpo["tendencia"]["media"]["formula"] == "media"
    assert corpo["aplicavel"]["separatrizes"] is True
    assert len(corpo["separatrizes"]["percentis"]) == 99
    assert corpo["figuras"] == []


def test_analise_de_coluna_nominal(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    corpo = cliente.get(f"/api/datasets/{dataset_id}/colunas/cidade/analise").json()

    assert corpo["separatrizes"] is None
    assert corpo["dispersao"] is None
    assert {"separatrizes", "dispersao"} <= {item["item"] for item in corpo["nao_aplicavel"]}


def test_numero_de_classes(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    url = f"/api/datasets/{dataset_id}/colunas/altura_m/analise"

    assert cliente.get(url, params={"classes": 5}).json()["frequencias"]["k"] == 5
    assert cliente.get(url, params={"classes": 2}).status_code == 422


def test_identificador_e_coluna_inexistente(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    identificador = cliente.get(f"/api/datasets/{dataset_id}/colunas/id/analise")
    inexistente = cliente.get(f"/api/datasets/{dataset_id}/colunas/renda/analise")

    assert identificador.status_code == 400
    assert identificador.json()["codigo"] == "COLUNA_IGNORADA"
    assert inexistente.status_code == 404
    assert inexistente.json()["codigo"] == "COLUNA_NAO_ENCONTRADA"


def test_onde_esta_meu_valor(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    url = f"/api/datasets/{dataset_id}/colunas/altura_m/posicao"

    resposta = cliente.get(url, params={"valor": 1.7, "tipo": "decil"})
    nominal = cliente.get(f"/api/datasets/{dataset_id}/colunas/cidade/posicao", params={"valor": 1})

    assert resposta.status_code == 200
    assert resposta.json()["tipo"] == "decil"
    assert len(resposta.json()["marcas"]) == 9
    assert nominal.json()["codigo"] == "POSICAO_NAO_APLICAVEL"
