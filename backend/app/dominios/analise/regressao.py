"""Regressão linear simples Ŷ = a + bX, resíduos e previsão (spec 10)."""

import math

import numpy as np

from app.compartilhado.numeros import formatar_numero
from app.dominios.analise import textos_bivariada as textos
from app.dominios.analise.correlacao import somas
from app.dominios.analise.resultados import Medida
from app.dominios.analise.resultados_bivariada import Faixa, Previsao, Regressao

PERCENTUAL = 100


def _f(valor: float) -> str:
    return textos.numero(valor)


def residuos(x: np.ndarray, y: np.ndarray, a: float, b: float) -> np.ndarray:
    """eᵢ = yᵢ − ŷᵢ, com ŷᵢ = a + b·xᵢ."""
    return y - (a + b * x)


def regressao(x: np.ndarray, y: np.ndarray, nomes: tuple[str, str]) -> Regressao:
    """b = Sxy / Sxx · a = ȳ − b·x̄ · R² = r² · Sₑ = √[Σeᵢ² / (n − 2)]."""
    nome_x, nome_y = nomes
    s = somas(x, y)
    b = s.sxy / s.sxx
    a = s.media_y - b * s.media_x
    r2 = s.sxy**2 / (s.sxx * s.syy)
    soma_quadrados = float(np.sum(residuos(x, y, a, b) ** 2))
    gl = len(x) - 2
    se = math.sqrt(soma_quadrados / gl)
    equacao = textos.formatar_equacao(a, b)
    calculo_reta = (
        f"b = Sxy / Sxx = {_f(s.sxy)} / {_f(s.sxx)} = {_f(b)} · "
        f"a = ȳ − b·x̄ = {_f(s.media_y)} − {_f(b)} · {_f(s.media_x)} = {_f(a)}"
    )
    return Regressao(
        a=a,
        b=b,
        equacao=equacao,
        reta=Medida(
            equacao,
            calculo=calculo_reta,
            interpretacao=textos.frase_reta(b, nome_x, nome_y),
            formula="regressao",
        ),
        r2=Medida(
            r2 * PERCENTUAL,
            calculo=f"R² = r² = {formatar_numero(r2)}",
            interpretacao=textos.frase_r2(r2 * PERCENTUAL, nome_x, nome_y),
            formula="r2",
        ),
        se=Medida(
            se,
            calculo=f"Sₑ = √({_f(soma_quadrados)} / {gl}) = {_f(se)}",
            interpretacao=textos.frase_se(se, nome_y),
            formula="erro_padrao_estimativa",
        ),
    )


def prever(a: float, b: float, valor: float, faixa: Faixa, nomes: tuple[str, str]) -> Previsao:
    """ŷ = a + b·x; fora de [mín X, máx X] avisa que é extrapolação."""
    nome_x, nome_y = nomes
    previsto = a + b * valor
    fora = valor < faixa.minimo or valor > faixa.maximo
    return Previsao(
        x=valor,
        y_previsto=previsto,
        extrapolacao=fora,
        faixa_x=faixa,
        frase=textos.frase_previsao(nome_x, valor, nome_y, previsto),
        aviso=textos.aviso_extrapolacao(nome_x, faixa) if fora else None,
    )
