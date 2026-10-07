import math

import pandas as pd
import pytest

from app.compartilhado.series import (
    casas_decimais,
    converter_para_numero,
    eh_inteira,
    proporcao_numerica,
)


def test_converter_texto_com_virgula_decimal_e_ponto_de_milhar() -> None:
    serie = pd.Series(["1,72", "1.234,5", " 7 ", "doze", None])

    convertida = converter_para_numero(serie, decimal=",")

    assert convertida.iloc[:3].tolist() == [1.72, 1234.5, 7.0]
    assert math.isnan(convertida.iloc[3])
    assert math.isnan(convertida.iloc[4])
    assert convertida.dtype == "float64"


def test_converter_serie_ja_numerica_mantem_valores() -> None:
    assert converter_para_numero(pd.Series([1, 2])).tolist() == [1.0, 2.0]


def test_converter_booleanos_nao_vira_numero() -> None:
    assert converter_para_numero(pd.Series([True, False])).isna().all()


def test_proporcao_numerica_ignora_faltantes() -> None:
    serie = pd.Series(["1", "2", "3", "doze", None])

    assert proporcao_numerica(serie) == pytest.approx(0.75)
    assert proporcao_numerica(pd.Series([None, None])) == 0.0


@pytest.mark.parametrize(
    ("valores", "esperado"),
    [([1.0, 2.0, 3.0], True), ([1.0, 2.5], False), ([1.0, None, 4.0], True)],
)
def test_eh_inteira(valores: list[float | None], esperado: bool) -> None:
    assert eh_inteira(pd.Series(valores, dtype="float64")) is esperado


@pytest.mark.parametrize(
    ("valores", "esperado"),
    [([1.0, 2.0], 0), ([1.5, 2.0], 1), ([1.62, 1.7], 2), ([0.1234567], 6)],
)
def test_casas_decimais(valores: list[float], esperado: int) -> None:
    assert casas_decimais(pd.Series(valores)) == esperado
