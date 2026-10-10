import numpy as np
import pandas as pd
import pytest

from app.dominios.analise.servico import ServicoAnalise


def test_resumo_numerico_confere_com_numpy_e_scipy() -> None:
    valores = np.array([1, 2, 3, 4, 10.0])

    resumo = ServicoAnalise.resumo_numerico(valores)

    assert resumo.n == 5
    assert resumo.media == pytest.approx(4.0)
    assert resumo.mediana == pytest.approx(3.0)
    assert resumo.desvio_padrao == pytest.approx(float(np.std(valores, ddof=1)))
    assert (resumo.minimo, resumo.maximo) == (1.0, 10.0)
    assert resumo.assimetria == pytest.approx(1.69706, rel=1e-4)
    assert resumo.curtose is not None


def test_resumo_numerico_sem_forma_com_poucos_valores() -> None:
    resumo = ServicoAnalise.resumo_numerico(np.array([1.0, 2.0]))

    assert resumo.assimetria is None
    assert resumo.curtose is None


def test_resumo_numerico_sem_variacao() -> None:
    resumo = ServicoAnalise.resumo_numerico(np.array([5.0, 5.0, 5.0, 5.0]))

    assert resumo.desvio_padrao == 0
    assert resumo.assimetria is None


def test_sucesso_padrao_da_binaria() -> None:
    assert ServicoAnalise.sucesso_padrao(pd.Series(["não", "sim", "sim"])) == "sim"
    assert ServicoAnalise.sucesso_padrao(pd.Series(["F", "M", "M"])) == "F"
