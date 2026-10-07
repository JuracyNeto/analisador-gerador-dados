from fastapi.testclient import TestClient


def test_saude_responde_ok_com_versao(cliente: TestClient) -> None:
    resposta = cliente.get("/api/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "versao": "0.1.0"}


def test_cors_libera_o_frontend_local(cliente: TestClient) -> None:
    resposta = cliente.options(
        "/api/saude",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )

    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
