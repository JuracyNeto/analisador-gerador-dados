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


def test_secao_distribuicoes_aceita(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(
        f"/api/datasets/{dataset_id}/relatorio", params={"secoes": ["distribuicoes"]}
    )

    assert resposta.status_code == 200


def test_secoes_gerador_e_detector_aceitas(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(
        f"/api/datasets/{dataset_id}/relatorio",
        params={"secoes": ["gerador", "detector"], "gerado": "nao-existe"},
    )

    assert resposta.status_code == 200


def test_sem_secoes_traz_as_nove(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    corpo = {"origem": {"dataset_id": dataset_id, "coluna": "peso_kg"}, "x": 50, "semente": 42}
    gerado_id = cliente.post("/api/gerador/univariado", json=corpo).json()["gerado_id"]

    sem_gerado = cliente.get(f"/api/datasets/{dataset_id}/relatorio").text
    html = cliente.get(f"/api/datasets/{dataset_id}/relatorio", params={"gerado": gerado_id}).text

    for titulo in ("Leitura do arquivo", "Tipos de variável", "Limpeza", "Análise de"):
        assert titulo in html
    assert "<h3>Forma e distribuição</h3>" in html
    assert ". Bivariada</h2>" in html
    assert ". Gerador de dados</h2>" in html
    assert ". Gerador de dados</h2>" not in sem_gerado
    assert ". Detector de dados artificiais</h2>" in html
    assert ". Detector de dados artificiais</h2>" in sem_gerado
    assert ". Fórmulas usadas</h2>" in html
    assert html.index("Detector de dados artificiais</h2>") < html.index("Fórmulas usadas</h2>")


def test_secao_formulas_aceita(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(
        f"/api/datasets/{dataset_id}/relatorio", params={"secoes": ["analises", "formulas"]}
    )

    assert resposta.status_code == 200
    assert "<h3>Análise por coluna</h3>" in resposta.text


def test_secao_desconhecida(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/relatorio", params={"secoes": ["xyz"]})

    assert resposta.status_code == 422


def test_dataset_inexistente(cliente: TestClient) -> None:
    assert cliente.get("/api/datasets/nao-existe/relatorio").status_code == 404
