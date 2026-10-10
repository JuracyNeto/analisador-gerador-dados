"""Resumo numérico de um vetor (D108): as mesmas fórmulas da análise para outros domínios."""

import numpy as np

from app.dominios.analise.forma import assimetria, curtose
from app.dominios.analise.resultados import Medida, ResumoNumerico


def _valor(medida: Medida) -> float | None:
    return float(medida.valor) if medida.aplicavel and isinstance(medida.valor, float) else None


def resumo_numerico(valores: np.ndarray) -> ResumoNumerico:
    """n, média, mediana, DP amostral (n − 1), mín, máx, G₁ e G₂ (None onde não se aplica)."""
    numeros = np.asarray(valores, dtype="float64")
    desvio = float(np.std(numeros, ddof=1)) if len(numeros) > 1 else 0.0
    return ResumoNumerico(
        n=len(numeros),
        media=float(np.mean(numeros)),
        mediana=float(np.median(numeros)),
        desvio_padrao=desvio,
        minimo=float(np.min(numeros)),
        maximo=float(np.max(numeros)),
        assimetria=_valor(assimetria(numeros)),
        curtose=_valor(curtose(numeros)),
    )
