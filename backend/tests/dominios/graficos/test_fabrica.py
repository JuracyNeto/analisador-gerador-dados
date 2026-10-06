import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.graficos.entradas import Barra, DadosUnivariados
from app.dominios.graficos.fabrica import figuras_univariadas

CATEGORIAS = tuple(Barra(f"c{i}", 10 - i, 10.0, 10.0 * (i + 1)) for i in range(6))
CLASSES = (
    Barra("2,0 ⊢ 3,9", 2, 40.0, 40.0, inferior=2.0, superior=3.9),
    Barra("3,9 ⊢ 5,8", 3, 60.0, 100.0, inferior=3.9, superior=5.8),
)
VALORES = pd.Series([2.0, 3.0, 4.0, 5.0, 5.5])


def _dados(
    tipo: TipoVariavel, barras: tuple[Barra, ...], valores: pd.Series | None = None
) -> DadosUnivariados:
    return DadosUnivariados("x", tipo, sum(b.frequencia for b in barras), barras, valores)


@pytest.mark.parametrize(
    ("tipo", "barras", "valores", "ids"),
    [
        (TipoVariavel.NOMINAL, CATEGORIAS, None, ["principal"]),
        (TipoVariavel.NOMINAL, CATEGORIAS[:3], None, ["principal", "pizza"]),
        (TipoVariavel.BINARIA, CATEGORIAS[:2], None, ["principal"]),
        (TipoVariavel.ORDINAL, CATEGORIAS, None, ["principal", "acumulada"]),
        (TipoVariavel.CONTINUA, CLASSES, VALORES, ["principal", "boxplot", "ogiva"]),
        (TipoVariavel.IDENTIFICADOR, CATEGORIAS, None, []),
    ],
)
def test_figuras_por_tipo(
    tipo: TipoVariavel, barras: tuple[Barra, ...], valores: pd.Series | None, ids: list[str]
) -> None:
    resultado = figuras_univariadas(_dados(tipo, barras, valores))

    assert [f.id for f in resultado] == ids


def test_discreta_tem_bastoes_boxplot_e_escada() -> None:
    barras = tuple(Barra(str(v), 1, 20.0, 20.0 * (i + 1), valor=v) for i, v in enumerate(VALORES))

    resultado = figuras_univariadas(_dados(TipoVariavel.DISCRETA, barras, VALORES))

    assert [f.rotulo for f in resultado] == ["Bastões", "Boxplot", "Acumulada"]


def test_principal_recomendada_com_titulo_resumo_e_porque() -> None:
    principal, *_ = figuras_univariadas(_dados(TipoVariavel.CONTINUA, CLASSES, VALORES))

    assert principal.recomendado is True
    assert principal.rotulo == "Histograma"
    assert principal.titulo == "Distribuição de x (n = 5)"
    assert principal.resumo == "A classe mais comum é 3,9 ⊢ 5,8, com 3 valores (60,0%)."
    assert principal.porque.startswith("Para números contínuos")


def test_complementares_nao_sao_recomendadas() -> None:
    _, boxplot, ogiva = figuras_univariadas(_dados(TipoVariavel.CONTINUA, CLASSES, VALORES))

    assert not boxplot.recomendado
    assert ogiva.resumo == "Metade dos valores chega até 3,9 ⊢ 5,8."
