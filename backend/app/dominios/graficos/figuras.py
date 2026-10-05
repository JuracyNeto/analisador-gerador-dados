"""Figuras no formato JSON do Plotly ({"data": [...], "layout": {...}}) a partir de dados agregados.

Montadas como dicionários: o pacote `plotly` não tem tipos para o `mypy --strict` (ver
decisions.md). Os testes validam cada figura com `plotly.graph_objects`. Sem template: o tema é
aplicado depois (frontend ou relatório).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.compartilhado.numeros import formatar_percentual
from app.dominios.graficos.entradas import Barra, ResumoCaixa
from app.dominios.graficos.tema import COR_PRINCIPAL, COR_REFERENCIA

type Figura = dict[str, Any]

FATOR_IQR = 1.5
MAX_ROTULOS = 12
MAX_DISCREPANTES = 500
OPACIDADE_BARRA = 0.85
LARGURA_BASTAO = 0.08
LARGURA_LINHA = 2.5
QUARTIS = (0.25, 0.5, 0.75)
EIXO_FREQUENCIA = "Frequência (fᵢ)"
EIXO_ACUMULADA = "Frequência acumulada (%)"
MARCADOR_BARRA = {"color": COR_PRINCIPAL, "opacity": OPACIDADE_BARRA}


def _figura(tracos: list[dict[str, Any]], eixo_x: str, eixo_y: str) -> Figura:
    layout = {
        "xaxis": {"title": {"text": eixo_x}},
        "yaxis": {"title": {"text": eixo_y}},
        "showlegend": False,
        "separators": ",.",
    }
    return {"data": tracos, "layout": layout}


def _com_rotulos(traco: dict[str, Any], barras: tuple[Barra, ...]) -> dict[str, Any]:
    """Rótulo "fᵢ (fr%)" na ponta das barras, só com até 12 barras (spec 08)."""
    if len(barras) > MAX_ROTULOS:
        return traco
    rotulos = [f"{b.frequencia} ({formatar_percentual(b.percentual)})" for b in barras]
    return traco | {"text": rotulos, "textposition": "outside"}


def barras_horizontais(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Nominal: a maior categoria no topo."""
    invertidas = barras[::-1]
    traco = {
        "type": "bar",
        "orientation": "h",
        "x": [b.frequencia for b in invertidas],
        "y": [b.rotulo for b in invertidas],
        "marker": MARCADOR_BARRA,
    }
    return _figura([_com_rotulos(traco, invertidas)], EIXO_FREQUENCIA, coluna)


def barras_verticais(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Ordinal (na ordem da escala) e binária (com o percentual no rótulo)."""
    traco = {
        "type": "bar",
        "x": [b.rotulo for b in barras],
        "y": [b.frequencia for b in barras],
        "marker": MARCADOR_BARRA,
    }
    return _figura([_com_rotulos(traco, barras)], coluna, EIXO_FREQUENCIA)


def bastoes(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Discreta: uma haste fina por valor, com um ponto no topo."""
    x = [b.valor for b in barras]
    y = [b.frequencia for b in barras]
    hastes = {
        "type": "bar",
        "x": x,
        "y": y,
        "width": LARGURA_BASTAO,
        "marker": {"color": COR_PRINCIPAL},
    }
    pontos = {
        "type": "scatter",
        "mode": "markers",
        "x": x,
        "y": y,
        "marker": {"color": COR_PRINCIPAL, "size": 9},
    }
    return _figura([hastes, pontos], coluna, EIXO_FREQUENCIA)


def histograma(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Contínua: as classes da spec 04 como barras encostadas (largura = h)."""
    inferiores = [b.inferior or 0.0 for b in barras]
    larguras = [(b.superior or 0.0) - (b.inferior or 0.0) for b in barras]
    traco = {
        "type": "bar",
        "x": [i + w / 2 for i, w in zip(inferiores, larguras, strict=True)],
        "y": [b.frequencia for b in barras],
        "width": larguras,
        "customdata": [b.rotulo for b in barras],
        "hovertemplate": "%{customdata}: %{y}<extra></extra>",
        "marker": MARCADOR_BARRA,
    }
    figura = _figura([traco], coluna, EIXO_FREQUENCIA)
    figura["layout"]["bargap"] = 0
    return figura


def resumo_caixa(valores: pd.Series) -> ResumoCaixa:
    """Quartis por interpolação linear, bigodes até 1,5·IQR e os valores além deles."""
    numeros = valores.dropna().to_numpy(dtype="float64")
    q1, mediana, q3 = (float(q) for q in np.quantile(numeros, QUARTIS, method="linear"))
    inferior, superior = q1 - FATOR_IQR * (q3 - q1), q3 + FATOR_IQR * (q3 - q1)
    dentro = numeros[(numeros >= inferior) & (numeros <= superior)]
    fora = np.sort(numeros[(numeros < inferior) | (numeros > superior)])
    return ResumoCaixa(
        minimo=float(numeros.min()),
        q1=q1,
        mediana=mediana,
        q3=q3,
        maximo=float(numeros.max()),
        media=float(numeros.mean()),
        bigode_inferior=float(dentro.min()),
        bigode_superior=float(dentro.max()),
        discrepantes=tuple(float(v) for v in fora[:MAX_DISCREPANTES]),
    )


def boxplot(caixa: ResumoCaixa, coluna: str) -> Figura:
    """Boxplot horizontal com estatísticas prontas e média; discrepantes como pontos à parte."""
    caixa_traco = {
        "type": "box",
        "orientation": "h",
        "y": [coluna],
        "q1": [caixa.q1],
        "median": [caixa.mediana],
        "q3": [caixa.q3],
        "lowerfence": [caixa.bigode_inferior],
        "upperfence": [caixa.bigode_superior],
        "mean": [caixa.media],
        "boxmean": True,
        "marker": {"color": COR_PRINCIPAL},
        "line": {"color": COR_PRINCIPAL},
    }
    pontos = {
        "type": "scatter",
        "mode": "markers",
        "x": list(caixa.discrepantes),
        "y": [coluna] * len(caixa.discrepantes),
        "marker": {"color": COR_REFERENCIA, "size": 7},
    }
    return _figura([caixa_traco, pontos], coluna, "")


def _linha(x: list[float | None], y: list[float | None], forma: str = "linear") -> dict[str, Any]:
    linha = {"color": COR_PRINCIPAL, "width": LARGURA_LINHA, "shape": forma}
    return {"type": "scatter", "mode": "lines+markers", "x": x, "y": y, "line": linha}


def ogiva(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Fr% acumulada nos limites superiores das classes, partindo de 0."""
    x = [barras[0].inferior, *(b.superior for b in barras)]
    y: list[float | None] = [0.0, *(b.acumulado_pct for b in barras)]
    return _figura([_linha(x, y)], coluna, EIXO_ACUMULADA)


def acumulada_categorias(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Ordinal: barras da frequência acumulada na ordem da escala."""
    traco = {
        "type": "bar",
        "x": [b.rotulo for b in barras],
        "y": [b.acumulado_pct for b in barras],
        "marker": MARCADOR_BARRA,
    }
    return _figura([traco], coluna, EIXO_ACUMULADA)


def acumulada_escada(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Discreta: frequência acumulada em escada."""
    traco = _linha([b.valor for b in barras], [b.acumulado_pct for b in barras], forma="hv")
    return _figura([traco], coluna, EIXO_ACUMULADA)


def pizza(barras: tuple[Barra, ...]) -> Figura:
    """Só para até 5 categorias (spec 08)."""
    traco = {
        "type": "pie",
        "labels": [b.rotulo for b in barras],
        "values": [b.frequencia for b in barras],
        "sort": False,
        "textinfo": "label+percent",
    }
    return {"data": [traco], "layout": {"showlegend": False, "separators": ",."}}
