import plotly.graph_objects as go
import pytest
from fastapi.testclient import TestClient

LIMPEZA = {
    "acoes": [
        {"problema": "fora_de_faixa", "acao": "remover_linhas", "coluna": "peso_kg"},
        {"problema": "fora_de_faixa", "acao": "remover_linhas", "coluna": "altura_m"},
        {"problema": "duplicados", "acao": "remover"},
    ]
}


def _exemplo(cliente: TestClient) -> str:
    """Exemplo sem os valores plantados fora de faixa (altura 17,2 m etc.), como na tela 5a."""
    dataset_id = str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])
    assert cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=LIMPEZA).status_code == 200
    return dataset_id


def _bivariada(cliente: TestClient, dataset_id: str, x: str, y: str) -> tuple[int, dict]:
    resposta = cliente.get(f"/api/datasets/{dataset_id}/bivariada", params={"x": x, "y": y})
    return resposta.status_code, resposta.json()


def test_altura_e_peso_tem_correlacao_positiva(cliente: TestClient) -> None:
    status, corpo = _bivariada(cliente, _exemplo(cliente), "altura_m", "peso_kg")

    assert status == 200
    assert (corpo["forca"], corpo["sentido"]) == ("forte", "positiva")
    assert corpo["n"] + corpo["n_descartados"] == 222
    assert corpo["faixa_x"] == {"minimo": 1.47, "maximo": 1.93}
    assert corpo["regressao"]["equacao"].startswith("Ŷ = ")
    assert corpo["pearson"]["formula"] == "pearson"
    assert [f["id"] for f in corpo["figuras"]] == ["dispersao", "residuos"]
    for figura in corpo["figuras"]:
        go.Figure(figura["dados"])
    assert {"pearson", "regressao", "r2"} <= {f["chave"] for f in corpo["formulas"]}


@pytest.mark.parametrize(
    ("x", "y", "codigo"),
    [
        ("cidade", "peso_kg", "COLUNA_NAO_NUMERICA"),
        ("peso_kg", "peso_kg", "COLUNAS_IGUAIS"),
    ],
)
def test_pares_recusados(cliente: TestClient, x: str, y: str, codigo: str) -> None:
    status, corpo = _bivariada(cliente, _exemplo(cliente), x, y)

    assert status == 400
    assert corpo["codigo"] == codigo


def test_coluna_inexistente(cliente: TestClient) -> None:
    status, corpo = _bivariada(cliente, _exemplo(cliente), "altura_m", "nao_existe")

    assert status == 404
    assert corpo["codigo"] == "COLUNA_NAO_ENCONTRADA"


def test_falta_um_parametro(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/bivariada", params={"x": "altura_m"})

    assert resposta.status_code == 422


def test_dataset_inexistente(cliente: TestClient) -> None:
    status, corpo = _bivariada(cliente, "nao-existe", "a", "b")

    assert status == 404
    assert corpo["codigo"] == "DATASET_NAO_ENCONTRADO"


@pytest.mark.parametrize(("valor", "fora"), [(1.7, False), (2.1, True)])
def test_prever(cliente: TestClient, valor: float, fora: bool) -> None:
    dataset_id = _exemplo(cliente)

    corpo = cliente.get(
        f"/api/datasets/{dataset_id}/bivariada/prever",
        params={"x": "altura_m", "y": "peso_kg", "valor": valor},
    ).json()

    assert corpo["extrapolacao"] is fora
    assert corpo["frase"].startswith("Para altura_m = ")
    assert (corpo["aviso"] is not None) is fora


def test_matriz_de_correlacao(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    corpo = cliente.get(f"/api/datasets/{dataset_id}/correlacoes").json()

    assert corpo["colunas"] == ["idade", "altura_m", "peso_kg"]
    assert len(corpo["valores"]) == 3
    assert corpo["resumo"].startswith("O par mais forte é ")
    assert corpo["figura"]["id"] == "matriz"
    go.Figure(corpo["figura"]["dados"])


def test_rotas_da_univariada_continuam_iguais(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    analise = cliente.get(f"/api/datasets/{dataset_id}/colunas/peso_kg/analise")
    posicao = cliente.get(
        f"/api/datasets/{dataset_id}/colunas/peso_kg/posicao", params={"valor": 70}
    )

    assert (analise.status_code, posicao.status_code) == (200, 200)
