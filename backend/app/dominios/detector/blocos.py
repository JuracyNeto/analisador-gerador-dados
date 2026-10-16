"""Blocos e trechos de linhas seguidas (R1, R2, R3, R11; D122).

Janelas de k valores seguidos, o fim da coluna (de qualquer tamanho) e o restante de cada um saem
de somas acumuladas de x e x² (O(n) para todos), o que deixa a simulação da R1 — o melhor trecho
de cada embaralhamento da coluna — vetorizada.
"""

from collections.abc import Iterator
from itertools import pairwise

import numpy as np

LIMITE_ELEMENTOS = 250_000
"""Embaralhamentos por lote: até 250 mil valores na matriz (D142).

Matrizes menores cabem no cache do processador: com 1 milhão, a simulação ficava 2× mais lenta.
O tamanho do lote não muda o sorteio.
"""
PARTES = 5


def _acumulada(matriz: np.ndarray) -> np.ndarray:
    """Somas acumuladas por linha, com um zero na frente (soma da janela = diferença)."""
    acumulada = np.zeros((matriz.shape[0], matriz.shape[1] + 1))
    np.cumsum(matriz, axis=1, out=acumulada[:, 1:])
    return acumulada


def _variancias(somas: np.ndarray, quadrados: np.ndarray, tamanho: int | np.ndarray) -> np.ndarray:
    """Variância amostral (≥ 0) de `tamanho` valores a partir de Σ(x − c) e Σ(x − c)²."""
    variancias: np.ndarray = quadrados - somas * somas / tamanho
    variancias /= tamanho - 1
    np.maximum(variancias, 0, out=variancias)
    return variancias


def _somas(matriz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Somas acumuladas de x − x̄ e de (x − x̄)², com um zero na frente."""
    numeros = np.asarray(matriz, dtype="float64")
    # Centrar na média geral evita perder precisão nas somas dos quadrados.
    centrados = numeros - numeros.mean()
    acumulada = _acumulada(centrados)
    return acumulada, _acumulada(np.square(centrados, out=centrados))


def _afastamentos(
    somas: tuple[np.ndarray, np.ndarray],
    trecho: tuple[np.ndarray, np.ndarray],
    tamanho: int | np.ndarray,
) -> np.ndarray:
    """max(dᵤ, dₛ) de cada trecho (Σ e Σ² dele, com `tamanho` valores) contra o resto da linha."""
    acumulada, quadrados = somas
    soma, quadrado = trecho
    n = acumulada.shape[1] - 1
    tamanhos = np.asarray(tamanho, dtype="float64")
    resto = n - tamanhos
    soma_resto, quadrado_resto = acumulada[:, -1:] - soma, quadrados[:, -1:] - quadrado
    desvio_resto = np.sqrt(_variancias(soma_resto, quadrado_resto, resto))
    # Menos cópias de matrizes grandes: as contas seguintes reaproveitam `diferencas`.
    diferencas = np.abs(np.sqrt(_variancias(soma, quadrado, tamanhos)) - desvio_resto)
    np.maximum(diferencas, np.abs(soma / tamanhos - soma_resto / resto), out=diferencas)
    afastamentos = np.full(diferencas.shape, np.inf)
    np.divide(diferencas, desvio_resto, out=afastamentos, where=desvio_resto > 0)
    return afastamentos


def afastamentos_do_resto(matriz: np.ndarray, k: int) -> np.ndarray:
    """max(dᵤ, dₛ) de cada janela de k colunas seguidas contra o restante da linha.

    dᵤ = |x̄_janela − x̄_resto| / s_resto e dₛ = |s_janela − s_resto| / s_resto. O resto sai do
    total menos a janela. Com o resto constante (s_resto = 0), a janela fica infinitamente longe.
    """
    acumulada, quadrados = somas = _somas(matriz)
    janela = acumulada[:, k:] - acumulada[:, :-k], quadrados[:, k:] - quadrados[:, :-k]
    return _afastamentos(somas, janela, k)


def afastamentos_do_fim(matriz: np.ndarray, menor: int, maior: int) -> np.ndarray:
    """max(dᵤ, dₛ) dos últimos `menor` a `maior` valores de cada linha contra o resto (D148).

    É onde ficam os dados anexados (Gerador › "Anexar ao dataset atual"), de qualquer tamanho.
    """
    acumulada, quadrados = somas = _somas(matriz)
    tamanhos = np.arange(menor, maior + 1)
    inicios = acumulada.shape[1] - 1 - tamanhos
    fim = acumulada[:, -1:] - acumulada[:, inicios], quadrados[:, -1:] - quadrados[:, inicios]
    return _afastamentos(somas, fim, tamanhos)


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
