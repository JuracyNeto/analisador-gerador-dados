import json

from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_diagnostico_com_limites(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    limites = json.dumps({"idade": {"min": 1, "max": 110}})

    resposta = cliente.get(f"/api/datasets/{dataset_id}/diagnostico", params={"limites": limites})

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["n_linhas"] == 230
    assert corpo["duplicados"] == [{"linha_original": 44, "copias": [45, 46, 47]}]
    idade = next(f for f in corpo["fora_de_faixa"] if f["coluna"] == "idade")
    assert idade["origem"] == "usuario"


def test_diagnostico_com_limites_invalidos(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    url = f"/api/datasets/{dataset_id}/diagnostico"

    invertidos = cliente.get(url, params={"limites": '{"idade": {"min": 110, "max": 1}}'})
    mal_formados = cliente.get(url, params={"limites": "{nao e json"})

    assert invertidos.status_code == 400
    assert invertidos.json()["codigo"] == "LIMITES_INVALIDOS"
    assert mal_formados.status_code == 422


def test_aplicar_e_desfazer_limpeza(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    pedido = {
        "acoes": [
            {"problema": "duplicados", "acao": "remover"},
            {"problema": "faltantes", "acao": "preencher_mediana", "coluna": "peso_kg"},
            {"problema": "faltantes", "acao": "manter", "coluna": "cidade"},
        ]
    }

    aplicada = cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=pedido)
    resumo = cliente.get(f"/api/datasets/{dataset_id}").json()["resumo"]
    desfeita = cliente.post(f"/api/datasets/{dataset_id}/limpeza/desfazer")

    assert aplicada.status_code == 200
    assert aplicada.json()["n_linhas"] == 227
    assert [e["acao"] for e in aplicada.json()["log"]] == ["remover", "preencher_mediana"]
    assert len(resumo["log_limpeza"]) == 2
    assert desfeita.json()["n_linhas"] == 230
    assert desfeita.json()["log"] == []


def test_acao_incompativel(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    pedido = {"acoes": [{"problema": "faltantes", "acao": "preencher_media", "coluna": "cidade"}]}

    resposta = cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=pedido)

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "ACAO_INCOMPATIVEL"
