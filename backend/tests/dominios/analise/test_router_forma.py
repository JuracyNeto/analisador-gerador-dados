from pathlib import Path

import plotly.graph_objects as go
from fastapi.testclient import TestClient

from app.core.config import Configuracao

NOTAS = Path(Configuracao().pasta_exemplos) / "notas_turma.csv"


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def _notas(cliente: TestClient) -> str:
    arquivo = ("notas_turma.csv", NOTAS.read_bytes(), "text/csv")
    return str(cliente.post("/api/datasets", files={"arquivo": arquivo}).json()["dataset_id"])


def _analise(cliente: TestClient, dataset_id: str, coluna: str, busca: str = "") -> dict:
    return cliente.get(f"/api/datasets/{dataset_id}/colunas/{coluna}/analise{busca}").json()


def test_continua_traz_forma_com_normal_e_figuras(cliente: TestClient) -> None:
    corpo = _analise(cliente, _exemplo(cliente), "peso_kg")

    forma = corpo["forma"]
    assert forma["normal"]["teste"]["nome"] == "Shapiro-Wilk"
    assert forma["normal"]["frase"].startswith("Os dados")
    assert forma["binomial"]["aplicavel"] is False
    assert forma["interpretacao"].startswith("Distribuição")
    assert [f["id"] for f in forma["figuras"]] == ["histograma_normal", "qqplot"]
    for figura in forma["figuras"]:
        go.Figure(figura["dados"])
    assert corpo["aplicavel"]["forma"] is True
    assert {"assimetria", "curtose", "normal"} <= {f["chave"] for f in corpo["formulas"]}


def test_nominal_fica_sem_forma(cliente: TestClient) -> None:
    corpo = _analise(cliente, _exemplo(cliente), "cidade")

    assert corpo["forma"] is None
    motivos = {n["item"]: n["motivo"] for n in corpo["nao_aplicavel"]}
    assert "exigem números" in motivos["forma"]


def test_binaria_usa_bernoulli(cliente: TestClient) -> None:
    forma = _analise(cliente, _exemplo(cliente), "sexo")["forma"]

    assert forma["binomial"]["distribuicao"] == "bernoulli"
    assert forma["figuras"] == []


def test_discreta_com_tentativas(cliente: TestClient) -> None:
    dataset_id = _notas(cliente)

    padrao = _analise(cliente, dataset_id, "faltas")["forma"]
    informado = _analise(cliente, dataset_id, "faltas", "?tentativas=20")["forma"]

    assert padrao["tentativas"] == 8
    assert informado["tentativas"] == 20
    assert [f["id"] for f in padrao["figuras"]] == ["bastoes_normal", "binomial"]


def test_tentativas_abaixo_do_maximo_e_erro(cliente: TestClient) -> None:
    dataset_id = _notas(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/colunas/faltas/analise?tentativas=2")

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "TENTATIVAS_INVALIDAS"


def test_tentativas_zero_e_recusado(cliente: TestClient) -> None:
    dataset_id = _notas(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/colunas/faltas/analise?tentativas=0")

    assert resposta.status_code == 422
