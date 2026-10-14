"""Blocos e trechos de linhas seguidas (R1, R2, R3, R11; D122).

Janelas de k valores seguidos e o restante de cada uma saem de somas acumuladas de x e x² (O(n)
para todas as janelas), o que deixa a simulação da R1 — a melhor janela de cada embaralhamento da
coluna — vetorizada.
"""

from collections.abc import Iterator
from itertools import pairwise

import numpy as np

LIMITE_ELEMENTOS = 1_000_000
"""Embaralhamentos por lote: até 1 milhão de valores na matriz (memória limitada)."""
PARTES = 5


def _acumulada(matriz: np.ndarray) -> np.ndarray:
    """Somas acumuladas por linha, com um zero na frente (soma da janela = diferença)."""
    acumulada = np.zeros((matriz.shape[0], matriz.shape[1] + 1))
    np.cumsum(matriz, axis=1, out=acumulada[:, 1:])
    return acumulada


def _desvios(somas: np.ndarray, quadrados: np.ndarray, tamanho: int) -> np.ndarray:
    """DP amostral de `tamanho` valores a partir de Σ(x − c) e Σ(x − c)²."""
    variancias = (quadrados - somas * somas / tamanho) / (tamanho - 1)
    return np.asarray(np.sqrt(np.clip(variancias, 0, None)), dtype="float64")


def afastamentos_do_resto(matriz: np.ndarray, k: int) -> np.ndarray:
    """max(dᵤ, dₛ) de cada janela de k colunas seguidas contra o restante da linha.

    dᵤ = |x̄_janela − x̄_resto| / s_resto e dₛ = |s_janela − s_resto| / s_resto. O resto sai do
    total menos a janela. Com o resto constante (s_resto = 0), a janela fica infinitamente longe.
    """
    numeros = np.asarray(matriz, dtype="float64")
    # Centrar na média geral evita perder precisão nas somas dos quadrados.
    centrados = numeros - numeros.mean()
    acumulada, quadrados = _acumulada(centrados), _acumulada(centrados * centrados)
    soma, quadrado = acumulada[:, k:] - acumulada[:, :-k], quadrados[:, k:] - quadrados[:, :-k]
    resto = numeros.shape[1] - k
    soma_resto, quadrado_resto = acumulada[:, -1:] - soma, quadrados[:, -1:] - quadrado
    desvio_resto = _desvios(soma_resto, quadrado_resto, resto)
    diferencas = np.maximum(
        np.abs(soma / k - soma_resto / resto),
        np.abs(_desvios(soma, quadrado, k) - desvio_resto),
    )
    afastamentos = np.full(diferencas.shape, np.inf)
    np.divide(diferencas, desvio_resto, out=afastamentos, where=desvio_resto > 0)
    return afastamentos


def embaralhados(
    valores: np.ndarray,
    quantidade: int,
    rng: np.random.Generator,
    limite_elementos: int = LIMITE_ELEMENTOS,
) -> Iterator[np.ndarray]:
    """`quantidade` embaralhamentos dos valores, em lotes (uma linha por embaralhamento)."""
    numeros = np.asarray(valores, dtype="float64")
    por_lote = max(1, limite_elementos // len(numeros))
    for inicio in range(0, quantidade, por_lote):
        linhas = min(por_lote, quantidade - inicio)
        yield rng.permuted(np.tile(numeros, (linhas, 1)), axis=1)


def dividir_em_blocos(n: int, partes: int = PARTES) -> tuple[slice, ...]:
    """Partes seguidas de tamanhos quase iguais (as primeiras ficam com a sobra)."""
    bordas = np.cumsum([0] + [n // partes + (i < n % partes) for i in range(partes)])
    return tuple(slice(int(a), int(b)) for a, b in pairwise(bordas))


def trechos_iguais(valores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Início e tamanho de cada trecho de valores iguais seguidos."""
    if len(valores) == 0:
        return np.array([], dtype="int64"), np.array([], dtype="int64")
    inicios = np.concatenate(([0], np.flatnonzero(np.diff(valores) != 0) + 1))
    return inicios, np.diff(np.concatenate((inicios, [len(valores)])))
