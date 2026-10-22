import pytest
from fastapi.testclient import TestClient

ARQUIVOS = [
    "pesquisa_saude.txt",
    "alturas_reais.txt",
    "alturas_plantadas.txt",
    "vendas_correlacao_puxada.txt",
]


def test_lista_os_exemplos_com_descricao(cliente: TestClient) -> None:
    resposta = cliente.get("/api/datasets/exemplos")

    assert resposta.status_code == 200
    exemplos = resposta.json()
    assert [exemplo["arquivo"] for exemplo in exemplos] == ARQUIVOS
    assert exemplos[0]["descricao"] == "Pesquisa de saúde (valores fora de faixa e duplicados)"
    assert all(exemplo["descricao"] for exemplo in exemplos)
    # Spec 16: tom neutro, com os termos do Detector ("dados inseridos").
    assert [exemplo["descricao"] for exemplo in exemplos[1:3]] == [
        "Alturas reais (sem dados inseridos)",
        "Alturas com dados inseridos",
    ]


@pytest.mark.parametrize("arquivo", ARQUIVOS)
def test_importa_cada_exemplo(cliente: TestClient, arquivo: str) -> None:
    resposta = cliente.post(f"/api/datasets/exemplo?arquivo={arquivo}")

    assert resposta.status_code == 201
    assert resposta.json()["nome_arquivo"] == arquivo


def test_sem_arquivo_importa_a_pesquisa_de_saude(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets/exemplo")

    assert resposta.json()["nome_arquivo"] == "pesquisa_saude.txt"


@pytest.mark.parametrize("arquivo", ["nao_existe.txt", "../pyproject.toml", "notas_turma.csv"])
def test_arquivo_fora_da_lista_da_404(cliente: TestClient, arquivo: str) -> None:
    resposta = cliente.post("/api/datasets/exemplo", params={"arquivo": arquivo})

    assert resposta.status_code == 404
    corpo = resposta.json()
    assert corpo["codigo"] == "EXEMPLO_NAO_ENCONTRADO"
    assert corpo["mensagem"] == f"Não encontramos o exemplo {arquivo}."
