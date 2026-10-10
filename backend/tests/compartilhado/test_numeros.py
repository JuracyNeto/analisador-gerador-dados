import pytest

from app.compartilhado.numeros import (
    formatar_com_sinal,
    formatar_fixo,
    formatar_inteiro,
    formatar_numero,
    formatar_p_valor,
    formatar_percentual,
)


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (70.314, "70,31"),
        (12345.6, "12.346"),
        (0.0012346, "0,001235"),
        (72.0, "72"),
        (0.0, "0"),
        (-3.14159, "-3,142"),
        (1.5, "1,5"),
    ],
)
def test_formatar_numero_usa_4_significativos_sem_zeros_a_direita(
    valor: float, esperado: str
) -> None:
    assert formatar_numero(valor) == esperado


def test_formatar_numero_aceita_outra_precisao() -> None:
    assert formatar_numero(70.314, casas_significativas=3) == "70,3"


def test_formatar_inteiro_usa_ponto_de_milhar() -> None:
    assert formatar_inteiro(1234567) == "1.234.567"


def test_formatar_percentual_usa_virgula() -> None:
    assert formatar_percentual(21.6) == "21,6%"
    assert formatar_percentual(100) == "100,0%"


def test_formatar_fixo_mantem_as_casas() -> None:
    assert formatar_fixo(60.0, 1) == "60,0"
    assert formatar_fixo(1234.5, 2) == "1.234,50"


@pytest.mark.parametrize(
    ("p", "esperado"),
    [(0.0004, "p < 0,001"), (0.001, "p = 0,001"), (0.2134, "p = 0,213"), (0.05, "p = 0,05")],
)
def test_formatar_p_valor(p: float, esperado: str) -> None:
    assert formatar_p_valor(p) == esperado


@pytest.mark.parametrize(
    ("valor", "texto"), [(-0.394, "−0,394"), (0.394, "0,394"), (-1234.5, "−1.234")]
)
def test_formatar_com_sinal_usa_o_sinal_de_menos(valor: float, texto: str) -> None:
    assert formatar_com_sinal(valor) == texto
