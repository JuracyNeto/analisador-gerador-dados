"""Blocos e trechos de linhas seguidas (R1, R2, R3, R11; D122).

Janelas de k valores seguidos saem de somas acumuladas de x e x² (O(n) para todas as janelas),
o que deixa a simulação da R1 — a melhor janela de cada embaralhamento da coluna — vetorizada.
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


def _janelas_centradas(centrados: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Σ(x − c) e DP amostral de cada janela de k colunas seguidas, em cada linha."""
    acumulada = _acumulada(centrados)
    quadrados = _acumulada(centrados * centrados)
    soma = acumulada[:, k:] - acumulada[:, :-k]
    variancias = (quadrados[:, k:] - quadrados[:, :-k] - soma * soma / k) / (k - 1)
    return soma, np.sqrt(np.clip(variancias, 0, None))


def janelas(valores: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Média e DP amostral de cada janela de k valores seguidos (n − k + 1 janelas)."""
    numeros = np.asarray(valores, dtype="float64")
    centro = float(numeros.mean())
    # Centrar na média geral evita perder precisão nas somas dos quadrados.
    soma, desvios = _janelas_centradas((numeros - centro)[np.newaxis, :], k)
    return soma[0] / k + centro, desvios[0]


def afastamento(medias: np.ndarray, desvios: np.ndarray, media: float, desvio: float) -> np.ndarray:
    """max(dᵤ, dₛ): dᵤ = |x̄_bloco − x̄| / s e dₛ = |s_bloco − s| / s."""
    return np.asarray(
        np.maximum(np.abs(medias - media), np.abs(desvios - desvio)) / desvio, dtype="float64"
    )


def menor_afastamento(matriz: np.ndarray, k: int, media: float, desvio: float) -> np.ndarray:
    """Para cada linha da matriz, o afastamento da janela mais parecida com o conjunto."""
    soma, desvios = _janelas_centradas(np.asarray(matriz, dtype="float64") - media, k)
    maiores = np.maximum(np.abs(soma) / k, np.abs(desvios - desvio))
    return np.asarray(maiores.min(axis=1) / desvio, dtype="float64")


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
