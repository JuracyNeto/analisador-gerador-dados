from typing import Any

import pytest
from fastapi.testclient import TestClient

UNIVARIADO = "/api/gerador/univariado"
BIVARIADO = "/api/gerador/bivariado"


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def _univariado(cliente: TestClient, corpo: dict[str, Any]) -> Any:
    return cliente.post(UNIVARIADO, json=corpo)


def test_univariado_preservando_coluna_do_exemplo(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    corpo = {"origem": {"dataset_id": dataset_id, "coluna": "peso_kg"}, "x": 500, "semente": 42}

    resposta = _univariado(cliente, corpo)

    assert resposta.status_code == 201
    gerado = resposta.json()
    assert gerado["n"] == 500
    assert gerado["semente"] == 42
    assert len(gerado["amostra"]) == 50
    assert [linha["estatistica"] for linha in gerado["comparacao"]][:2] == ["n", "Média"]
    assert gerado["origem"]["nome_arquivo"] == "pesquisa_saude.txt"
    assert "semente 42" in gerado["explicacao"]
    assert gerado["figuras"][0]["id"] == "sobreposicao"
    assert {"nome": "Semente", "valor": "42"} in gerado["parametros"]
    assert [f["chave"] for f in gerado["formulas"]] == ["kde", "reescala"]
    assert gerado["formulas"][1]["texto"] == "zᵢ = (gᵢ − ḡ) / s_g → xᵢ' = x̄ + s·zᵢ"


def test_mesma_semente_mesma_amostra(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    corpo = {"origem": {"dataset_id": dataset_id, "coluna": "idade"}, "x": 30, "semente": 7}

    primeira = _univariado(cliente, corpo).json()["amostra"]
    segunda = _univariado(cliente, corpo).json()["amostra"]

    assert primeira == segunda


def test_sem_semente_o_servidor_sorteia_e_devolve(cliente: TestClient) -> None:
    corpo = {"tipo": "continua", "modo": "parametros", "x": 10, "media": 5, "desvio": 1}

    gerado = _univariado(cliente, corpo).json()

    assert 0 <= gerado["semente"] < 2**32
    assert gerado["colunas"] == ["valor"]
    assert gerado["origem"] is None


@pytest.mark.parametrize(
    ("corpo", "codigo"),
    [
        ({"tipo": "continua", "modo": "parametros", "x": 10, "media": 5}, "PARAMETROS_INCOMPLETOS"),
        ({"x": 10}, "PARAMETROS_INCOMPLETOS"),
        ({"tipo": "binaria", "modo": "parametros", "x": 10}, "PARAMETROS_INCOMPLETOS"),
    ],
)
def test_erros_sem_origem(cliente: TestClient, corpo: dict[str, Any], codigo: str) -> None:
    resposta = _univariado(cliente, corpo)

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == codigo


def test_nominal_so_preserva(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    corpo = {
        "origem": {"dataset_id": dataset_id, "coluna": "cidade"},
        "x": 10,
        "modo": "parametros",
    }

    resposta = _univariado(cliente, corpo)

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "MODO_NAO_APLICAVEL"


def test_identificador_nao_serve_de_origem(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = _univariado(cliente, {"origem": {"dataset_id": dataset_id, "coluna": "id"}, "x": 5})

    assert resposta.json()["codigo"] == "COLUNA_NAO_GERAVEL"


def test_validacao_do_pedido(cliente: TestClient) -> None:
    assert _univariado(cliente, {"x": 0}).status_code == 422
    assert _univariado(cliente, {"x": 1_000_001}).status_code == 422


def test_bivariado_com_ajuste_exato_bate_a_correlacao_do_par(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    corpo = {"origem": {"dataset_id": dataset_id, "x": "altura_m", "y": "peso_kg"}, "n": 200}

    gerado = cliente.post(BIVARIADO, json=corpo).json()

    correlacao = gerado["comparacao"][-1]
    assert correlacao["estatistica"] == "Correlação (r)"
    assert abs(correlacao["gerado"] - correlacao["original"]) < 1e-9
    assert gerado["colunas"] == ["altura_m", "peso_kg"]
    assert gerado["metodo"] == "Cholesky"
    assert [f["chave"] for f in gerado["formulas"]] == ["cholesky", "ajuste_exato"]
    reaberto = cliente.get(f"/api/gerador/{gerado['gerado_id']}").json()
    assert reaberto["formulas"] == gerado["formulas"]


def test_bivariado_sem_origem_exige_os_parametros(cliente: TestClient) -> None:
    resposta = cliente.post(BIVARIADO, json={"n": 50, "media_x": 1})

    assert resposta.status_code == 400
    assert "a média de Y" in resposta.json()["mensagem"]


def test_bivariado_sem_origem_com_alvo(cliente: TestClient) -> None:
    corpo = {
        "n": 100,
        "media_x": 10,
        "media_y": 20,
        "desvio_x": 2,
        "desvio_y": 3,
        "rho": -0.5,
        "nome_x": "a",
        "nome_y": "b",
        "ajuste_exato": False,
        "semente": 3,
    }

    gerado = cliente.post(BIVARIADO, json=corpo).json()

    assert gerado["colunas"] == ["a", "b"]
    assert gerado["comparacao"][-1]["original"] == -0.5
    assert [f["chave"] for f in gerado["formulas"]] == ["cholesky"]


def test_geracao_inexistente(cliente: TestClient) -> None:
    resposta = cliente.get("/api/gerador/nao-existe")

    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "GERADO_NAO_ENCONTRADO"


def test_geracoes_antigas_saem_da_memoria(cliente: TestClient) -> None:
    corpo = {"tipo": "discreta", "modo": "parametros", "x": 3, "media": 5, "desvio": 1}
    primeiro = _univariado(cliente, corpo).json()["gerado_id"]
    for _ in range(20):
        _univariado(cliente, corpo)

    assert cliente.get(f"/api/gerador/{primeiro}").status_code == 404
