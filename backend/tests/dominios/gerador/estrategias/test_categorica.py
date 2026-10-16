import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.gerador.estrategias.base import EntradaEstrategia
from app.dominios.gerador.univariado import gerar_univariado


def test_binaria_preserva_a_proporcao_do_sucesso() -> None:
    origem = pd.Series(["F"] * 30 + ["M"] * 70)
    entrada = EntradaEstrategia(10_000, "preservar", origem, rotulos=("M", "F"))

    resultado = gerar_univariado(TipoVariavel.BINARIA, entrada, 42)

    assert resultado.metodo == "bernoulli"
    assert set(resultado.valores) == {"F", "M"}
    assert (resultado.valores == "F").mean() == pytest.approx(0.3, abs=0.02)


def test_binaria_com_chance_informada() -> None:
    entrada = EntradaEstrategia(10_000, "parametros", p=0.8, rotulos=("0", "1"))

    valores = gerar_univariado(TipoVariavel.BINARIA, entrada, 1).valores

    assert (valores == "1").mean() == pytest.approx(0.8, abs=0.02)


@pytest.mark.parametrize("tipo", [TipoVariavel.NOMINAL, TipoVariavel.ORDINAL])
def test_categorias_pelas_frequencias(tipo: TipoVariavel) -> None:
    origem = pd.Series(["a"] * 50 + ["b"] * 30 + ["c"] * 20)

    resultado = gerar_univariado(tipo, EntradaEstrategia(10_000, "preservar", origem), 42)

    assert resultado.metodo == "frequencias"
    frequencias = resultado.valores.value_counts(normalize=True)
    assert frequencias["a"] == pytest.approx(0.5, abs=0.02)
    assert set(frequencias.index) == {"a", "b", "c"}


def test_mesma_semente_mesmas_categorias() -> None:
    entrada = EntradaEstrategia(50, "preservar", pd.Series(list("abcabc")))

    primeira = gerar_univariado(TipoVariavel.NOMINAL, entrada, 9).valores
    segunda = gerar_univariado(TipoVariavel.NOMINAL, entrada, 9).valores

    assert np.array_equal(primeira.to_numpy(), segunda.to_numpy())
