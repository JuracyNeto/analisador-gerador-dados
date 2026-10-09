"""Figuras da forma (spec 09): histograma ou bastões com curva Normal, QQ-plot e Binomial.

Mesmo formato de `figuras.py` (dicionários do Plotly, sem template, D77); cada traço tem nome
porque estas figuras mostram legenda (prints 4e e 4j).
"""

from typing import Any

from app.compartilhado.numeros import formatar_numero
from app.dominios.graficos import figuras
from app.dominios.graficos.entradas import Barra, BinomialFigura, CurvaFigura, QQFigura
from app.dominios.graficos.figuras import EIXO_FREQUENCIA, LARGURA_LINHA, Figura
from app.dominios.graficos.tema import PAPEL_PRINCIPAL, PAPEL_REFERENCIA

OPACIDADE_PONTOS = 0.7
TAMANHO_PONTOS = 6
OPACIDADE_SOBREPOSTA = 0.55
EIXO_TEORICO = "Quantis teóricos (Normal)"
EIXO_OBSERVADO = "Quantis observados"


def _com_legenda(figura: Figura) -> Figura:
    figura["layout"]["showlegend"] = True
    return figura


def _nomear(traco: dict[str, Any], nome: str) -> dict[str, Any]:
    return traco | {"name": nome}


def _traco_curva(curva: CurvaFigura) -> dict[str, Any]:
    media, desvio = formatar_numero(curva.media), formatar_numero(curva.desvio)
    return {
        "type": "scatter",
        "mode": "lines",
        "x": list(curva.x),
        "y": list(curva.y),
        "line": {"width": LARGURA_LINHA},
        "name": f"Curva Normal (μ = {media}; σ = {desvio})",
        "meta": PAPEL_REFERENCIA,
    }


def histograma_normal(barras: tuple[Barra, ...], curva: CurvaFigura, coluna: str) -> Figura:
    """Histograma das classes da spec 04 com a curva Normal (μ̂, σ̂) por cima."""
    figura = figuras.histograma(barras, coluna)
    figura["data"] = [_nomear(figura["data"][0], "Frequência observada"), _traco_curva(curva)]
    return _com_legenda(figura)


def bastoes_normal(barras: tuple[Barra, ...], curva: CurvaFigura, coluna: str) -> Figura:
    """Bastões da discreta com a aproximação Normal por cima."""
    figura = figuras.bastoes(barras, coluna)
    hastes, pontos = figura["data"]
    figura["data"] = [
        _nomear(hastes, "Frequência observada") | {"showlegend": False},
        _nomear(pontos, "Frequência observada"),
        _traco_curva(curva),
    ]
    return _com_legenda(figura)


def qqplot(qq: QQFigura, coluna: str) -> Figura:
    """Pontos (z, quantil observado) e a reta y = μ + σ·z."""
    pontos = {
        "type": "scatter",
        "mode": "markers",
        "x": list(qq.teoricos),
        "y": list(qq.observados),
        "marker": {"size": TAMANHO_PONTOS, "opacity": OPACIDADE_PONTOS},
        "name": f"Valores de {coluna}",
        "meta": PAPEL_PRINCIPAL,
    }
    extremos = [qq.teoricos[0], qq.teoricos[-1]]
    reta = {
        "type": "scatter",
        "mode": "lines",
        "x": extremos,
        "y": [qq.media + qq.desvio * z for z in extremos],
        "line": {"width": LARGURA_LINHA},
        "name": "Referência Normal",
        "meta": PAPEL_REFERENCIA,
    }
    return _com_legenda(figuras.figura_basica([pontos, reta], EIXO_TEORICO, EIXO_OBSERVADO))


def observado_esperado(binomial: BinomialFigura, coluna: str) -> Figura:
    """Barras lado a lado: quantas vezes cada k apareceu × N · P(X = k)."""
    k = list(binomial.k)
    observado = {
        "type": "bar",
        "x": k,
        "y": list(binomial.observados),
        "marker": figuras.MARCADOR_BARRA,
        "name": "Observado",
        "meta": PAPEL_PRINCIPAL,
    }
    esperado = {
        "type": "bar",
        "x": k,
        "y": list(binomial.esperados),
        "marker": {"opacity": OPACIDADE_SOBREPOSTA},
        "name": "Esperado (Binomial)",
        "meta": PAPEL_REFERENCIA,
    }
    figura = figuras.figura_basica([observado, esperado], coluna, EIXO_FREQUENCIA)
    figura["layout"]["barmode"] = "group"
    return _com_legenda(figura)
