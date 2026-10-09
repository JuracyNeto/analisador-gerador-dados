import pytest

from app.compartilhado.estatistica import ALFA, agrupar_esperados_pequenos


def test_alfa_padrao() -> None:
    assert ALFA == 0.05


def test_agrupar_junta_as_caudas_com_esperado_pequeno() -> None:
    observados, esperados = agrupar_esperados_pequenos(
        [1, 3, 10, 12, 4, 1], [0.5, 2.5, 11, 11, 4, 2]
    )

    assert observados == [14, 12, 5]
    assert esperados == pytest.approx([14.0, 11.0, 6.0])


def test_agrupar_sem_grupos_pequenos_nao_muda() -> None:
    assert agrupar_esperados_pequenos([6, 7], [6.5, 6.5]) == ([6, 7], [6.5, 6.5])


def test_grupo_pequeno_no_meio_junta_ao_vizinho_menor() -> None:
    observados, esperados = agrupar_esperados_pequenos([8, 2, 6, 9], [7, 3, 6, 9])

    assert (observados, esperados) == ([8, 8, 9], [7, 9, 9])


def test_tudo_pequeno_vira_um_grupo_so() -> None:
    assert agrupar_esperados_pequenos([1, 1, 1], [1, 1, 1]) == ([3], [3])
