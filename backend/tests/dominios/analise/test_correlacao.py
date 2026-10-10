import numpy as np
import pandas as pd
import pytest

from app.dominios.analise import correlacao
from app.dominios.analise.correlacao import (
    classificar,
    matriz_correlacao,
    pearson,
    somas,
    spearman,
)

# Exemplo de livro (conferido com scipy 1.18): r = 0,774597, p = 0,124027, ρ = 0,737865.
X = np.array([1, 2, 3, 4, 5.0])
Y = np.array([2, 4, 5, 4, 5.0])


def test_somas_dos_desvios() -> None:
    resultado = somas(X, Y)

    assert (resultado.sxx, resultado.syy, resultado.sxy) == (10.0, 6.0, 6.0)
    assert (resultado.media_x, resultado.media_y) == (3.0, 4.0)


def test_pearson_do_exemplo() -> None:
    medida = pearson(X, Y)

    assert medida.valor == pytest.approx(0.774597, rel=1e-5)
    assert medida.formula == "pearson"
    assert medida.calculo == "r = Sxy / √(Sxx · Syy) = 6 / √(10 · 6) = 0,7746"


def test_teste_t_do_exemplo() -> None:
    medida = correlacao.teste_t(0.774597, n=5)

    assert medida.valor == pytest.approx(0.124027, rel=1e-4)
    assert medida.formula == "teste_t_correlacao"
    assert "não é significativa" in (medida.interpretacao or "")
    assert medida.calculo == "t = 2,121 · gl = 3 · p = 0,124"


def test_spearman_do_exemplo() -> None:
    medida = spearman(X, Y)

    assert medida.valor == pytest.approx(0.737865, rel=1e-5)
    assert medida.formula == "spearman"


@pytest.mark.parametrize(
    ("y", "r", "sentido"),
    [(2 * X + 1, 1.0, "positiva"), (-3 * X + 10, -1.0, "negativa")],
)
def test_relacoes_perfeitas(y: np.ndarray, r: float, sentido: str) -> None:
    assert pearson(X, y).valor == pytest.approx(r)
    medida = correlacao.teste_t(r, n=5)
    assert medida.valor == 0.0
    assert medida.calculo == "t = ∞ · gl = 3 · p < 0,001"
    assert classificar(r) == ("forte", sentido)


def test_sem_relacao_e_fraca() -> None:
    rng = np.random.default_rng(3)
    x, y = rng.normal(size=500), rng.normal(size=500)

    valor = pearson(x, y).valor
    assert isinstance(valor, float)
    assert classificar(valor)[0] == "fraca"


@pytest.mark.parametrize(
    ("r", "esperado"),
    [
        (0.29, ("fraca", "positiva")),
        (0.3, ("moderada", "positiva")),
        (-0.69, ("moderada", "negativa")),
        (0.7, ("forte", "positiva")),
        (0.0, ("fraca", "nula")),
    ],
)
def test_limites_de_forca(r: float, esperado: tuple[str, str]) -> None:
    assert classificar(r) == esperado


def test_matriz_de_correlacao() -> None:
    a = np.arange(1, 11, dtype="float64")
    tabela = pd.DataFrame(
        {
            "a": a,
            "b": 2 * a,
            "c": np.random.default_rng(1).normal(size=10),
            "d": [1.0, 2.0, *[np.nan] * 8],
        }
    )

    matriz = matriz_correlacao(tabela)

    assert matriz.colunas == ("a", "b", "c", "d")
    assert matriz.valores[0][1] == pytest.approx(1.0)
    assert matriz.valores[0][0] == pytest.approx(1.0)
    assert matriz.valores[0][3] is None
    assert matriz.resumo.startswith("O par mais forte é a × b (1).")
    assert all(isinstance(v, float) or v is None for linha in matriz.valores for v in linha)


def test_matriz_com_uma_coluna() -> None:
    matriz = matriz_correlacao(pd.DataFrame({"a": [1.0, 2.0, 3.0]}))

    assert matriz.colunas == ("a",)
    assert matriz.resumo == "Precisa de pelo menos duas colunas numéricas para montar a matriz."


def test_t_negativo_usa_o_sinal_de_menos() -> None:
    assert (correlacao.teste_t(-0.06, n=218).calculo or "").startswith("t = −0,8")
