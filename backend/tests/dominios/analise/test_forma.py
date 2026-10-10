import numpy as np
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.forma import (
    assimetria,
    classificar_assimetria,
    classificar_curtose,
    curtose,
    curtose_percentilica,
    pearson,
)
from app.dominios.analise.separatrizes import separatrizes
from tests.dominios.analise.conftest import CriarAmostra

# Amostra de livro: x̄ = 5, s = 2,1381, Md = 4,5, Mo = 4 (valores conferidos com scipy 1.18).
LIVRO = [2, 4, 4, 4, 5, 5, 7, 9]


def valores(lista: list[float]) -> np.ndarray:
    return np.asarray(lista, dtype="float64")


def test_assimetria_de_fisher_amostral() -> None:
    medida = assimetria(valores(LIVRO))

    assert medida.valor == pytest.approx(0.818488, rel=1e-5)
    assert medida.formula == "assimetria"
    assert medida.interpretacao == (
        "Assimetria moderada à direita: há valores altos mais afastados do centro."
    )
    assert (medida.calculo or "").endswith("= 0,8185")


@pytest.mark.parametrize(
    ("g1", "esperado"),
    [
        (0.818, ("moderada", "direita")),
        (-0.3, ("simetrica", "esquerda")),
        (1.4, ("forte", "direita")),
        (-1.0, ("moderada", "esquerda")),
        (0.0, ("simetrica", None)),
    ],
)
def test_classifica_assimetria(g1: float, esperado: tuple[str, str | None]) -> None:
    assert classificar_assimetria(g1) == esperado


def test_curtose_em_excesso() -> None:
    medida = curtose(valores(LIVRO))

    assert medida.valor == pytest.approx(0.940625, rel=1e-5)
    assert medida.formula == "curtose"
    assert (medida.interpretacao or "").startswith("Leptocúrtica:")


@pytest.mark.parametrize(
    ("g2", "classe"),
    [(0.94, "leptocurtica"), (-0.18, "mesocurtica"), (0.5, "mesocurtica"), (-0.9, "platicurtica")],
)
def test_classifica_curtose(g2: float, classe: str) -> None:
    assert classificar_curtose(g2) == classe


def test_coeficientes_de_pearson() -> None:
    as1, as2 = pearson(valores(LIVRO), moda=4.0, mediana=4.5)

    assert as1.valor == pytest.approx(0.467707, rel=1e-5)
    assert as2.valor == pytest.approx(0.701561, rel=1e-5)
    assert (as1.formula, as2.formula) == ("assimetria_pearson_1", "assimetria_pearson_2")


def test_pearson_sem_moda_unica_nao_se_aplica() -> None:
    as1, as2 = pearson(valores([1, 1, 2, 2, 3]), moda=None, mediana=2.0)

    assert not as1.aplicavel
    assert as1.motivo == "1º coeficiente de Pearson não se aplica: precisa de uma moda única."
    assert as2.aplicavel


def test_curtose_percentilica_usa_quartis_e_decis(criar_amostra: CriarAmostra) -> None:
    seps = separatrizes(criar_amostra(TipoVariavel.DISCRETA, LIVRO))
    assert seps is not None

    medida = curtose_percentilica(seps)

    # (5,5 − 4) / (2 · (7,6 − 3,4))
    assert medida.valor == pytest.approx(0.178571, rel=1e-5)
    assert medida.formula == "curtose_percentilica"


def test_curtose_percentilica_sem_espalhamento(criar_amostra: CriarAmostra) -> None:
    seps = separatrizes(criar_amostra(TipoVariavel.DISCRETA, [1, *[5] * 18, 9]))
    assert seps is not None

    assert not curtose_percentilica(seps).aplicavel


def test_poucos_valores_nao_se_aplica() -> None:
    assert assimetria(valores([1, 2])).motivo == (
        "Assimetria não se aplica: precisa de pelo menos 3 valores."
    )
    assert curtose(valores([1, 2, 3])).motivo == (
        "Curtose não se aplica: precisa de pelo menos 4 valores."
    )


def test_valores_iguais_nao_tem_forma() -> None:
    medida = assimetria(valores([3, 3, 3, 3]))

    assert not medida.aplicavel
    assert "não há variação" in (medida.motivo or "")
    assert not pearson(valores([3, 3, 3, 3]), moda=3.0, mediana=3.0)[1].aplicavel
