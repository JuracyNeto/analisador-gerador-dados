"""Medidas de dispersão: amplitude, variância, desvio padrão, IQR e CV (spec 07)."""

import math
from typing import Literal

import numpy as np

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.frequencias import ordem_completa
from app.dominios.analise.resultados import (
    Amostra,
    Dispersao,
    Medida,
    Separatrizes,
    nao_aplicavel,
)

MIN_VALORES_VARIANCIA = 2

type ClassificacaoCV = Literal["baixa", "media", "alta"]

LIMIARES_CV: tuple[tuple[float, ClassificacaoCV], ...] = ((15.0, "baixa"), (30.0, "media"))
FRASES_CV: dict[ClassificacaoCV, str] = {
    "baixa": "Os dados são homogêneos (pouca variação em relação à média).",
    "media": "Variação moderada em relação à média.",
    "alta": "Os dados são heterogêneos (muita variação em relação à média).",
}
CV_NEGATIVOS = "CV pouco interpretável com valores negativos."
SEM_DISPERSAO = "Todos os valores são iguais; não há dispersão."
ITENS_NUMERICOS = (
    "amplitude",
    "variancia",
    "variancia_populacional",
    "desvio_padrao",
    "desvio_padrao_populacional",
    "iqr",
    "cv",
)


def _f(valor: float) -> str:
    return formatar_numero(valor)


def classificar_cv(cv: float) -> ClassificacaoCV:
    """< 15% baixa · 15–30% média · > 30% alta."""
    return next((classe for limite, classe in LIMIARES_CV if cv < limite), "alta")


def _montar(medidas: dict[str, Medida], classificacao: ClassificacaoCV | None = None) -> Dispersao:
    return Dispersao(
        amplitude=medidas["amplitude"],
        variancia=medidas["variancia"],
        variancia_populacional=medidas["variancia_populacional"],
        desvio_padrao=medidas["desvio_padrao"],
        desvio_padrao_populacional=medidas["desvio_padrao_populacional"],
        iqr=medidas["iqr"],
        cv=medidas["cv"],
        classificacao_cv=classificacao,
    )


def _sem_distancias(tipo: TipoVariavel) -> dict[str, Medida]:
    return {i: nao_aplicavel(textos.nao_se_aplica(i, tipo, "distancias")) for i in ITENS_NUMERICOS}


def _variancias(valores: np.ndarray) -> dict[str, Medida]:
    """s² = Σ(xᵢ − x̄)² / (n − 1) e σ² = Σ(xᵢ − μ)² / n, com os desvios padrão."""
    n = len(valores)
    quadrados = float(np.sum((valores - valores.mean()) ** 2))
    populacional = quadrados / n
    medidas = {
        "variancia_populacional": Medida(
            populacional,
            calculo=f"Σ(xᵢ − μ)² / n = {_f(quadrados)} / {n} = {_f(populacional)}",
            formula="variancia_populacional",
        ),
        "desvio_padrao_populacional": Medida(
            math.sqrt(populacional),
            calculo=f"√{_f(populacional)} = {_f(math.sqrt(populacional))}",
            formula="desvio_padrao",
        ),
    }
    if n < MIN_VALORES_VARIANCIA:
        motivo = textos.nao_calculavel
        medidas["variancia"] = nao_aplicavel(motivo("variancia", "poucos_valores"))
        medidas["desvio_padrao"] = nao_aplicavel(motivo("desvio_padrao", "poucos_valores"))
        return medidas
    amostral = quadrados / (n - 1)
    desvio = math.sqrt(amostral)
    medidas["variancia"] = Medida(
        amostral,
        calculo=f"Σ(xᵢ − x̄)² / (n − 1) = {_f(quadrados)} / {n - 1} = {_f(amostral)}",
        formula="variancia",
    )
    medidas["desvio_padrao"] = Medida(
        desvio,
        calculo=f"√{_f(amostral)} = {_f(desvio)}",
        interpretacao=SEM_DISPERSAO if desvio == 0 else None,
        formula="desvio_padrao",
    )
    return medidas


def _cv(valores: np.ndarray, desvio: Medida) -> Medida:
    """CV = (s / x̄) · 100%; com valores negativos usa |x̄| e avisa."""
    media = float(valores.mean())
    if not desvio.aplicavel or not isinstance(desvio.valor, float):
        return nao_aplicavel(textos.nao_calculavel("cv", "poucos_valores"))
    if media == 0:
        return nao_aplicavel(textos.CV_MEDIA_ZERO)
    cv = desvio.valor / abs(media) * 100
    frase = FRASES_CV[classificar_cv(cv)]
    if bool(np.any(valores < 0)):
        frase = f"{frase} {CV_NEGATIVOS}"
    calculo = f"(s / x̄) · 100% = ({_f(desvio.valor)} / {_f(abs(media))}) · 100% = {_f(cv)}%"
    return Medida(cv, calculo=calculo, interpretacao=frase, formula="cv")


def _iqr_numerico(separatrizes: Separatrizes) -> Medida:
    q1, q3 = float(separatrizes.quartis[0].valor), float(separatrizes.quartis[2].valor)
    calculo = f"Q3 − Q1 = {_f(q3)} − {_f(q1)} = {_f(q3 - q1)}"
    return Medida(q3 - q1, calculo=calculo, formula="iqr")


def _numerica(amostra: Amostra, separatrizes: Separatrizes) -> Dispersao:
    valores = amostra.valores.to_numpy(dtype="float64")
    minimo, maximo = float(valores.min()), float(valores.max())
    calculo = f"xₘₐₓ − xₘᵢₙ = {_f(maximo)} − {_f(minimo)} = {_f(maximo - minimo)}"
    medidas = _variancias(valores)
    cv = _cv(valores, medidas["desvio_padrao"])
    medidas |= {
        "amplitude": Medida(maximo - minimo, calculo=calculo, formula="amplitude"),
        "iqr": _iqr_numerico(separatrizes),
        "cv": cv,
    }
    return _montar(medidas, classificar_cv(cv.valor) if isinstance(cv.valor, float) else None)


def _binaria(amostra: Amostra, proporcao: Medida) -> Dispersao:
    p = float(proporcao.valor) if isinstance(proporcao.valor, float) else 0.0
    variancia = p * (1 - p)
    medidas = _sem_distancias(amostra.tipo) | {
        "variancia": Medida(
            variancia,
            calculo=f"p(1 − p) = {_f(p)} · {_f(1 - p)} = {_f(variancia)}",
            formula="variancia_binaria",
        ),
        "desvio_padrao": Medida(
            math.sqrt(variancia),
            calculo=f"√{_f(variancia)} = {_f(math.sqrt(variancia))}",
            formula="desvio_padrao",
        ),
    }
    return _montar(medidas)


def _ordinal(amostra: Amostra, separatrizes: Separatrizes) -> Dispersao:
    """Amplitude e IQR em categorias ("de baixo a muito alto")."""
    ordem = ordem_completa(amostra)
    q1, q3 = separatrizes.quartis[0].valor, separatrizes.quartis[2].valor
    medidas = _sem_distancias(amostra.tipo) | {
        "amplitude": Medida(f"de {ordem[0]} a {ordem[-1]}"),
        "iqr": Medida(f"de {q1} a {q3}", calculo=f"Q1 = {q1} · Q3 = {q3}"),
    }
    return _montar(medidas)


def dispersao(
    amostra: Amostra, separatrizes: Separatrizes | None, proporcao: Medida
) -> Dispersao | None:
    """Numéricas: todas; binária: p(1 − p); ordinal: em categorias; nominal: não se aplica."""
    if amostra.tipo == TipoVariavel.BINARIA:
        return _binaria(amostra, proporcao)
    if separatrizes is None:
        return None
    if amostra.tipo == TipoVariavel.ORDINAL:
        return _ordinal(amostra, separatrizes)
    return _numerica(amostra, separatrizes)
