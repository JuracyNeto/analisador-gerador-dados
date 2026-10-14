"""Linhas iguais e quase iguais (R5, spec 12, D120).

Quase iguais: numéricas padronizadas a distância euclidiana < 0,01·√p e as demais colunas
(e os faltantes) iguais. Os grupos são as componentes ligadas dos pares encontrados.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from app.dominios.detector.tabela import ColunaDetector

FATOR_DISTANCIA = 0.01


@dataclass(frozen=True, slots=True, eq=False)
class ColunasComparaveis:
    """Chaves das linhas: números (n × p, NaN nos faltantes) e textos das demais colunas."""

    numeros: np.ndarray
    textos: pd.DataFrame

    @property
    def n(self) -> int:
        return len(self.textos)


@dataclass(frozen=True, slots=True, eq=False)
class GrupoRepetido:
    """Posições (crescentes) de linhas iguais ou quase iguais entre si."""

    posicoes: np.ndarray
    exato: bool

    @property
    def copias(self) -> int:
        return len(self.posicoes) - 1

    @property
    def maior_sequencia(self) -> np.ndarray:
        """Posições do maior trecho de linhas seguidas do grupo."""
        quebras = np.flatnonzero(np.diff(self.posicoes) != 1) + 1
        return max(np.split(self.posicoes, quebras), key=len)


def chaves_das_colunas(colunas: Sequence[ColunaDetector]) -> ColunasComparaveis:
    """Separa as colunas numéricas (para a distância) das demais (comparadas como texto)."""
    numericas = [coluna.numeros for coluna in colunas if coluna.numeros is not None]
    outras = [coluna.textos for coluna in colunas if coluna.numeros is None]
    n = len(colunas[0].textos)
    numeros = np.column_stack(numericas) if numericas else np.empty((n, 0))
    textos = pd.DataFrame(dict(enumerate(outras)), index=range(n), dtype=object)
    return ColunasComparaveis(numeros, textos)


def _ids(chaves: pd.DataFrame) -> np.ndarray:
    """Mesmo número para linhas com as mesmas chaves (faltantes iguais entre si)."""
    if chaves.shape[1] == 0:
        return np.zeros(len(chaves), dtype="int64")
    agrupado = chaves.set_axis(range(chaves.shape[1]), axis="columns")
    return agrupado.groupby(list(agrupado.columns), dropna=False, sort=False).ngroup().to_numpy()


def _ids_exatos(chaves: ColunasComparaveis) -> np.ndarray:
    return _ids(pd.concat([pd.DataFrame(chaves.numeros), chaves.textos], axis="columns"))


def _pares_de_mesmo_id(ids: np.ndarray) -> np.ndarray:
    """Liga cada linha à próxima com o mesmo id (basta para formar as componentes)."""
    ordem = np.argsort(ids, kind="stable")
    mesmos = ids[ordem][1:] == ids[ordem][:-1]
    return np.column_stack((ordem[:-1][mesmos], ordem[1:][mesmos]))


def _padronizados(numeros: np.ndarray) -> np.ndarray:
    """z por coluna; desvio zero não escala e faltante vira 0 (o padrão de NaN vai na chave)."""
    desvios = np.nanstd(numeros, axis=0, ddof=1)
    escalas = np.where(np.isfinite(desvios) & (desvios > 0), desvios, 1.0)
    return np.nan_to_num((numeros - np.nanmean(numeros, axis=0)) / escalas)


def _pares_proximos(chaves: ColunasComparaveis) -> np.ndarray:
    """Pares com as demais colunas iguais e distância padronizada < 0,01·√p."""
    p = chaves.numeros.shape[1]
    raio = float(np.nextafter(FATOR_DISTANCIA * math.sqrt(p), 0))
    pontos = _padronizados(chaves.numeros)
    faltantes = pd.DataFrame(np.isnan(chaves.numeros))
    ids = _ids(pd.concat([chaves.textos, faltantes.add_prefix("nan")], axis="columns"))
    pares = [np.empty((0, 2), dtype="int64")]
    for posicoes in _grupos_por_id(ids):
        locais = cKDTree(pontos[posicoes]).query_pairs(raio, output_type="ndarray")
        pares.append(posicoes[locais])
    return np.concatenate(pares)


def _grupos_por_id(ids: np.ndarray) -> list[np.ndarray]:
    """Posições de cada id com 2 linhas ou mais."""
    ordem = np.argsort(ids, kind="stable")
    fronteiras = np.flatnonzero(np.diff(ids[ordem])) + 1
    return [grupo for grupo in np.split(ordem, fronteiras) if len(grupo) > 1]


def _componentes(pares: np.ndarray) -> list[np.ndarray]:
    """Grupos de linhas ligadas pelos pares, cada um com as posições em ordem."""
    if len(pares) == 0:
        return []
    nos, locais = np.unique(pares, return_inverse=True)
    locais = locais.reshape(pares.shape)
    grafo = coo_matrix((np.ones(len(pares)), (locais[:, 0], locais[:, 1])), (len(nos),) * 2)
    _, rotulos = connected_components(grafo, directed=False)
    return [np.sort(nos[grupo]) for grupo in _grupos_por_id(rotulos)]


def _grupos(pares: np.ndarray, ids_exatos: np.ndarray) -> tuple[GrupoRepetido, ...]:
    grupos = (
        GrupoRepetido(posicoes, bool(np.unique(ids_exatos[posicoes]).size == 1))
        for posicoes in _componentes(pares)
    )
    return tuple(sorted(grupos, key=lambda grupo: int(grupo.posicoes[0])))


def repetidos_exatos(chaves: ColunasComparaveis) -> tuple[GrupoRepetido, ...]:
    """Grupos de linhas idênticas em todas as colunas comparadas."""
    ids = _ids_exatos(chaves)
    return _grupos(_pares_de_mesmo_id(ids), ids)


def repetidos_ou_quase(chaves: ColunasComparaveis) -> tuple[GrupoRepetido, ...]:
    """Grupos de linhas idênticas ou quase iguais (O(n log n) com árvore k-d)."""
    ids = _ids_exatos(chaves)
    pares = _pares_de_mesmo_id(ids)
    if chaves.numeros.shape[1] > 0:
        pares = np.concatenate([pares, _pares_proximos(chaves)])
    return _grupos(pares, ids)
