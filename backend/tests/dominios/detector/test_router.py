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
    assert resumo["regras_verificadas"] + resumo["regras_nao_aplicadas"] == 11
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


def _importar(cliente: TestClient, nome: str, linhas: list[str]) -> str:
    conteudo = "\n".join(linhas).encode("utf-8")
    resposta = cliente.post("/api/datasets", files={"arquivo": (nome, conteudo, "text/plain")})
    return str(resposta.json()["dataset_id"])


def test_ultimo_digito_vem_com_a_figura(cliente: TestClient) -> None:
    finais = [0] * 48 + [d for _ in range(19) for d in range(1, 10)][:152]
    idades = [20 + 10 * (i % 6) + final for i, final in enumerate(finais)]
    dataset_id = _importar(cliente, "idades.txt", ["idade"] + [str(v) for v in idades])

    corpo = _detector(cliente, dataset_id, "?regras=R9").json()

    (aviso,) = corpo["avisos"]
    figura = aviso["figura"]
    assert figura["id"] == "ultimo_digito"
    assert figura["titulo"] == "Último dígito de idade"
    assert [traco["meta"] for traco in figura["dados"]["data"]] == ["principal", "referencia"]


def test_avisos_sem_grafico_vem_sem_figura(cliente: TestClient) -> None:
    corpo = _detector(cliente, _exemplo(cliente), "?regras=R5,R7").json()

    assert {aviso["figura"] is None for aviso in corpo["avisos"]} == {True}
