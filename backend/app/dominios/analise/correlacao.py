"""Correlação de Pearson (com teste t), Spearman, força e sentido, e a matriz (spec 10)."""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from app.compartilhado.numeros import formatar_numero, formatar_p_valor
from app.dominios.analise import textos_bivariada
from app.dominios.analise.resultados import Medida
from app.dominios.analise.resultados_bivariada import Forca, MatrizCorrelacao, Sentido

LIMIAR_MODERADA = 0.3
LIMIAR_FORTE = 0.7
MIN_PARES_MATRIZ = 3
INTERPRETACAO_SPEARMAN = (
    "Correlação pelos postos: útil quando há valores extremos ou a relação não é uma reta."
)


def _f(valor: float) -> str:
    return formatar_numero(valor)


@dataclass(frozen=True, slots=True)
class Somas:
    """Sxx = Σ(xᵢ − x̄)², Syy = Σ(yᵢ − ȳ)², Sxy = Σ(xᵢ − x̄)(yᵢ − ȳ)."""

    media_x: float
    media_y: float
    sxx: float
    syy: float
    sxy: float


def somas(x: np.ndarray, y: np.ndarray) -> Somas:
    dx, dy = x - x.mean(), y - y.mean()
    return Somas(
        media_x=float(x.mean()),
        media_y=float(y.mean()),
        sxx=float(np.sum(dx**2)),
        syy=float(np.sum(dy**2)),
        sxy=float(np.sum(dx * dy)),
    )


def pearson(x: np.ndarray, y: np.ndarray) -> Medida:
    """r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[Σ(xᵢ − x̄)² · Σ(yᵢ − ȳ)²]."""
    s = somas(x, y)
    r = s.sxy / math.sqrt(s.sxx * s.syy)
    r = max(-1.0, min(1.0, r))  # arredondamento de ponto flutuante não passa de ±1
    calculo = f"r = Sxy / √(Sxx · Syy) = {_f(s.sxy)} / √({_f(s.sxx)} · {_f(s.syy)}) = {_f(r)}"
    return Medida(r, calculo=calculo, formula="pearson")


def teste_t(r: float, n: int) -> Medida:
    """t = r√(n − 2) / √(1 − r²), gl = n − 2, p bilateral; |r| = 1 → p = 0."""
    gl = n - 2
    if math.isclose(abs(r), 1.0):
        estatistica, p = math.inf, 0.0
    else:
        estatistica = r * math.sqrt(gl) / math.sqrt(1 - r**2)
        p = float(2 * stats.t.sf(abs(estatistica), gl))
    texto_t = "∞" if math.isinf(estatistica) else _f(estatistica)
    return Medida(
        p,
        calculo=f"t = {texto_t} · gl = {gl} · {formatar_p_valor(p)}",
        interpretacao=textos_bivariada.frase_significancia(p),
        formula="teste_t_correlacao",
    )


def spearman(x: np.ndarray, y: np.ndarray) -> Medida:
    """ρ = correlação de Pearson entre os postos de X e de Y."""
    rho = float(stats.spearmanr(x, y).statistic)
    return Medida(
        rho,
        calculo=f"ρ = {_f(rho)}",
        interpretacao=INTERPRETACAO_SPEARMAN,
        formula="spearman",
    )


def classificar(r: float) -> tuple[Forca, Sentido]:
    """|r| < 0,3 fraca · 0,3–0,7 moderada · ≥ 0,7 forte; o sinal dá o sentido."""
    sentido: Sentido = "positiva" if r > 0 else "negativa" if r < 0 else "nula"
    if abs(r) < LIMIAR_MODERADA:
        return "fraca", sentido
    return ("moderada" if abs(r) < LIMIAR_FORTE else "forte"), sentido


def _celula(valor: float) -> float | None:
    return None if math.isnan(valor) else float(valor)


def matriz_correlacao(tabela: pd.DataFrame) -> MatrizCorrelacao:
    """Pearson par a par, só com as linhas em que as duas colunas têm valor."""
    corr = tabela.corr(method="pearson", min_periods=MIN_PARES_MATRIZ)
    colunas = tuple(str(c) for c in corr.columns)
    valores = tuple(tuple(_celula(float(v)) for v in linha) for linha in corr.to_numpy())
    return MatrizCorrelacao(
        colunas=colunas,
        valores=valores,
        resumo=textos_bivariada.resumo_matriz(colunas, valores),
    )
