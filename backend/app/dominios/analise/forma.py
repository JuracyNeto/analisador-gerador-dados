"""Assimetria (Fisher e Pearson) e curtose (excesso e percentílica) (spec 09)."""

import math

import numpy as np
from scipy import stats

from app.compartilhado.numeros import formatar_numero
from app.dominios.analise import textos_forma
from app.dominios.analise.resultados import (
    ClasseAssimetria,
    ClasseCurtose,
    Medida,
    Sentido,
    Separatrizes,
    nao_aplicavel,
)

MIN_ASSIMETRIA = 3
MIN_CURTOSE = 4
LIMIAR_SIMETRIA = 0.5
LIMIAR_FORTE = 1.0
LIMIAR_CURTOSE = 0.5
INDICE_Q1, INDICE_Q3 = 0, 2
INDICE_P10, INDICE_P90 = 0, 8


def _f(valor: float) -> str:
    return formatar_numero(valor)


def _motivo_borda(item: str, valores: np.ndarray, minimo: int) -> str | None:
    """Casos de borda (spec 09): poucos valores ou nenhuma variação."""
    if len(valores) < minimo:
        return textos_forma.nao_calculavel(item, f"poucos_{minimo}")
    if float(np.ptp(valores)) == 0:
        return textos_forma.nao_calculavel(item, "sem_variacao")
    return None


def classificar_assimetria(g1: float) -> tuple[ClasseAssimetria, Sentido | None]:
    """|G₁| < 0,5 simétrica · 0,5–1 moderada · > 1 forte; o sinal diz o lado da cauda."""
    sentido: Sentido | None = "direita" if g1 > 0 else "esquerda" if g1 < 0 else None
    if abs(g1) < LIMIAR_SIMETRIA:
        return "simetrica", sentido
    return ("moderada" if abs(g1) <= LIMIAR_FORTE else "forte"), sentido


def classificar_curtose(g2: float) -> ClasseCurtose:
    """|G₂| ≤ 0,5 mesocúrtica · G₂ > 0,5 leptocúrtica · G₂ < −0,5 platicúrtica."""
    if g2 > LIMIAR_CURTOSE:
        return "leptocurtica"
    return "platicurtica" if g2 < -LIMIAR_CURTOSE else "mesocurtica"


def _momento(valores: np.ndarray, k: int) -> float:
    return float(np.mean((valores - valores.mean()) ** k))


def assimetria(valores: np.ndarray) -> Medida:
    """G₁ = [√(n(n−1)) / (n−2)] · m₃ / m₂^(3/2) (`scipy.stats.skew(bias=False)`)."""
    motivo = _motivo_borda("assimetria", valores, MIN_ASSIMETRIA)
    if motivo:
        return nao_aplicavel(motivo)
    n = len(valores)
    g1 = float(stats.skew(valores, bias=False))
    m2, m3 = _momento(valores, 2), _momento(valores, 3)
    calculo = f"G₁ = [√({n}·{n - 1}) / {n - 2}] · {_f(m3)} / {_f(m2)}^(3/2) = {_f(g1)}"
    return Medida(
        g1,
        calculo=calculo,
        interpretacao=textos_forma.frase_assimetria(*classificar_assimetria(g1)),
        formula="assimetria",
    )


def curtose(valores: np.ndarray) -> Medida:
    """Excesso de curtose amostral G₂ (`scipy.stats.kurtosis(fisher=True, bias=False)`)."""
    motivo = _motivo_borda("curtose", valores, MIN_CURTOSE)
    if motivo:
        return nao_aplicavel(motivo)
    g2 = float(stats.kurtosis(valores, fisher=True, bias=False))
    return Medida(
        g2,
        calculo=f"G₂ = {_f(g2)} (na Normal, G₂ = 0; n = {len(valores)})",
        interpretacao=textos_forma.frase_curtose(classificar_curtose(g2)),
        formula="curtose",
    )


def _pearson_1(media: float, moda: float | None, desvio: float) -> Medida:
    if moda is None:
        return nao_aplicavel(textos_forma.nao_calculavel("assimetria_pearson_1", "moda_multipla"))
    valor = (media - moda) / desvio
    calculo = f"As₁ = ({_f(media)} − {_f(moda)}) / {_f(desvio)} = {_f(valor)}"
    return Medida(valor, calculo=calculo, formula="assimetria_pearson_1")


def pearson(valores: np.ndarray, moda: float | None, mediana: float) -> tuple[Medida, Medida]:
    """As₁ = (x̄ − Mo) / s e As₂ = 3(x̄ − Md) / s."""
    motivo = _motivo_borda("assimetria_pearson_1", valores, MIN_ASSIMETRIA)
    if motivo:
        segundo = _motivo_borda("assimetria_pearson_2", valores, MIN_ASSIMETRIA) or motivo
        return nao_aplicavel(motivo), nao_aplicavel(segundo)
    media, desvio = float(valores.mean()), float(valores.std(ddof=1))
    valor = 3 * (media - mediana) / desvio
    calculo = f"As₂ = 3 · ({_f(media)} − {_f(mediana)}) / {_f(desvio)} = {_f(valor)}"
    as2 = Medida(valor, calculo=calculo, formula="assimetria_pearson_2")
    return _pearson_1(media, moda, desvio), as2


def curtose_percentilica(separatrizes: Separatrizes) -> Medida:
    """K = (Q3 − Q1) / [2(P90 − P10)]; na Normal, K ≈ 0,263."""
    q1 = float(separatrizes.quartis[INDICE_Q1].valor)
    q3 = float(separatrizes.quartis[INDICE_Q3].valor)
    p10 = float(separatrizes.decis[INDICE_P10].valor)
    p90 = float(separatrizes.decis[INDICE_P90].valor)
    if math.isclose(p90, p10):
        motivo = textos_forma.nao_calculavel("curtose_percentilica", "percentis_iguais")
        return nao_aplicavel(motivo)
    valor = (q3 - q1) / (2 * (p90 - p10))
    calculo = f"K = ({_f(q3)} − {_f(q1)}) / [2 · ({_f(p90)} − {_f(p10)})] = {_f(valor)}"
    return Medida(valor, calculo=calculo, formula="curtose_percentilica")
