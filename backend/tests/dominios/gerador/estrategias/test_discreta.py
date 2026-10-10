import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.gerador.estrategias.base import EntradaEstrategia
from app.dominios.gerador.estrategias.discreta import parece_poisson
from app.dominios.gerador.univariado import gerar_univariado


def _gerar(entrada: EntradaEstrategia) -> tuple[pd.Series, str]:
    resultado = gerar_univariado(TipoVariavel.DISCRETA, entrada, 42)
    return resultado.valores, resultado.metodo


def test_media_e_variancia_parecidas_viram_poisson() -> None:
    contagens = pd.Series(np.random.default_rng(2).poisson(3, 400))

    valores, metodo = _gerar(EntradaEstrategia(2000, "preservar", contagens))

    assert metodo == "poisson"
    assert valores.dtype == "int64"
    assert valores.mean() == pytest.approx(contagens.mean(), rel=0.05)


def test_variancia_grande_vira_empirica() -> None:
    contagens = pd.Series([0, 0, 1, 9, 9, 10, 2, 8, 0, 10])

    valores, metodo = _gerar(EntradaEstrategia(500, "preservar", contagens))

    assert metodo == "empirica"
    assert set(valores) <= set(contagens)


@pytest.mark.parametrize(
    ("valores", "esperado"), [([3, 3, 3, 4, 2], False), ([0, 0, 0], False), ([1, 2, 3, 4, 5], True)]
)
def test_parece_poisson(valores: list[int], esperado: bool) -> None:
    assert parece_poisson(np.array(valores, dtype="float64")) is esperado


def test_parametros_inteiros_sem_negativos_quando_o_original_nao_tem() -> None:
    origem = pd.Series([0, 1, 2, 3, 4])

    valores, metodo = _gerar(EntradaEstrategia(500, "parametros", origem, media=1.0, desvio=3.0))

    assert metodo == "normal_inteira"
    assert valores.min() >= 0
    assert valores.dtype == "int64"


def test_parametros_sem_origem_podem_ser_negativos() -> None:
    valores, _ = _gerar(EntradaEstrategia(500, "parametros", media=0.0, desvio=3.0))

    assert valores.min() < 0
