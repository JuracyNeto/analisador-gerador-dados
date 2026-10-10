from typing import Any

from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def _gerar_peso(cliente: TestClient, dataset_id: str, x: int = 500) -> dict[str, Any]:
    corpo = {"origem": {"dataset_id": dataset_id, "coluna": "peso_kg"}, "x": x, "semente": 1}
    resposta: dict[str, Any] = cliente.post("/api/gerador/univariado", json=corpo).json()
    return resposta


def test_csv_com_ponto_e_virgula_e_virgula_decimal(cliente: TestClient) -> None:
    gerado = _gerar_peso(cliente, _exemplo(cliente), 5)

    resposta = cliente.get(f"/api/gerador/{gerado['gerado_id']}/csv")

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/csv")
    assert 'filename="gerado-peso_kg.csv"' in resposta.headers["content-disposition"]
    assert "\r" not in resposta.text
    linhas = resposta.text.splitlines()
    assert linhas[0] == "peso_kg"
    assert len(linhas) == 6
    assert "," in "".join(linhas[1:])


def test_usar_como_novo_dataset(cliente: TestClient) -> None:
    gerado = _gerar_peso(cliente, _exemplo(cliente))

    adotado = cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar", json={"modo": "novo"}
    ).json()

    assert adotado["modo"] == "novo"
    assert adotado["n_linhas"] == 500
    assert adotado["nome_arquivo"] == "gerado-peso_kg.csv"
    colunas = cliente.get(f"/api/datasets/{adotado['dataset_id']}/colunas").json()
    assert colunas[0]["tipo"] == "continua"


def test_anexar_ao_dataset_atual_e_desfazer(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    gerado = _gerar_peso(cliente, dataset_id)

    adotado = cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar",
        json={"modo": "anexar", "dataset_id": dataset_id},
    ).json()

    assert adotado["n_linhas"] == 730
    assert adotado["nome_arquivo"] == "pesquisa_saude.txt"
    pagina = cliente.get(f"/api/datasets/{dataset_id}", params={"pagina": 37}).json()
    ultima = pagina["linhas"][-1]["valores"]
    assert ultima["cidade"] is None
    assert isinstance(ultima["peso_kg"], float)
    desfeito = cliente.post(f"/api/datasets/{dataset_id}/limpeza/desfazer").json()
    assert desfeito["n_linhas"] == 230


def test_anexar_registra_no_log(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    gerado = _gerar_peso(cliente, dataset_id, 3)
    cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar",
        json={"modo": "anexar", "dataset_id": dataset_id},
    )

    limpeza = cliente.post(f"/api/datasets/{dataset_id}/limpeza", json={"acoes": []}).json()

    assert limpeza["log"][-1]["frase"] == "Anexamos 3 linhas geradas em peso_kg."
    assert limpeza["n_linhas"] == 233


def test_anexar_coluna_que_nao_existe(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    corpo = {"tipo": "continua", "modo": "parametros", "x": 3, "media": 1, "desvio": 1}
    gerado = cliente.post("/api/gerador/univariado", json=corpo).json()

    resposta = cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar",
        json={"modo": "anexar", "dataset_id": dataset_id},
    )

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "COLUNAS_INCOMPATIVEIS"


def test_anexar_sem_dataset(cliente: TestClient) -> None:
    gerado = _gerar_peso(cliente, _exemplo(cliente), 3)

    resposta = cliente.post(f"/api/gerador/{gerado['gerado_id']}/adotar", json={"modo": "anexar"})

    assert resposta.json()["codigo"] == "PARAMETROS_INCOMPLETOS"


def test_pares_viram_um_dataset_de_duas_colunas(cliente: TestClient) -> None:
    corpo = {"n": 40, "media_x": 10, "media_y": 20, "desvio_x": 2, "desvio_y": 3, "rho": 0.5}
    gerado = cliente.post("/api/gerador/bivariado", json=corpo).json()

    adotado = cliente.post(
        f"/api/gerador/{gerado['gerado_id']}/adotar", json={"modo": "novo"}
    ).json()

    colunas = cliente.get(f"/api/datasets/{adotado['dataset_id']}/colunas").json()
    assert [(c["coluna"], c["tipo"]) for c in colunas] == [("x", "continua"), ("y", "continua")]
    assert adotado["n_linhas"] == 40
