"""Linhas iguais e quase iguais (R5, spec 12, D120).

Iguais: as mesmas células em todas as colunas comparadas. Quase iguais: numéricas padronizadas
a distância euclidiana < 0,01·√p, as demais colunas (e os faltantes) iguais, sem serem idênticas.

Com poucas colunas ou valores de pouca precisão, pares assim aparecem por acaso. O acaso vem da
densidade local: na grade da precisão de cada coluna (passos de 0,01 com 2 casas…), dados reais
têm tantos pares numa posição vizinha quanto na mesma posição. Conta-se quantos pares cabem, em
média, em cada posição de uma caixa de vizinhança, e daí os iguais e os quase iguais esperados.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from app.compartilhado.series import casas_decimais
from app.dominios.detector.tabela import ColunaDetector

FATOR_DISTANCIA = 0.01
VIZINHANCA = 3
"""A caixa de referência vai a 3 raios das quase iguais em cada coluna (e a 1 passo, no mínimo)."""
MAX_POSICOES_CONTADAS = 200_000
FOLGA = 1e-6
SEM_PARES = np.empty((0, 2), dtype="int64")
TRINCA = 3
"""3 linhas iguais seguidas ou mais: o padrão de "copiar e colar" (suspeita alta)."""


@dataclass(frozen=True, slots=True, eq=False)
class ColunasComparaveis:
    """Chaves das linhas: números (n × p, NaN nos faltantes) e códigos das demais colunas."""

    numeros: np.ndarray
    codigos: np.ndarray
    """n × q: cada texto vira um código; faltante = −1."""

    @property
    def n(self) -> int:
        return len(self.numeros)

    @property
    def p(self) -> int:
        return int(self.numeros.shape[1])


@dataclass(frozen=True, slots=True)
class ContraOAcaso:
    """Quantos casos foram vistos e quantos o acaso produziria (média de uma Poisson)."""

    observados: int
    esperados: float

    @property
    def p_valor(self) -> float:
        """P(X ≥ observados), X ~ Poisson(esperados)."""
        if self.observados == 0:
            return 1.0
        if self.esperados == 0:
            return 0.0
        return float(stats.poisson.sf(self.observados - 1, self.esperados))


@dataclass(frozen=True, slots=True)
class AcasoDasRepeticoes:
    iguais: ContraOAcaso
    quase: ContraOAcaso


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
    """Separa as numéricas (para a distância) das demais (comparadas pelo texto)."""
    n = len(colunas[0].textos)
    numericas = [coluna.numeros for coluna in colunas if coluna.numeros is not None]
    codigos = [
        pd.factorize(pd.Series(coluna.textos, dtype=object))[0]
        for coluna in colunas
        if coluna.numeros is None
    ]
    return ColunasComparaveis(
        numeros=np.column_stack(numericas) if numericas else np.empty((n, 0)),
        codigos=np.column_stack(codigos) if codigos else np.empty((n, 0), dtype="int64"),
    )


# Grupos -------------------------------------------------------------------------------------


def _ids(linhas: np.ndarray) -> np.ndarray:
    """Mesmo número para linhas iguais da matriz."""
    return np.asarray(np.unique(linhas, axis=0, return_inverse=True)[1]).ravel()


def _ids_exatos(chaves: ColunasComparaveis) -> np.ndarray:
    numeros = chaves.numeros
    return _ids(np.column_stack([chaves.codigos, np.nan_to_num(numeros), np.isnan(numeros)]))


def _ids_sem_numeros(chaves: ColunasComparaveis) -> np.ndarray:
    """Mesmo número para linhas com as mesmas não numéricas e os mesmos faltantes."""
    return _ids(np.column_stack([chaves.codigos, np.isnan(chaves.numeros)]))


def _pares_de_mesmo_id(ids: np.ndarray) -> np.ndarray:
    """Liga cada linha à próxima com o mesmo id (basta para formar as componentes)."""
    ordem = np.argsort(ids, kind="stable")
    mesmos = ids[ordem][1:] == ids[ordem][:-1]
    return np.column_stack((ordem[:-1][mesmos], ordem[1:][mesmos]))


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


def repetidos(chaves: ColunasComparaveis, quase: np.ndarray) -> tuple[GrupoRepetido, ...]:
    """Grupos de linhas idênticas, ligados também pelos pares quase iguais dados."""
    ids = _ids_exatos(chaves)
    pares = np.concatenate([_pares_de_mesmo_id(ids), quase])
    grupos = (
        GrupoRepetido(posicoes, bool(np.unique(ids[posicoes]).size == 1))
        for posicoes in _componentes(pares)
    )
    return tuple(sorted(grupos, key=lambda grupo: int(grupo.posicoes[0])))


# Quase iguais -------------------------------------------------------------------------------


def _desvios(numeros: np.ndarray) -> np.ndarray:
    desvios = np.nanstd(numeros, axis=0, ddof=1)
    return np.where(np.isfinite(desvios) & (desvios > 0), desvios, 1.0)


def _padronizados(numeros: np.ndarray) -> np.ndarray:
    """z por coluna, com 0 nos faltantes (o padrão de faltantes já separa as linhas)."""
    z = (numeros - np.nanmean(numeros, axis=0)) / _desvios(numeros)
    return np.asarray(np.nan_to_num(z), dtype="float64")


def _raio(chaves: ColunasComparaveis) -> float:
    return FATOR_DISTANCIA * math.sqrt(chaves.p)


def pares_quase_iguais(chaves: ColunasComparaveis) -> np.ndarray:
    """Pares não idênticos com as demais colunas iguais e distância padronizada < 0,01·√p."""
    pontos = _padronizados(chaves.numeros)
    raio = float(np.nextafter(_raio(chaves), 0))
    pares = [SEM_PARES]
    for posicoes in _grupos_por_id(_ids_sem_numeros(chaves)):
        locais = cKDTree(pontos[posicoes]).query_pairs(raio, output_type="ndarray")
        pares.append(posicoes[locais])
    juntos = np.concatenate(pares)
    exatos = _ids_exatos(chaves)
    return np.asarray(juntos[exatos[juntos[:, 0]] != exatos[juntos[:, 1]]], dtype="int64")


# Acaso --------------------------------------------------------------------------------------


def _passos(numeros: np.ndarray) -> np.ndarray:
    """Passo da precisão de cada coluna em desvios padrão (0,01 m com DP 0,09 m → 0,11)."""
    casas = [casas_decimais(pd.Series(coluna)) for coluna in numeros.T]
    return np.asarray(np.array([10.0**-c for c in casas]) / _desvios(numeros), dtype="float64")


def _posicoes_no_raio(passos: np.ndarray, raio: float) -> float:
    """Posições da grade (fora a origem) a distância < raio: as dos pares quase iguais."""
    alcance = np.floor(raio / passos).astype("int64")
    if np.prod(2.0 * alcance + 1) > MAX_POSICOES_CONTADAS:
        bola = math.pi ** (len(passos) / 2) / math.gamma(len(passos) / 2 + 1) * raio ** len(passos)
        return float(bola / np.prod(passos))
    grade = np.stack(np.meshgrid(*(np.arange(-a, a + 1) for a in alcance)), -1)
    distancias = np.sqrt(np.sum((grade * passos) ** 2, axis=-1))
    return float(np.count_nonzero(distancias < raio) - 1)


def _pares_na_caixa(chaves: ColunasComparaveis, meia_caixa: np.ndarray) -> int:
    """Pares com as demais colunas iguais e cada número a até `meia_caixa` (em DP)."""
    pontos = _padronizados(chaves.numeros) / meia_caixa
    total = 0
    for posicoes in _grupos_por_id(_ids_sem_numeros(chaves)):
        arvore = cKDTree(pontos[posicoes])
        total += (int(arvore.count_neighbors(arvore, 1 + FOLGA, p=np.inf)) - len(posicoes)) // 2
    return total


def _coincidencia(coluna: np.ndarray) -> float:
    """Chance de duas linhas sorteadas (sem reposição) terem o mesmo valor na coluna."""
    _, contagens = np.unique(coluna, return_counts=True)
    n = len(coluna)
    return float(np.sum(contagens * (contagens - 1)) / (n * (n - 1)))


def _iguais_independentes(chaves: ColunasComparaveis) -> float:
    """C(n,2) · Π P(coincidir na coluna j): o acaso se as colunas fossem independentes."""
    colunas = [*chaves.numeros.T, *chaves.codigos.T]
    return chaves.n * (chaves.n - 1) / 2 * math.prod(_coincidencia(c) for c in colunas)


def acaso_das_repeticoes(
    chaves: ColunasComparaveis, identicos: Sequence[GrupoRepetido], quase: np.ndarray
) -> AcasoDasRepeticoes:
    """Iguais e quase iguais observados × esperados pela densidade local (Poisson)."""
    iguais = sum(len(g.posicoes) * (len(g.posicoes) - 1) // 2 for g in identicos)
    independentes = _iguais_independentes(chaves)
    if chaves.p == 0:
        return AcasoDasRepeticoes(ContraOAcaso(iguais, independentes), ContraOAcaso(0, 0.0))
    passos = _passos(chaves.numeros)
    alcance = np.maximum(np.ceil(VIZINHANCA * _raio(chaves) / passos), 1)
    no_raio = _posicoes_no_raio(passos, _raio(chaves))
    na_caixa = float(np.prod(2 * alcance + 1)) - 1 - no_raio
    vizinhos = _pares_na_caixa(chaves, alcance * passos) - iguais - len(quase)
    por_posicao = max(vizinhos, 0) / na_caixa
    return AcasoDasRepeticoes(
        ContraOAcaso(iguais, max(por_posicao, independentes)),
        ContraOAcaso(len(quase), por_posicao * no_raio),
    )


def seguidas_contra_o_acaso(grupos: Sequence[GrupoRepetido], n: int) -> ContraOAcaso:
    """Grupos com 3 linhas seguidas × trincas esperadas com as linhas em ordem aleatória."""
    seguidas = sum(len(g.maior_sequencia) >= TRINCA for g in grupos)
    tamanhos = np.array([len(g.posicoes) for g in grupos], dtype="float64")
    esperadas = float(np.sum(tamanhos * (tamanhos - 1) * (tamanhos - 2)) / (n * (n - 1)))
    return ContraOAcaso(seguidas, esperadas)
