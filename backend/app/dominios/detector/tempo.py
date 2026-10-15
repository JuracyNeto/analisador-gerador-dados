"""Linha do tempo do arquivo: a coluna de data que acompanha a ordem das linhas (D130, D137)."""

import numpy as np
from scipy import stats

from app.compartilhado.tipos import TipoVariavel
from app.dominios.detector.tabela import TabelaDetector

MINIMO_ACOMPANHA = 0.5
"""ρ de Spearman mínimo entre a data e o número da linha para ela ser a linha do tempo."""
MINIMO_DATAS = 2


def acompanha_as_linhas(datas: np.ndarray) -> float:
    """ρ de Spearman entre as datas e o número da linha (só as linhas com data)."""
    validas = ~np.isnat(datas)
    valores = datas[validas].astype("int64")
    if len(valores) < MINIMO_DATAS or np.ptp(valores) == 0:
        return 0.0
    return float(stats.spearmanr(np.flatnonzero(validas), valores).statistic)


def colunas_de_datas(tabela: TabelaDetector) -> list[tuple[str, np.ndarray]]:
    """Nome e datas de cada coluna `data`, na ordem do arquivo."""
    return [
        (coluna.nome, coluna.datas)
        for coluna in tabela.do_tipo({TipoVariavel.DATA})
        if coluna.datas is not None
    ]


def coluna_do_tempo(tabela: TabelaDetector) -> str | None:
    """A coluna de data que mais acompanha as linhas (ρ ≥ 0,5), ou None se nenhuma acompanha.

    Com ela, o arquivo é uma série no tempo: valores vizinhos costumam ser parecidos.
    """
    colunas = colunas_de_datas(tabela)
    if not colunas:
        return None
    acompanham = [acompanha_as_linhas(datas) for _, datas in colunas]
    melhor = int(np.argmax(acompanham))
    return colunas[melhor][0] if acompanham[melhor] >= MINIMO_ACOMPANHA else None
