import math

import pandas as pd
import pytest

from app.compartilhado.series import (
    Unidade,
    casas_decimais,
    converter_para_numero,
    eh_inteira,
    na_precisao,
    proporcao_numerica,
    reconhecer_unidade,
    sem_unidade,
)


@pytest.mark.parametrize(
    ("texto", "decimal", "esperado"),
    [
        ("R$ 1.234,56", ",", 1234.56),
        ("R$1.234,56", ",", 1234.56),
        ("R$ 1.234,56", ",", 1234.56),
        ("−R$ 10,00", ",", -10.0),
        ("R$ −10,00", ",", -10.0),
        ("-R$ 10,00", ",", -10.0),
        ("R$ -10,00", ",", -10.0),
        ("12,5%", ",", 12.5),
        ("12,5 %", ",", 12.5),
        ("−3,5%", ",", -3.5),
        ("−7", ",", -7.0),
        ("R$ 1234.56", ".", 1234.56),
        ("12.5%", ".", 12.5),
    ],
)
def test_converter_aceita_reais_percentual_e_sinal_de_menos(
    texto: str, decimal: str, esperado: float
) -> None:
    convertido = converter_para_numero(pd.Series([texto]), decimal).iloc[0]

    assert convertido == pytest.approx(esperado)


@pytest.mark.parametrize("texto", ["10,00 R$", "US$ 10,00", "% 12", "12,5%%", "R$", "R$ dez"])
def test_unidade_fora_do_lugar_nao_vira_numero(texto: str) -> None:
    assert math.isnan(converter_para_numero(pd.Series([texto]), ",").iloc[0])


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [(" R$ 1.234,56 ", "1.234,56"), ("−R$ 10,00", "-10,00"), ("12,5 %", "12,5"), ("Ana", "Ana")],
)
def test_sem_unidade(texto: str, esperado: str) -> None:
    assert sem_unidade(texto) == esperado


@pytest.mark.parametrize(
    ("valores", "esperado"),
    [
        (["R$ 10,50", None, "−R$ 7,00"], Unidade("reais", "R$ 10,50")),
        (["5 %", "12,5%"], Unidade("percentual", "5 %")),
        (["10,5", "7"], None),
        ([None, None], None),
    ],
)
def test_reconhecer_unidade(valores: list[str | None], esperado: Unidade | None) -> None:
    assert reconhecer_unidade(pd.Series(valores), 0.9) == esperado


def test_unidade_precisa_estar_em_quase_todos_os_valores() -> None:
    valores = pd.Series(["R$ 10,50"] * 8 + ["10,50"] * 2)

    assert reconhecer_unidade(valores, 0.9) is None
    assert reconhecer_unidade(valores, 0.8) == Unidade("reais", "R$ 10,50")


def test_coluna_ja_numerica_nao_tem_unidade() -> None:
    assert reconhecer_unidade(pd.Series([10.5, 7.0]), 0.9) is None


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


@pytest.mark.parametrize(
    ("valor", "valores", "esperado"),
    [(68.75, [60.0, 68.5], 68.8), (2.25, [1.0, 4.0], 2.0), (1.6234, [1.62, 1.7], 1.62)],
)
def test_na_precisao_usa_as_casas_da_coluna(
    valor: float, valores: list[float], esperado: float
) -> None:
    assert na_precisao(valor, pd.Series(valores)) == esperado
