from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.erros import NaoEncontrado
from app.main import create_app


def _app_com_rotas_de_teste() -> FastAPI:
    app = create_app()

    @app.get("/teste/nao-encontrado")
    def nao_encontrado() -> None:
        raise NaoEncontrado(
            "DATASET_NAO_ENCONTRADO", "Sua sessão expirou.", "Envie o arquivo novamente."
        )

    @app.get("/teste/inesperado")
    def inesperado() -> None:
        raise RuntimeError("detalhe interno")

    @app.get("/teste/validacao")
    def validacao(quantidade: int) -> int:
        return quantidade

    return app


cliente = TestClient(_app_com_rotas_de_teste(), raise_server_exceptions=False)


def test_erro_de_aplicacao_vira_json_padronizado() -> None:
    resposta = cliente.get("/teste/nao-encontrado")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "codigo": "DATASET_NAO_ENCONTRADO",
        "mensagem": "Sua sessão expirou.",
        "sugestao": "Envie o arquivo novamente.",
    }


def test_erro_inesperado_nao_vaza_detalhes() -> None:
    resposta = cliente.get("/teste/inesperado")

    assert resposta.status_code == 500
    assert resposta.json()["codigo"] == "ERRO_INTERNO"
    assert "detalhe interno" not in resposta.text


def test_validacao_cita_o_campo_em_portugues() -> None:
    resposta = cliente.get("/teste/validacao", params={"quantidade": "abc"})

    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "ENTRADA_INVALIDA"
    assert "quantidade" in resposta.json()["mensagem"]
