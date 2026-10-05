import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.separatrizes import separatrizes
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

UM_A_DEZ = [float(i) for i in range(1, 11)]


def test_quartis_decis_e_percentis_por_interpolacao(criar_amostra: CriarAmostra) -> None:
    resultado = separatrizes(criar_amostra(TipoVariavel.CONTINUA, UM_A_DEZ))

    assert resultado is not None
    # h = (n − 1)·p: Q1 → h = 2,25 → 3 + 0,25·(4 − 3) = 3,25
    assert [q.valor for q in resultado.quartis] == [3.25, 5.5, 7.75]
    assert [q.rotulo for q in resultado.quartis] == ["Q1", "Q2", "Q3"]
    assert resultado.decis[0].valor == pytest.approx(1.9)
    assert len(resultado.percentis) == 99
    assert resultado.percentis[-1].valor == pytest.approx(9.91)
    assert "P50" in resultado.destaques


def test_separatrizes_ordinais_sao_categorias(criar_amostra: CriarAmostra) -> None:
    valores = ["ruim", "regular", "bom", "bom"]

    resultado = separatrizes(criar_amostra(TipoVariavel.ORDINAL, valores, ESCALA_SATISFACAO))

    assert resultado is not None
    assert [q.valor for q in resultado.quartis] == ["ruim", "regular", "bom"]


def test_separatrizes_nao_se_aplicam_a_nominal(criar_amostra: CriarAmostra) -> None:
    assert separatrizes(criar_amostra(TipoVariavel.NOMINAL, ["a", "b"])) is None
