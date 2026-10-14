from typing import Any

import pytest
from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def _detector(cliente: TestClient, dataset_id: str, consulta: str = "") -> Any:
    return cliente.get(f"/api/datasets/{dataset_id}/detector{consulta}")


def _avisos(corpo: dict[str, Any], regra: str) -> list[dict[str, Any]]:
    return [aviso for aviso in corpo["avisos"] if aviso["regra"] == regra]


def test_detector_do_exemplo_acha_duplicatas_e_valores_distantes(cliente: TestClient) -> None:
    resposta = _detector(cliente, _exemplo(cliente))

    assert resposta.status_code == 200
    corpo = resposta.json()
    (duplicatas,) = _avisos(corpo, "R5")
    assert duplicatas["severidade"] == "alta"
    assert duplicatas["exemplo"]["linhas"] == [44, 45, 46, 47]
    assert "as linhas 44 a 47 são iguais e seguidas" in duplicatas["resumo"]
    distantes = {aviso["colunas"][0]: aviso for aviso in _avisos(corpo, "R7")}
    assert "17,2" in distantes["altura_m"]["exemplo"]["valores"]
    assert corpo["avisos"][0]["severidade"] == "alta"


def test_resumo_bate_com_os_avisos(cliente: TestClient) -> None:
    corpo = _detector(cliente, _exemplo(cliente)).json()

    resumo = corpo["resumo"]
    assert resumo["total"] == len(corpo["avisos"])
    assert sum(resumo["por_severidade"].values()) == resumo["total"]
    assert resumo["frase"].startswith(f"Encontramos {resumo['total']} alertas")
    assert resumo["regras_verificadas"] + resumo["regras_nao_aplicadas"] == 6
    nao_aplicadas = {(n["regra"], n["coluna"]) for n in corpo["nao_aplicadas"]}
    assert ("R8", "idade") in nao_aplicadas


def test_regras_pedidas_rodam_so_essas(cliente: TestClient) -> None:
    corpo = _detector(cliente, _exemplo(cliente), "?regras=R4,R7").json()

    regras = {aviso["regra"] for aviso in corpo["avisos"]}
    regras |= {item["regra"] for item in corpo["nao_aplicadas"]}
    assert regras <= {"R4", "R7"}
    assert corpo["resumo"]["regras_verificadas"] + corpo["resumo"]["regras_nao_aplicadas"] == 2


@pytest.mark.parametrize("consulta", ["?regras=R99", "?regras=R4,X", "?regras=r4"])
def test_codigo_de_regra_desconhecido_da_422(cliente: TestClient, consulta: str) -> None:
    resposta = _detector(cliente, _exemplo(cliente), consulta)

    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "ENTRADA_INVALIDA"


def test_dataset_inexistente_da_404(cliente: TestClient) -> None:
    resposta = _detector(cliente, "nao-existe")

    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "DATASET_NAO_ENCONTRADO"


def test_duplicatas_somem_depois_da_limpeza(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    acoes = {"acoes": [{"problema": "duplicados", "acao": "remover"}]}
    cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=acoes)

    corpo = _detector(cliente, dataset_id).json()

    assert _avisos(corpo, "R5") == []
