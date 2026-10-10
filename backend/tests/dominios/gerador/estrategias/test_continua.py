import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.gerador.estrategias.base import EntradaEstrategia
from app.dominios.gerador.univariado import gerar_univariado

NORMAIS = pd.Series(np.round(np.random.default_rng(3).normal(70, 11, 227), 1))


def _gerar(entrada: EntradaEstrategia, semente: int = 42) -> pd.Series:
    return gerar_univariado(TipoVariavel.CONTINUA, entrada, semente).valores


def test_preservar_normal_bate_media_e_desvio() -> None:
    entrada = EntradaEstrategia(500, "preservar", NORMAIS, normal_compativel=True, casas=6)

    resultado = gerar_univariado(TipoVariavel.CONTINUA, entrada, 42)

    assert resultado.metodo == "normal"
    assert resultado.valores.mean() == pytest.approx(NORMAIS.mean(), rel=1e-6)
    assert resultado.valores.std(ddof=1) == pytest.approx(NORMAIS.std(ddof=1), rel=1e-6)


def test_preservar_arredonda_nas_casas_do_original() -> None:
    valores = _gerar(EntradaEstrategia(500, "preservar", NORMAIS, normal_compativel=True, casas=1))

    assert np.allclose(valores * 10, np.round(valores * 10))
    assert abs(valores.mean() - NORMAIS.mean()) / NORMAIS.mean() < 0.01


def test_preservar_nao_normal_usa_kde() -> None:
    exponenciais = pd.Series(np.random.default_rng(1).exponential(1, 300))

    resultado = gerar_univariado(
        TipoVariavel.CONTINUA, EntradaEstrategia(300, "preservar", exponenciais, casas=6), 1
    )

    assert resultado.metodo == "kde"
    assert resultado.valores.mean() == pytest.approx(exponenciais.mean(), rel=1e-6)


def test_parametros_sem_origem() -> None:
    valores = _gerar(EntradaEstrategia(1000, "parametros", media=50.0, desvio=5.0, casas=2))

    assert valores.mean() == pytest.approx(50.0, rel=1e-3)
    assert valores.std(ddof=1) == pytest.approx(5.0, rel=1e-2)


def test_limitar_faixa_fica_dentro_do_original() -> None:
    entrada = EntradaEstrategia(
        500, "preservar", NORMAIS, normal_compativel=True, casas=1, limitar_faixa=True
    )

    valores = _gerar(entrada)

    assert valores.min() >= NORMAIS.min()
    assert valores.max() <= NORMAIS.max()


def test_mesma_semente_mesmo_resultado() -> None:
    entrada = EntradaEstrategia(100, "preservar", NORMAIS, casas=1)

    assert np.array_equal(_gerar(entrada, 7), _gerar(entrada, 7))
    assert not np.array_equal(_gerar(entrada, 7), _gerar(entrada, 8))
