from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_relatorio_em_html(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(
        f"/api/datasets/{dataset_id}/relatorio",
        params={"secoes": ["leitura", "analises"], "colunas": ["altura_m", "sexo"]},
    )

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "1. Leitura do arquivo" in resposta.text
    assert "Tipos de variável" not in resposta.text
    assert resposta.text.count("Plotly.newPlot(") == 2


def test_secao_desconhecida(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/relatorio", params={"secoes": ["gerador"]})

    assert resposta.status_code == 422


def test_dataset_inexistente(cliente: TestClient) -> None:
    assert cliente.get("/api/datasets/nao-existe/relatorio").status_code == 404
