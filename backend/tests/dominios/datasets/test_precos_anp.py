"""Leitura e tipos numa amostra real: preços de combustíveis da ANP em Goiás (D139).

Fonte: ANP, Série Histórica de Preços de Combustíveis e de GLP (set/2026), CC-BY; ver
`tests/fixtures/FONTES.md`.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

TIPOS = {
    "Regiao - Sigla": "nominal",
    "Municipio": "nominal",
    "Revenda": "nominal",
    "CNPJ da Revenda": "identificador",
    "Cep": "identificador",
    "Produto": "nominal",
    "Data da Coleta": "data",
    "Valor de Venda": "continua",
    "Valor de Compra": "identificador",
    "Bandeira": "nominal",
}


@pytest.fixture
def tipos(cliente: TestClient, precos_anp: str) -> dict[str, dict[str, Any]]:
    resposta = cliente.get(f"/api/datasets/{precos_anp}/colunas")
    return {coluna["coluna"]: coluna for coluna in resposta.json()}


def test_leitura_do_arquivo_da_anp(cliente: TestClient, precos_anp: str) -> None:
    resumo = cliente.get(f"/api/datasets/{precos_anp}").json()["resumo"]

    metadados = resumo["metadados"]
    assert (metadados["codificacao"], metadados["separador"]) == ("utf-8-sig", ";")
    assert (metadados["decimal"], metadados["linha_cabecalho"]) == (",", 1)
    assert (resumo["n_linhas"], resumo["n_colunas"]) == (300, 16)


@pytest.mark.parametrize(("coluna", "tipo"), TIPOS.items())
def test_tipo_de_cada_coluna_da_anp(
    tipos: dict[str, dict[str, Any]], coluna: str, tipo: str
) -> None:
    assert tipos[coluna]["tipo"] == tipo, tipos[coluna]["motivo"]


def test_coluna_sem_nenhum_valor_e_ignorada(tipos: dict[str, dict[str, Any]]) -> None:
    assert tipos["Valor de Compra"]["motivo"] == "A coluna está vazia; foi ignorada."
