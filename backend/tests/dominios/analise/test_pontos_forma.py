import numpy as np
import pytest

from app.dominios.analise.pontos_forma import comparacao_binomial, curva_normal, pontos_qq


def test_curva_normal_tem_area_igual_a_escala() -> None:
    curva = curva_normal(70.0, 11.0, 70.0 - 4 * 11.0, 70.0 + 4 * 11.0, escala=227 * 5.5)

    x, y = np.asarray(curva.x), np.asarray(curva.y)
    area = float(np.sum((y[1:] + y[:-1]) / 2 * np.diff(x)))
    assert len(x) == 200
    assert area == pytest.approx(227 * 5.5, rel=0.02)
    assert (curva.media, curva.desvio) == (70.0, 11.0)


def test_pico_da_curva_fica_na_media() -> None:
    curva = curva_normal(0.0, 1.0, -3.0, 3.0, escala=1.0)

    pico = curva.x[int(np.argmax(curva.y))]
    assert abs(pico) < 0.05


def test_qq_com_poucos_valores_usa_todos_ordenados() -> None:
    dados = np.array([5.0, 1.0, 3.0, 2.0, 4.0, 9.0, 0.0, 7.0, 6.0, 8.0])

    qq = pontos_qq(dados)

    assert qq.observados == tuple(sorted(dados.tolist()))
    assert len(qq.teoricos) == 10
    assert qq.teoricos[0] == pytest.approx(-qq.teoricos[-1])
    assert qq.media == pytest.approx(4.5)


def test_qq_com_muitos_valores_limita_a_500_pontos() -> None:
    dados = np.random.default_rng(1).normal(0, 1, 6000)

    qq = pontos_qq(dados)

    assert len(qq.teoricos) == len(qq.observados) == 500
    assert list(qq.observados) == sorted(qq.observados)
    assert list(qq.teoricos) == sorted(qq.teoricos)


def test_comparacao_binomial_soma_os_esperados() -> None:
    dados = np.array([0, 1, 1, 2, 2, 2, 3, 4], dtype="float64")

    comparacao = comparacao_binomial(dados, n=4, p=0.5)

    assert comparacao.k == (0, 1, 2, 3, 4)
    assert comparacao.observados == (1, 2, 3, 1, 1)
    assert sum(comparacao.esperados) == pytest.approx(8.0)
    assert comparacao.esperados[2] == pytest.approx(8 * 6 / 16)
