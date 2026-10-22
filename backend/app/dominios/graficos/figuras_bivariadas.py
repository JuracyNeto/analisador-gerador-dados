"""Figuras da bivariada (spec 10): dispersão com reta, resíduos × X e heatmap da matriz.

Mesmo formato de `figuras.py` (dicionários do Plotly, sem template, D77). Mais de 5.000 pontos
viram uma amostra fixa (D101), para o JSON ficar pequeno (ADR 0003).
"""

from typing import Any

import numpy as np

from app.compartilhado.numeros import formatar_numero
from app.dominios.graficos.entradas import DadosBivariados, DadosMatriz
from app.dominios.graficos.figuras import LARGURA_LINHA, Figura, figura_basica
from app.dominios.graficos.tema import PAPEL_DIVERGENTE, PAPEL_PRINCIPAL, PAPEL_REFERENCIA

MAX_PONTOS = 5000
SEMENTE_AMOSTRA = 20261008
TAMANHO_PONTOS = 6
OPACIDADE_PONTOS = 0.7
OPACIDADE_HEATMAP = 0.6  # graficos-plotly.md: intensidade máxima de 60%
CASAS_MATRIZ = 2
EIXO_RESIDUO = "Resíduo (Y − Ŷ)"


def amostrar(x: tuple[float, ...], y: tuple[float, ...]) -> tuple[list[float], list[float]]:
    """Até 5.000 pares; acima disso, uma amostra sempre igual (semente fixa), na ordem original."""
    if len(x) <= MAX_PONTOS:
        return list(x), list(y)
    indices = np.sort(
        np.random.default_rng(SEMENTE_AMOSTRA).choice(len(x), MAX_PONTOS, replace=False)
    )
    return [x[i] for i in indices], [y[i] for i in indices]


def _pontos(x: list[float], y: list[float], nome: str) -> dict[str, Any]:
    return {
        "type": "scatter",
        "mode": "markers",
        "x": x,
        "y": y,
        "marker": {"size": TAMANHO_PONTOS, "opacity": OPACIDADE_PONTOS},
        "name": nome,
        "meta": PAPEL_PRINCIPAL,
    }


def _linha(x: list[float], y: list[float], nome: str) -> dict[str, Any]:
    return {
        "type": "scatter",
        "mode": "lines",
        "x": x,
        "y": y,
        "line": {"width": LARGURA_LINHA},
        "name": nome,
        "meta": PAPEL_REFERENCIA,
    }


def _tracejada(traco: dict[str, Any]) -> dict[str, Any]:
    return traco | {"line": {**traco["line"], "dash": "dash"}}


def _com_legenda(figura: Figura) -> Figura:
    figura["layout"]["showlegend"] = True
    return figura


def _extremos(dados: DadosBivariados) -> list[float]:
    return [min(dados.x), max(dados.x)]


def dispersao(dados: DadosBivariados) -> Figura:
    """Pontos (X, Y) e a reta de regressão de ponta a ponta da faixa de X."""
    x, y = amostrar(dados.x, dados.y)
    extremos = _extremos(dados)
    reta = [dados.a + dados.b * valor for valor in extremos]
    tracos = [
        _pontos(x, y, f"Pontos (n = {formatar_numero(len(dados.x))})"),
        _linha(extremos, reta, dados.equacao),
    ]
    return _com_legenda(figura_basica(tracos, f"{dados.x_nome} (X)", f"{dados.y_nome} (Y)"))


def residuos(dados: DadosBivariados) -> Figura:
    """eᵢ = yᵢ − ŷᵢ contra X (specs 08 e 10, D102), com a linha do zero tracejada."""
    x, y = amostrar(dados.x, dados.y)
    erros = [yi - (dados.a + dados.b * xi) for xi, yi in zip(x, y, strict=True)]
    tracos = [
        _pontos(x, erros, "Resíduos"),
        _tracejada(_linha(_extremos(dados), [0, 0], "Resíduo zero")),
    ]
    return _com_legenda(figura_basica(tracos, f"{dados.x_nome} (X)", EIXO_RESIDUO))


def _texto_celula(valor: float | None) -> str:
    return "" if valor is None else formatar_numero(round(valor, CASAS_MATRIZ))


def heatmap(dados: DadosMatriz) -> Figura:
    """Matriz de Pearson com escala divergente (papel `divergente`, D103) e valores anotados."""
    traco = {
        "type": "heatmap",
        "z": [list(linha) for linha in dados.valores],
        "x": list(dados.colunas),
        "y": list(dados.colunas),
        "zmin": -1,
        "zmax": 1,
        "opacity": OPACIDADE_HEATMAP,
        "text": [[_texto_celula(v) for v in linha] for linha in dados.valores],
        "texttemplate": "%{text}",
        "hovertemplate": "%{y} × %{x}: %{text}<extra></extra>",
        "colorbar": {"tickvals": [-1, 0, 1], "ticktext": ["−1", "0", "1"]},
        "meta": PAPEL_DIVERGENTE,
    }
    figura = figura_basica([traco], "", "")
    figura["layout"]["yaxis"]["autorange"] = "reversed"
    return figura
