from typing import Any

import pandas as pd
import plotly.graph_objects as go
import pytest

from app.dominios.graficos import figuras
from app.dominios.graficos.entradas import Barra
from app.dominios.graficos.tema import PAPEIS

CATEGORIAS = (
    Barra("Goiânia", 87, 38.2),
    Barra("Anápolis", 38, 16.7),
    Barra("Trindade", 3, 1.3),
)
VALORES = (
    Barra("1", 2, 20.0, 20.0, valor=1.0),
    Barra("2", 5, 50.0, 70.0, valor=2.0),
    Barra("3", 3, 30.0, 100.0, valor=3.0),
)
CLASSES = (
    Barra("2,0 ⊢ 3,9", 2, 40.0, 40.0, inferior=2.0, superior=3.9),
    Barra("3,9 ⊢ 5,8", 3, 60.0, 100.0, inferior=3.9, superior=5.8),
)


def _valida(figura: dict[str, Any]) -> dict[str, Any]:
    """O Plotly recusa propriedades inválidas; é o que garante o formato sem tipos no app."""
    go.Figure(figura)
    assert "template" not in figura["layout"]
    return figura


def test_barras_horizontais_poem_a_maior_no_topo() -> None:
    figura = _valida(figuras.barras_horizontais(CATEGORIAS, "cidade"))

    traco = figura["data"][0]
    assert traco["orientation"] == "h"
    assert traco["y"] == ["Trindade", "Anápolis", "Goiânia"]
    assert traco["text"][-1] == "87 (38,2%)"


def test_sem_rotulos_com_mais_de_12_barras() -> None:
    muitas = tuple(Barra(str(i), 1, 1.0) for i in range(13))

    figura = _valida(figuras.barras_verticais(muitas, "x"))

    assert "text" not in figura["data"][0]


def test_bastoes_tem_hastes_finas_e_pontos() -> None:
    figura = _valida(figuras.bastoes(VALORES, "filhos"))

    hastes, pontos = figura["data"]
    assert hastes["width"] == figuras.LARGURA_BASTAO
    assert pontos["mode"] == "markers"
    assert hastes["x"] == [1.0, 2.0, 3.0]


def test_histograma_usa_as_classes() -> None:
    figura = _valida(figuras.histograma(CLASSES, "peso_kg"))

    traco = figura["data"][0]
    assert traco["x"] == pytest.approx([2.95, 4.85])
    assert traco["width"] == pytest.approx([1.9, 1.9])
    assert traco["customdata"] == ["2,0 ⊢ 3,9", "3,9 ⊢ 5,8"]
    assert figura["layout"]["bargap"] == 0


def test_resumo_caixa_e_boxplot_sem_pontos_brutos() -> None:
    valores = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 100.0])

    caixa = figuras.resumo_caixa(valores)
    figura = _valida(figuras.boxplot(caixa, "x"))

    assert (caixa.q1, caixa.mediana, caixa.q3) == (2.25, 3.5, 4.75)
    assert caixa.discrepantes == (100.0,)
    assert caixa.bigode_superior == 5.0
    assert "x" not in figura["data"][0]
    assert figura["data"][1]["x"] == [100.0]


def test_ogiva_comeca_no_zero() -> None:
    figura = _valida(figuras.ogiva(CLASSES, "peso_kg"))

    assert figura["data"][0]["x"] == [2.0, 3.9, 5.8]
    assert figura["data"][0]["y"] == [0.0, 40.0, 100.0]


def test_acumuladas_e_pizza() -> None:
    escada = _valida(figuras.acumulada_escada(VALORES, "filhos"))
    barras = _valida(figuras.acumulada_categorias(VALORES, "filhos"))
    pizza = _valida(figuras.pizza(CATEGORIAS))

    assert escada["data"][0]["line"]["shape"] == "hv"
    assert barras["data"][0]["y"] == [20.0, 70.0, 100.0]
    assert pizza["data"][0]["labels"] == ["Goiânia", "Anápolis", "Trindade"]


def _figuras_de_exemplo() -> list[dict[str, Any]]:
    caixa = figuras.resumo_caixa(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 100.0]))
    return [
        figuras.barras_horizontais(CATEGORIAS, "cidade"),
        figuras.barras_verticais(CATEGORIAS, "sexo"),
        figuras.bastoes(VALORES, "filhos"),
        figuras.histograma(CLASSES, "peso_kg"),
        figuras.boxplot(caixa, "x"),
        figuras.ogiva(CLASSES, "peso_kg"),
        figuras.acumulada_categorias(VALORES, "filhos"),
        figuras.acumulada_escada(VALORES, "filhos"),
    ]


@pytest.mark.parametrize("figura", _figuras_de_exemplo())
def test_tracos_tem_papel_e_nenhuma_cor_fixa(figura: dict[str, Any]) -> None:
    # A cor depende do tema (claro no relatório, o ativo no frontend): a figura só diz o papel.
    for traco in _valida(figura)["data"]:
        assert traco["meta"] in PAPEIS
        assert "color" not in traco.get("marker", {})
        assert "color" not in traco.get("line", {})
