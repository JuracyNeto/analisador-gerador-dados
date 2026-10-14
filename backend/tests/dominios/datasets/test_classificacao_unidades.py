"""Valores em reais e percentuais viram número; o motivo diz a unidade (spec 02, D132)."""

import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.datasets.classificacao import Classificacao, Limiares, classificar, ler_coluna


def _classificar(nome: str, valores: list[object]) -> Classificacao:
    return classificar(ler_coluna(nome, pd.Series(valores), ",", Limiares()))


@pytest.mark.parametrize(
    ("valores", "motivo"),
    [
        (["R$ 1.234,56", "R$ 59,90", "−R$ 10,00", None], "Valores em reais (ex.: R$ 1.234,56)."),
        (["12,5%", "7,5 %", "10%"], "Percentuais (ex.: 12,5%)."),
    ],
)
def test_reais_e_percentuais_com_decimais_viram_continua(
    valores: list[object], motivo: str
) -> None:
    resultado = _classificar("valor", valores)

    assert (resultado.tipo, resultado.motivo) == (TipoVariavel.CONTINUA, motivo)


def test_percentuais_inteiros_com_poucos_valores_viram_discreta() -> None:
    resultado = _classificar("desconto", ["10%", "5%", "15%", "10%"])

    assert (resultado.tipo, resultado.motivo) == (
        TipoVariavel.DISCRETA,
        "Percentuais (ex.: 10%).",
    )


def test_reais_inteiros_e_unicos_nao_viram_codigo() -> None:
    valores = [f"R$ {1000 + 7 * i}" for i in range(40)]

    resultado = _classificar("preco", valores)

    assert (resultado.tipo, resultado.motivo) == (
        TipoVariavel.CONTINUA,
        "Valores em reais (ex.: R$ 1000).",
    )


def test_nome_de_codigo_vence_a_unidade() -> None:
    assert _classificar("cod_tarifa", ["R$ 1,50", "R$ 2,00"]).tipo == TipoVariavel.IDENTIFICADOR


def test_reais_com_dois_valores_seguem_binaria() -> None:
    resultado = _classificar("taxa", ["R$ 5,00", "R$ 7,50", "R$ 5,00"])

    assert (resultado.tipo, resultado.motivo) == (
        TipoVariavel.BINARIA,
        "Tem só dois valores: 5 e 7,5.",
    )
