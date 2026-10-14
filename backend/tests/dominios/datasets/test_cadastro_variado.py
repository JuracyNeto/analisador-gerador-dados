"""Leitura e classificação de um cadastro com tipos de dado variados (D131, spec 01, spec 02)."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

TIPOS = {
    "id": "identificador",
    "nome": "identificador",
    "celular": "identificador",
    "contato": "identificador",
    "cpf": "identificador",
    "cep": "identificador",
    "email": "identificador",
    "nascimento": "data",
    "dia": "data",
    "hora_atendimento": "data",
    "data_hora": "data",
    "valor_compra": "continua",
    "satisfacao": "discreta",
    "vip": "binaria",
    "itens": "discreta",
    "saldo": "continua",
    "temperatura": "continua",
    "cidade": "nominal",
    "escolaridade": "ordinal",
    "observacao": "nominal",
}


@pytest.fixture
def colunas(cliente: TestClient, cadastro_variado: str) -> dict[str, dict[str, Any]]:
    resposta = cliente.get(f"/api/datasets/{cadastro_variado}/colunas")
    return {coluna["coluna"]: coluna for coluna in resposta.json()}


def test_leitura_acha_separador_decimal_e_tamanho(
    cliente: TestClient, cadastro_variado: str
) -> None:
    resumo = cliente.get(f"/api/datasets/{cadastro_variado}").json()["resumo"]

    metadados = resumo["metadados"]
    assert (metadados["separador"], metadados["decimal"]) == (";", ",")
    assert (resumo["n_linhas"], resumo["n_colunas"]) == (300, 22)


@pytest.mark.parametrize(("coluna", "tipo"), TIPOS.items())
def test_tipo_de_cada_coluna(colunas: dict[str, dict[str, Any]], coluna: str, tipo: str) -> None:
    assert colunas[coluna]["tipo"] == tipo, colunas[coluna]["motivo"]


@pytest.mark.parametrize(
    ("coluna", "motivo"),
    [
        ("celular", "Parece um código: 100% dos valores são únicos."),
        ("cpf", "O nome da coluna indica um código (cpf)."),
        ("hora_atendimento", "Horários (ex.: 15:52)."),
        ("data_hora", "Datas com horário (ex.: 01/01/2026 15:06)."),
        ("escolaridade", "Os valores seguem uma escala conhecida: fundamental < médio < superior."),
    ],
)
def test_motivos_mostram_o_formato(
    colunas: dict[str, dict[str, Any]], coluna: str, motivo: str
) -> None:
    assert colunas[coluna]["motivo"] == motivo


@pytest.mark.parametrize(("coluna", "faltantes"), [("saldo", 8), ("observacao", 229)])
def test_na_e_celula_vazia_contam_como_faltantes(
    colunas: dict[str, dict[str, Any]], coluna: str, faltantes: int
) -> None:
    assert colunas[coluna]["n_faltantes"] == faltantes
