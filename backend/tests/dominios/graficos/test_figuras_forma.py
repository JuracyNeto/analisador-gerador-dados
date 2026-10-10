from typing import Any

import plotly.graph_objects as go
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.graficos import figuras_forma
from app.dominios.graficos.entradas import (
    BinomialFigura,
    CurvaFigura,
    DadosForma,
    QQFigura,
)
from app.dominios.graficos.fabrica import figuras_forma as fabricar
from app.dominios.graficos.tema import PAPEL_PRINCIPAL, PAPEL_REFERENCIA
from tests.dominios.graficos.barras_exemplo import CLASSES, VALORES

CURVA = CurvaFigura((1.0, 2.0, 3.0), (0.5, 2.0, 0.5), media=70.31, desvio=11.2)
QQ = QQFigura((-1.0, 0.0, 1.0), (60.0, 70.0, 81.0), media=70.0, desvio=10.0)
BINOMIAL = BinomialFigura((0, 1, 2), (3, 5, 2), (2.5, 5.0, 2.5), n=2, p=0.4567)


def _valida(figura: dict[str, Any]) -> dict[str, Any]:
    go.Figure(figura)
    assert "template" not in figura["layout"]
    assert figura["layout"]["showlegend"] is True
    return figura


def _papeis(figura: dict[str, Any]) -> list[str]:
    return [traco["meta"] for traco in figura["data"]]


def test_histograma_com_curva_normal() -> None:
    figura = _valida(figuras_forma.histograma_normal(CLASSES, CURVA, "peso_kg"))

    barras, curva = figura["data"]
    assert _papeis(figura) == [PAPEL_PRINCIPAL, PAPEL_REFERENCIA]
    assert barras["name"] == "Frequência observada"
    assert curva["name"] == "Curva Normal (μ = 70,31; σ = 11,2)"
    assert curva["mode"] == "lines"
    assert curva["y"] == [0.5, 2.0, 0.5]


def test_qqplot_tem_pontos_e_reta_de_referencia() -> None:
    figura = _valida(figuras_forma.qqplot(QQ, "peso_kg"))

    pontos, reta = figura["data"]
    assert pontos["mode"] == "markers"
    assert pontos["name"] == "Valores de peso_kg"
    assert reta["x"] == [-1.0, 1.0]
    assert reta["y"] == [pytest.approx(60.0), pytest.approx(80.0)]
    assert figura["layout"]["xaxis"]["title"]["text"] == "Quantis teóricos (Normal)"


def test_bastoes_com_curva_normal() -> None:
    figura = _valida(figuras_forma.bastoes_normal(VALORES, CURVA, "filhos"))

    assert _papeis(figura) == [PAPEL_PRINCIPAL, PAPEL_PRINCIPAL, PAPEL_REFERENCIA]


def test_observado_esperado_binomial() -> None:
    figura = _valida(figuras_forma.observado_esperado(BINOMIAL, "faltas"))

    observado, esperado = figura["data"]
    assert observado["y"] == [3, 5, 2]
    assert esperado["y"] == [2.5, 5.0, 2.5]
    assert esperado["meta"] == PAPEL_REFERENCIA
    assert figura["layout"]["barmode"] == "group"


def _dados(**campos: Any) -> DadosForma:
    padrao: dict[str, Any] = {
        "coluna": "x",
        "tipo": TipoVariavel.CONTINUA,
        "n": 5,
        "barras": CLASSES,
    }
    return DadosForma(**(padrao | campos))


def test_fabrica_da_continua() -> None:
    prontas = fabricar(_dados(curva=CURVA, qq=QQ, normal_compativel=True))

    assert [f.id for f in prontas] == ["histograma_normal", "qqplot"]
    assert prontas[0].titulo == "Histograma de x com curva Normal (n = 5)"
    assert prontas[0].resumo == "As barras acompanham a curva."
    assert (
        prontas[1].resumo == "Os pontos ficam perto da reta: os dados se comportam como uma Normal."
    )


def test_fabrica_da_discreta_sem_normal() -> None:
    prontas = fabricar(
        _dados(
            tipo=TipoVariavel.DISCRETA, barras=VALORES, binomial=BINOMIAL, binomial_compativel=False
        )
    )

    assert [f.id for f in prontas] == ["binomial"]
    assert prontas[0].titulo == "x: observado × Binomial (n = 2; p = 0,4567)"
    assert prontas[0].resumo == "Há diferenças entre o observado e o esperado."


def test_fabrica_da_discreta_com_normal() -> None:
    prontas = fabricar(
        _dados(tipo=TipoVariavel.DISCRETA, barras=VALORES, curva=CURVA, normal_compativel=False)
    )

    assert [f.id for f in prontas] == ["bastoes_normal"]
    assert prontas[0].resumo == "As barras se afastam da curva em alguns trechos."


def test_fabrica_sem_nada_nao_tem_figuras() -> None:
    assert fabricar(_dados(tipo=TipoVariavel.BINARIA)) == ()
