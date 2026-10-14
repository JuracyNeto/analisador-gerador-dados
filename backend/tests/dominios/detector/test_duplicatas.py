import numpy as np
import pandas as pd

from app.compartilhado.tipos import TipoVariavel
from app.dominios.detector.duplicatas import (
    ColunasComparaveis,
    GrupoRepetido,
    chaves_das_colunas,
    repetidos_exatos,
    repetidos_ou_quase,
)
from tests.dominios.detector.apoio import tabela_de

TIPOS = {"a": TipoVariavel.CONTINUA, "b": TipoVariavel.NOMINAL}


def _chaves(a: list[float | None], b: list[str | None]) -> ColunasComparaveis:
    tabela = tabela_de(pd.DataFrame({"a": a, "b": b}), TIPOS)
    return chaves_das_colunas(tuple(tabela.colunas.values()))


def _posicoes(grupos: tuple[GrupoRepetido, ...]) -> list[list[int]]:
    return [grupo.posicoes.tolist() for grupo in grupos]


def test_linhas_identicas_formam_um_grupo() -> None:
    chaves = _chaves([1.0, 2.0, 1.0, 3.0, 2.0], ["x", "y", "x", "x", "z"])

    assert _posicoes(repetidos_exatos(chaves)) == [[0, 2]]


def test_faltantes_iguais_contam_como_iguais() -> None:
    chaves = _chaves([None, 2.0, None], [None, "y", None])

    assert _posicoes(repetidos_exatos(chaves)) == [[0, 2]]


def test_quase_iguais_entram_com_as_identicas() -> None:
    a = [float(v) for v in range(1, 21)]
    a[15] = 4.001
    a[18] = 9.0
    chaves = _chaves(a, ["x"] * 20)

    grupos = repetidos_ou_quase(chaves)

    assert _posicoes(grupos) == [[3, 15], [8, 18]]
    assert [grupo.exato for grupo in grupos] == [False, True]


def test_quase_iguais_precisam_ter_as_qualitativas_iguais() -> None:
    a = [float(v) for v in range(1, 21)]
    a[15] = 4.001
    b = ["x"] * 20
    b[15] = "y"

    assert repetidos_ou_quase(_chaves(a, b)) == ()


def test_sem_colunas_numericas_quase_iguais_sao_as_identicas() -> None:
    tabela = tabela_de(
        pd.DataFrame({"b": ["x", "y", "x"], "c": ["1", "2", "1"]}),
        {"b": TipoVariavel.NOMINAL, "c": TipoVariavel.NOMINAL},
    )

    grupos = repetidos_ou_quase(chaves_das_colunas(tuple(tabela.colunas.values())))

    assert _posicoes(grupos) == [[0, 2]]


def test_maior_sequencia_de_linhas_seguidas() -> None:
    grupo = GrupoRepetido(np.array([2, 10, 11, 12, 30]), exato=True)

    assert grupo.maior_sequencia.tolist() == [10, 11, 12]
    assert grupo.copias == 4
