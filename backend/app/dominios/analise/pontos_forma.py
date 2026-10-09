"""Pontos que alimentam as figuras da forma: curva Normal, QQ-plot e observado × Binomial."""

from dataclasses import dataclass

import numpy as np
from scipy import stats

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise.resultados import Ajuste, Analise

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


@dataclass(frozen=True, slots=True)
class PontosForma:
    curva: Curva | None = None
    qq: PontosQQ | None = None
    binomial: ComparacaoBinomial | None = None


def _escala(analise: Analise) -> float:
    """Contínua: N · h (área das barras do histograma); discreta: N (um valor por haste)."""
    h = analise.frequencias.h
    return analise.n * h if analise.tipo == TipoVariavel.CONTINUA and h else float(analise.n)


def _curva(valores: np.ndarray, analise: Analise, normal: Ajuste) -> Curva | None:
    if not normal.aplicavel:
        return None
    media, desvio = (p.valor for p in normal.parametros)
    inicio, fim = faixa_da_curva(valores, media, desvio)
    return curva_normal(media, desvio, inicio, fim, _escala(analise))


def _binomial(valores: np.ndarray, binomial: Ajuste) -> ComparacaoBinomial | None:
    if not binomial.aplicavel or binomial.distribuicao != "binomial":
        return None
    parametros = {p.simbolo: p.valor for p in binomial.parametros}
    return comparacao_binomial(valores, int(parametros["n"]), parametros["p̂"])


def pontos_da_forma(valores: np.ndarray, analise: Analise) -> PontosForma:
    """Curva (contínua e discreta com Normal), QQ-plot (contínua) e Binomial (discreta)."""
    forma = analise.forma
    if forma is None or analise.tipo not in TIPOS_NUMERICOS:
        return PontosForma()
    continua = analise.tipo == TipoVariavel.CONTINUA and forma.normal.aplicavel
    return PontosForma(
        curva=_curva(valores, analise, forma.normal),
        qq=pontos_qq(valores) if continua else None,
        binomial=_binomial(valores, forma.binomial),
    )
