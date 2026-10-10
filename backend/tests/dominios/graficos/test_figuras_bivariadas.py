from typing import Any

import numpy as np
import plotly.graph_objects as go
import pytest

from app.dominios.graficos import figuras_bivariadas
from app.dominios.graficos.entradas import DadosBivariados, DadosMatriz
from app.dominios.graficos.fabrica import figura_matriz
from app.dominios.graficos.fabrica import figuras_bivariadas as fabricar
from app.dominios.graficos.tema import PAPEL_DIVERGENTE, PAPEL_PRINCIPAL, PAPEL_REFERENCIA

DADOS = DadosBivariados(
    x_nome="altura_m",
    y_nome="peso_kg",
    x=(1.5, 1.6, 1.7, 1.8),
    y=(50.0, 58.0, 70.0, 75.0),
    a=-98.4,
    b=98.1,
    equacao="Ŷ = −98,4 + 98,1·X",
    forca="forte",
    sentido="positiva",
)
MATRIZ = DadosMatriz(
    colunas=("idade", "altura_m", "peso_kg"),
    valores=((1.0, 0.12, -0.21), (0.12, 1.0, 0.78), (-0.21, 0.78, None)),
    resumo="O par mais forte é altura_m × peso_kg (0,78).",
)


def _valida(figura: dict[str, Any]) -> dict[str, Any]:
    go.Figure(figura)
    assert "template" not in figura["layout"]
    return figura


def test_dispersao_tem_pontos_e_reta() -> None:
    figura = _valida(figuras_bivariadas.dispersao(DADOS))

    pontos, reta = figura["data"]
    assert (pontos["meta"], reta["meta"]) == (PAPEL_PRINCIPAL, PAPEL_REFERENCIA)
    assert pontos["mode"] == "markers"
    assert pontos["name"] == "Pontos (n = 4)"
    assert reta["name"] == DADOS.equacao
    assert reta["x"] == [1.5, 1.8]
    assert reta["y"] == [pytest.approx(-98.4 + 98.1 * 1.5), pytest.approx(-98.4 + 98.1 * 1.8)]
    assert figura["layout"]["showlegend"] is True
    assert figura["layout"]["xaxis"]["title"]["text"] == "altura_m (X)"


def test_residuos_contra_x_com_linha_zero_tracejada() -> None:
    figura = _valida(figuras_bivariadas.residuos(DADOS))

    pontos, zero = figura["data"]
    assert pontos["x"] == list(DADOS.x)
    assert pontos["y"][0] == pytest.approx(50.0 - (-98.4 + 98.1 * 1.5))
    assert zero["y"] == [0, 0]
    assert zero["line"]["dash"] == "dash"
    assert figura["layout"]["yaxis"]["title"]["text"] == "Resíduo (Y − Ŷ)"


def test_muitos_pontos_viram_uma_amostra_fixa() -> None:
    rng = np.random.default_rng(1)
    x = tuple(rng.normal(size=6000).tolist())
    dados = DadosBivariados("a", "b", x, x, 0.0, 1.0, "Ŷ = 0 + 1·X", "forte", "positiva")

    primeira = fabricar(dados)
    segunda = fabricar(dados)

    assert len(primeira[0].dados["data"][0]["x"]) == 5000
    assert primeira[0].dados == segunda[0].dados
    assert primeira[0].resumo.endswith("Mostramos 5.000 dos 6.000 pontos.")


def test_heatmap_divergente_com_valores_anotados() -> None:
    figura = _valida(figuras_bivariadas.heatmap(MATRIZ))

    traco = figura["data"][0]
    assert traco["meta"] == PAPEL_DIVERGENTE
    assert (traco["zmin"], traco["zmax"]) == (-1, 1)
    assert traco["text"][1] == ["0,12", "1", "0,78"]
    assert traco["text"][2] == ["−0,21", "0,78", ""]
    assert figura["layout"]["yaxis"]["autorange"] == "reversed"


@pytest.mark.parametrize(
    ("forca", "sentido", "inicio"),
    [
        ("forte", "positiva", "Os pontos sobem da esquerda para a direita e ficam perto da reta."),
        ("moderada", "negativa", "Os pontos descem da esquerda para a direita, mas se espalham"),
        ("fraca", "positiva", "Os pontos não seguem uma direção clara."),
    ],
)
def test_resumo_da_dispersao(forca: str, sentido: str, inicio: str) -> None:
    dados = DadosBivariados("x", "y", (1.0, 2.0), (1.0, 2.0), 0.0, 1.0, "e", forca, sentido)

    assert fabricar(dados)[0].resumo.startswith(inicio)


def test_fabrica_da_bivariada() -> None:
    dispersao, residuos = fabricar(DADOS)

    assert (dispersao.id, residuos.id) == ("dispersao", "residuos")
    assert dispersao.titulo == "peso_kg em função de altura_m (n = 4)"
    assert residuos.titulo == "Resíduos da regressão"
    assert "peso_kg real e o previsto" in residuos.resumo


def test_fabrica_da_matriz() -> None:
    pronta = figura_matriz(MATRIZ)

    assert pronta is not None
    assert (pronta.id, pronta.titulo, pronta.resumo) == (
        "matriz",
        "Matriz de correlação (Pearson)",
        MATRIZ.resumo,
    )
    assert figura_matriz(DadosMatriz(("a",), ((1.0,),), "x")) is None
