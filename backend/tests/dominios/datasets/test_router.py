from fastapi.testclient import TestClient

ARQUIVO = ("pesquisa.txt", b"id;sexo;peso\n1;F;58,2\n2;M;79,6\n3;F;\n4;M;63,0\n", "text/plain")


def _importar(cliente: TestClient) -> str:
    resposta = cliente.post("/api/datasets", files={"arquivo": ARQUIVO})
    assert resposta.status_code == 201
    return str(resposta.json()["dataset_id"])


def test_importar_devolve_metadados_previa_e_colunas(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets", files={"arquivo": ARQUIVO})

    corpo = resposta.json()
    assert resposta.status_code == 201
    assert corpo["metadados"]["separador"] == ";"
    assert corpo["metadados"]["motivos"]["decimal"] == "Valores como 58,2 e 79,6."
    assert corpo["previa"][0] == {"linha": 1, "valores": {"id": 1, "sexo": "F", "peso": 58.2}}
    assert [c["tipo"] for c in corpo["colunas"]] == ["identificador", "binaria", "continua"]


def test_importar_com_opcoes_do_formulario(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/api/datasets",
        files={"arquivo": ARQUIVO},
        data={"separador": ";", "decimal": ",", "linha_cabecalho": "1"},
    )

    assert resposta.json()["metadados"]["motivos"]["separador"] == "Escolhido por você."


def test_formato_nao_suportado(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets", files={"arquivo": ("a.pdf", b"%PDF", "x")})

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "FORMATO_NAO_SUPORTADO"


def test_importar_exemplo(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets/exemplo")

    assert resposta.status_code == 201
    assert resposta.json()["nome_arquivo"] == "pesquisa_saude.txt"


def test_pagina_com_resumo(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    corpo = cliente.get(f"/api/datasets/{dataset_id}", params={"tamanho": 2}).json()

    assert corpo["resumo"]["n_linhas"] == 4
    assert corpo["resumo"]["log_limpeza"] == []
    assert corpo["total_paginas"] == 2


def test_dataset_inexistente(cliente: TestClient) -> None:
    resposta = cliente.get("/api/datasets/nao-existe")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "codigo": "DATASET_NAO_ENCONTRADO",
        "mensagem": "Sua sessão expirou.",
        "sugestao": "Envie o arquivo novamente.",
    }


def test_remover(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    assert cliente.delete(f"/api/datasets/{dataset_id}").status_code == 204
    assert cliente.get(f"/api/datasets/{dataset_id}").status_code == 404


def test_listar_e_alterar_tipo(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    resposta = cliente.patch(
        f"/api/datasets/{dataset_id}/colunas/sexo",
        json={"tipo": "ordinal", "categorias_ordem": ["M", "F"]},
    )
    colunas = cliente.get(f"/api/datasets/{dataset_id}/colunas").json()

    assert resposta.status_code == 200
    assert resposta.json()["origem"] == "manual"
    assert colunas[1]["categorias_ordem"] == ["M", "F"]


def test_alterar_tipo_incompativel(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    resposta = cliente.patch(f"/api/datasets/{dataset_id}/colunas/sexo", json={"tipo": "continua"})

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "TIPO_INCOMPATIVEL"
