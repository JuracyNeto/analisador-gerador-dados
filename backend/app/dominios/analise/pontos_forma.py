"""Pontos que alimentam as figuras da forma: curva Normal, QQ-plot e observado × Binomial."""

from dataclasses import dataclass

import numpy as np
from scipy import stats

PONTOS_CURVA = 200
MAX_PONTOS_QQ = 500  # D98: o QQ-plot nunca envia mais que isso (ADR 0003)
DESVIOS_NA_CURVA = 4.0


@dataclass(frozen=True, slots=True)
class Curva:
    x: tuple[float, ...]
    y: tuple[float, ...]
    media: float
    desvio: float


@dataclass(frozen=True, slots=True)
class PontosQQ:
    """Quantis da Normal padrão × quantis da amostra; a reta de referência é y = μ + σ·z."""

    teoricos: tuple[float, ...]
    observados: tuple[float, ...]
    media: float
    desvio: float


@dataclass(frozen=True, slots=True)
class ComparacaoBinomial:
    k: tuple[int, ...]
    observados: tuple[int, ...]
    esperados: tuple[float, ...]
    n: int
    p: float


def _tupla(valores: np.ndarray) -> tuple[float, ...]:
    return tuple(float(v) for v in valores)


def curva_normal(media: float, desvio: float, inicio: float, fim: float, escala: float) -> Curva:
    """Densidade Normal × escala (N·h no histograma, N nos bastões), em 200 pontos."""
    x = np.linspace(inicio, fim, PONTOS_CURVA)
    y = stats.norm.pdf(x, loc=media, scale=desvio) * escala
    return Curva(_tupla(x), _tupla(y), media, desvio)


def faixa_da_curva(valores: np.ndarray, media: float, desvio: float) -> tuple[float, float]:
    """Da menor ponta à maior: dados ou μ ± 4σ, o que for mais largo."""
    inicio = min(float(valores.min()), media - DESVIOS_NA_CURVA * desvio)
    fim = max(float(valores.max()), media + DESVIOS_NA_CURVA * desvio)
    return inicio, fim


def pontos_qq(valores: np.ndarray) -> PontosQQ:
    """Posições (i − 0,5)/m; acima de 500 valores, quantis igualmente espaçados."""
    m = min(len(valores), MAX_PONTOS_QQ)
    probabilidades = (np.arange(1, m + 1) - 0.5) / m
    if len(valores) > MAX_PONTOS_QQ:
        observados = np.quantile(valores, probabilidades, method="linear")
    else:
        observados = np.sort(valores)
    return PontosQQ(
        teoricos=_tupla(stats.norm.ppf(probabilidades)),
        observados=_tupla(observados),
        media=float(valores.mean()),
        desvio=float(valores.std(ddof=1)),
    )


def comparacao_binomial(valores: np.ndarray, n: int, p: float) -> ComparacaoBinomial:
    """Frequência observada e esperada (N · P(X = k)) para k = 0..n, sem agrupar."""
    k = np.arange(n + 1)
    observados = np.bincount(np.round(valores).astype(int), minlength=n + 1)
    esperados = len(valores) * stats.binom.pmf(k, n, p)
    return ComparacaoBinomial(
        k=tuple(int(v) for v in k),
        observados=tuple(int(v) for v in observados),
        esperados=_tupla(esperados),
        n=n,
        p=p,
    )
