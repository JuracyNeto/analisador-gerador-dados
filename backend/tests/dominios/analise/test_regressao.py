import numpy as np
import pytest

from app.dominios.analise.regressao import prever, regressao, residuos
from app.dominios.analise.resultados_bivariada import Faixa

# Exemplo de livro: b = 0,6; a = 2,2; R² = 60%; Sₑ = √0,8 (conferido com scipy.linregress).
X = np.array([1, 2, 3, 4, 5.0])
Y = np.array([2, 4, 5, 4, 5.0])
NOMES = ("x", "y")


def test_coeficientes_da_reta() -> None:
    reg = regressao(X, Y, NOMES)

    assert reg.a == pytest.approx(2.2)
    assert reg.b == pytest.approx(0.6)
    assert reg.equacao == "Ŷ = 2,2 + 0,6·X"
    assert reg.r2.valor == pytest.approx(60.0)
    assert reg.se.valor == pytest.approx(0.894427, rel=1e-5)


def test_textos_da_reta() -> None:
    reg = regressao(X, Y, NOMES)

    assert reg.reta.valor == "Ŷ = 2,2 + 0,6·X"
    assert reg.reta.calculo == "b = Sxy / Sxx = 6 / 10 = 0,6 · a = ȳ − b·x̄ = 4 − 0,6 · 3 = 2,2"
    assert reg.reta.interpretacao == (
        "A cada 1 a mais em x, o valor previsto de y sobe cerca de 0,6."
    )
    assert reg.r2.interpretacao == "60% da variação de y é explicada por x."
    assert (reg.reta.formula, reg.r2.formula, reg.se.formula) == (
        "regressao",
        "r2",
        "erro_padrao_estimativa",
    )


def test_residuos() -> None:
    assert residuos(X, Y, a=2.2, b=0.6) == pytest.approx([-0.8, 0.6, 1.0, -0.6, -0.2])


def test_previsao_dentro_da_faixa() -> None:
    previsao = prever(2.2, 0.6, valor=3.5, faixa=Faixa(1, 5), nomes=NOMES)

    assert previsao.y_previsto == pytest.approx(4.3)
    assert not previsao.extrapolacao
    assert previsao.aviso is None
    assert previsao.frase == "Para x = 3,5, o valor previsto de y é 4,3."


@pytest.mark.parametrize("valor", [0.5, 8.0])
def test_previsao_fora_da_faixa_avisa(valor: float) -> None:
    previsao = prever(2.2, 0.6, valor=valor, faixa=Faixa(1, 5), nomes=NOMES)

    assert previsao.extrapolacao
    assert (previsao.aviso or "").startswith("Os valores de x vão de 1 a 5.")


@pytest.mark.parametrize("valor", [1.0, 5.0])
def test_limites_da_faixa_nao_sao_extrapolacao(valor: float) -> None:
    assert not prever(2.2, 0.6, valor=valor, faixa=Faixa(1, 5), nomes=NOMES).extrapolacao
