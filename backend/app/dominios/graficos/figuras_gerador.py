"""Figuras do gerador (spec 11): original × gerado sobrepostos e dispersão dos pares.

Só as alturas das barras vão para o JSON, nunca os valores (ADR 0003): a figura continua leve
com 1.000.000 de valores gerados (D113).
"""

import math
from typing import Any

import numpy as np
import pandas as pd

from app.compartilhado.numeros import formatar_inteiro
from app.dominios.graficos.entradas import DadosParesGerados, DadosSobreposicao
from app.dominios.graficos.figuras import Figura, figura_basica
from app.dominios.graficos.figuras_bivariadas import (
    OPACIDADE_PONTOS,
    TAMANHO_PONTOS,
    amostrar,
)
from app.dominios.graficos.tema import PAPEL_PRINCIPAL, PAPEL_REFERENCIA

OPACIDADE_SOBREPOSTA = 0.55  # graficos-plotly.md: barras sobrepostas
PERCENTUAL = 100
EIXO_RELATIVA = "Frequência relativa (%)"


def nome_serie(rotulo: str, n: int) -> str:
    return f"{rotulo} (n = {formatar_inteiro(n)})"


def classes_comuns(original: pd.Series | None, gerado: pd.Series) -> np.ndarray:
    """Mesmas classes para as duas séries: faixa da união e k de Sturges da menor série.

    Com o k da união (até 1.000.000 de valores), as classes ficariam finas demais para o
    original e as barras dele virariam ruído.
    """
    partes = [gerado.to_numpy(dtype="float64")]
    if original is not None:
        partes.append(original.to_numpy(dtype="float64"))
    menor = min(len(parte) for parte in partes)
    k = math.ceil(math.log2(menor)) + 1 if menor > 1 else 1
    return np.asarray(np.histogram_bin_edges(np.concatenate(partes), bins=k))


def percentuais_por_classe(valores: pd.Series, bordas: np.ndarray) -> np.ndarray:
    contagens, _ = np.histogram(valores.to_numpy(dtype="float64"), bordas)
    return np.asarray(contagens / len(valores) * PERCENTUAL, dtype="float64")


def percentuais_por_categoria(valores: pd.Series, categorias: list[str]) -> np.ndarray:
    frequencias = valores.astype(str).value_counts(normalize=True) * PERCENTUAL
    return np.array([float(frequencias.get(categoria, 0.0)) for categoria in categorias])


def categorias_comuns(original: pd.Series | None, gerado: pd.Series) -> list[str]:
    """Categorias na ordem do original; as que só saíram no gerado vão para o fim."""
    vistas = list(original.astype(str).value_counts().index) if original is not None else []
    novas = [c for c in gerado.astype(str).value_counts().index if c not in vistas]
    return [str(c) for c in vistas + novas]


def _barras(x: list[Any], y: np.ndarray, nome: str, papel: str) -> dict[str, Any]:
    return {
        "type": "bar",
        "x": x,
        "y": [float(v) for v in y],
        "name": nome,
        "meta": papel,
        "marker": {"opacity": OPACIDADE_SOBREPOSTA},
    }


def _series(
    dados: DadosSobreposicao, x: list[Any], originais: np.ndarray | None, gerados: np.ndarray
) -> list[dict[str, Any]]:
    tracos = []
    if originais is not None:
        tracos.append(
            _barras(x, originais, nome_serie("Original", dados.n_original), PAPEL_PRINCIPAL)
        )
    tracos.append(_barras(x, gerados, nome_serie("Gerado", len(dados.gerado)), PAPEL_REFERENCIA))
    return tracos


def _com_legenda(figura: Figura, barmode: str) -> Figura:
    figura["layout"] |= {"showlegend": True, "barmode": barmode}
    return figura


def sobreposicao_numerica(dados: DadosSobreposicao) -> Figura:
    """Histogramas de frequência relativa nas mesmas classes, um sobre o outro."""
    bordas = classes_comuns(dados.original, dados.gerado)
    centros = [float(c) for c in (bordas[:-1] + bordas[1:]) / 2]
    originais = (
        percentuais_por_classe(dados.original, bordas) if dados.original is not None else None
    )
    tracos = _series(dados, centros, originais, percentuais_por_classe(dados.gerado, bordas))
    for traco in tracos:
        traco["width"] = [float(w) for w in np.diff(bordas)]
    figura = figura_basica(tracos, dados.coluna, EIXO_RELATIVA)
    figura["layout"]["bargap"] = 0
    return _com_legenda(figura, "overlay")


def sobreposicao_categorica(dados: DadosSobreposicao) -> Figura:
    """Barras agrupadas por categoria (frequência relativa)."""
    categorias = categorias_comuns(dados.original, dados.gerado)
    originais = (
        percentuais_por_categoria(dados.original, categorias)
        if dados.original is not None
        else None
    )
    gerados = percentuais_por_categoria(dados.gerado, categorias)
    figura = figura_basica(
        _series(dados, categorias, originais, gerados), dados.coluna, EIXO_RELATIVA
    )
    return _com_legenda(figura, "group")


def _pontos(x: tuple[float, ...], y: tuple[float, ...], nome: str, papel: str) -> dict[str, Any]:
    mostrados_x, mostrados_y = amostrar(x, y)
    return {
        "type": "scatter",
        "mode": "markers",
        "x": mostrados_x,
        "y": mostrados_y,
        "marker": {"size": TAMANHO_PONTOS, "opacity": OPACIDADE_PONTOS},
        "name": nome,
        "meta": papel,
    }


def dispersao_gerada(dados: DadosParesGerados) -> Figura:
    """Pares gerados (e os originais, quando há origem), até 5.000 pontos por série (D101)."""
    tracos = []
    if dados.x_original is not None and dados.y_original is not None:
        nome = nome_serie("Original", len(dados.x_original))
        tracos.append(_pontos(dados.x_original, dados.y_original, nome, PAPEL_PRINCIPAL))
    tracos.append(_pontos(dados.x, dados.y, nome_serie("Gerado", len(dados.x)), PAPEL_REFERENCIA))
    figura = figura_basica(tracos, f"{dados.x_nome} (X)", f"{dados.y_nome} (Y)")
    figura["layout"]["showlegend"] = True
    return figura


def maior_diferenca_numerica(dados: DadosSobreposicao) -> float | None:
    """Maior distância, em pontos percentuais, entre as barras das duas séries."""
    if dados.original is None:
        return None
    bordas = classes_comuns(dados.original, dados.gerado)
    diferencas = percentuais_por_classe(dados.original, bordas) - percentuais_por_classe(
        dados.gerado, bordas
    )
    return float(np.abs(diferencas).max())


def maior_diferenca_categorica(dados: DadosSobreposicao) -> float | None:
    if dados.original is None:
        return None
    categorias = categorias_comuns(dados.original, dados.gerado)
    diferencas = percentuais_por_categoria(dados.original, categorias) - (
        percentuais_por_categoria(dados.gerado, categorias)
    )
    return float(np.abs(diferencas).max())
