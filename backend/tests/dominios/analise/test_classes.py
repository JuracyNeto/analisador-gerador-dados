import pandas as pd
import pytest

from app.dominios.analise.classes import agrupar, amplitude_de_classe, k_sturges

DEZ_VALORES = pd.Series([2.0, 3.5, 4.0, 5.5, 6.0, 7.5, 8.0, 9.5, 10.0, 11.5])


@pytest.mark.parametrize(("n", "k"), [(10, 5), (227, 9), (230, 9), (1, 1), (1000, 11)])
def test_k_de_sturges(n: int, k: int) -> None:
    assert k_sturges(n) == k


def test_amplitude_arredonda_para_cima_na_casa_dos_dados() -> None:
    # Exemplo do design (4b): AT = 49,1 e k = 9 → h = 5,4555… → 5,5.
    assert amplitude_de_classe(49.1, 9, 1) == 5.5
    assert amplitude_de_classe(9.5, 5, 1) == 1.9


def test_classes_por_sturges() -> None:
    agrupamento = agrupar(DEZ_VALORES, None)

    assert (agrupamento.k, agrupamento.h, agrupamento.metodo) == (5, 1.9, "sturges")
    assert [c.inferior for c in agrupamento.classes] == [2.0, 3.9, 5.8, 7.7, 9.6]
    assert [c.frequencia for c in agrupamento.classes] == [2, 2, 2, 2, 2]
    assert agrupamento.classes[0].ponto_medio == pytest.approx(2.95)


def test_classes_escolhidas_pelo_usuario() -> None:
    agrupamento = agrupar(DEZ_VALORES, 3)

    assert (agrupamento.k, agrupamento.h, agrupamento.metodo) == (3, 3.2, "usuario")
    assert [c.frequencia for c in agrupamento.classes] == [3, 4, 3]


def test_limite_da_esquerda_entra_e_ultima_classe_e_fechada() -> None:
    agrupamento = agrupar(pd.Series([0.0, 1.0, 2.0, 3.0, 4.0]), 2)

    assert [c.frequencia for c in agrupamento.classes] == [2, 3]


def test_valores_iguais_formam_uma_classe() -> None:
    agrupamento = agrupar(pd.Series([5.0, 5.0, 5.0]), None)

    assert (agrupamento.k, agrupamento.h) == (1, 0.0)
    assert agrupamento.classes[0].frequencia == 3
