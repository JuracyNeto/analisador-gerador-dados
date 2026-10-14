"""Testes binomial, qui-quadrado, runs e autocorrelação (spec 12, fórmulas auxiliares)."""

import numpy as np
import pytest
from scipy import stats

from app.compartilhado import estatistica


def test_binomial_unilateral_com_46_de_100_e_p0_de_20_porcento_e_minusculo() -> None:
    assert estatistica.teste_binomial_unilateral(46, 100, 0.2) < 1e-8


def test_binomial_unilateral_e_a_cauda_superior_incluindo_k() -> None:
    esperado = float(stats.binom.pmf(np.arange(3, 11), 10, 0.3).sum())

    assert estatistica.teste_binomial_unilateral(3, 10, 0.3) == pytest.approx(esperado)


def test_binomial_unilateral_com_k_zero_e_um() -> None:
    assert estatistica.teste_binomial_unilateral(0, 10, 0.3) == pytest.approx(1.0)


def test_qui_quadrado_igual_ao_do_scipy() -> None:
    observados = np.array([30, 14, 12, 9, 8, 7, 7, 7, 6])
    esperados = observados.sum() * np.full(9, 1 / 9)

    resultado = estatistica.teste_qui_quadrado(observados, esperados)

    referencia = stats.chisquare(observados, esperados)
    assert resultado.estatistica == pytest.approx(float(referencia.statistic))
    assert resultado.p_valor == pytest.approx(float(referencia.pvalue))
    assert resultado.gl == 8


def test_runs_de_uma_sequencia_alternada_tem_p_pequeno() -> None:
    acima = np.array([True, False] * 25)

    resultado = estatistica.teste_runs(acima)

    assert resultado.runs == 50
    assert resultado.z > 0
    assert resultado.p_valor < 0.001


def test_runs_de_dois_blocos_tem_poucos_runs() -> None:
    acima = np.array([True] * 20 + [False] * 20)

    resultado = estatistica.teste_runs(acima)

    assert resultado.runs == 2
    assert resultado.z < 0
    assert resultado.p_valor < 0.001


def test_runs_segue_a_formula_da_spec() -> None:
    acima = np.array([True, True, False, True, False, False, False, True, True, False])
    n1, n2, runs = 5, 5, 6
    media = 2 * n1 * n2 / (n1 + n2) + 1
    variancia = 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2) ** 2 * (n1 + n2 - 1))

    resultado = estatistica.teste_runs(acima)

    assert resultado.runs == runs
    assert resultado.z == pytest.approx((runs - media) / np.sqrt(variancia))
    assert resultado.p_valor == pytest.approx(2 * stats.norm.sf(abs(resultado.z)))


def test_runs_sem_os_dois_lados_nao_tem_como_testar() -> None:
    resultado = estatistica.teste_runs(np.array([True] * 10))

    assert resultado.runs == 1
    assert resultado.z == 0
    assert resultado.p_valor == 1


def test_autocorrelacao_de_uma_rampa_e_quase_um() -> None:
    assert estatistica.autocorrelacao_lag1(np.arange(100.0)) == pytest.approx(0.97, abs=0.01)


def test_autocorrelacao_de_valores_alternados_e_negativa() -> None:
    assert estatistica.autocorrelacao_lag1(np.array([1.0, -1.0] * 20)) < -0.9


def test_autocorrelacao_de_valores_constantes_e_zero() -> None:
    assert estatistica.autocorrelacao_lag1(np.full(10, 3.0)) == 0
