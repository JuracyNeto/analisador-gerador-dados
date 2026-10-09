"""Fábrica: o melhor gráfico para cada tipo de variável, num só lugar (spec 08, ADR 0003)."""

from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from app.compartilhado.numeros import formatar_percentual
from app.compartilhado.tipos import TipoVariavel
from app.dominios.graficos import figuras, textos
from app.dominios.graficos import figuras_bivariadas as desenhos_bivariados
from app.dominios.graficos import figuras_forma as desenhos_forma
from app.dominios.graficos.entradas import (
    DadosBivariados,
    DadosForma,
    DadosMatriz,
    DadosUnivariados,
    FiguraPronta,
)
from app.dominios.graficos.figuras import Figura

MAX_FATIAS_PIZZA = 5


@dataclass(frozen=True, slots=True)
class _Molde:
    id: str
    tipo_grafico: str
    porque: str
    recomendado: bool = False


MOLDES = {
    "barras_nominal": _Molde("principal", "barras", textos.PORQUE["barras_nominal"], True),
    "barras_binaria": _Molde("principal", "barras", textos.PORQUE["barras_binaria"], True),
    "barras_ordinal": _Molde("principal", "barras", textos.PORQUE["barras_ordinal"], True),
    "bastoes": _Molde("principal", "bastoes", textos.PORQUE["bastoes"], True),
    "histograma": _Molde("principal", "histograma", textos.PORQUE["histograma"], True),
    "boxplot": _Molde("boxplot", "boxplot", textos.PORQUE["boxplot"]),
    "ogiva": _Molde("ogiva", "ogiva", textos.PORQUE["ogiva"]),
    "acumulada": _Molde("acumulada", "acumulada", textos.PORQUE["acumulada"]),
    "pizza": _Molde("pizza", "pizza", textos.PORQUE["pizza"]),
    "histograma_normal": _Molde(
        "histograma_normal", "histograma_normal", textos.PORQUE["histograma_normal"]
    ),
    "bastoes_normal": _Molde("bastoes_normal", "bastoes_normal", textos.PORQUE["bastoes_normal"]),
    "qqplot": _Molde("qqplot", "qqplot", textos.PORQUE["qqplot"]),
    "binomial": _Molde("binomial", "binomial", textos.PORQUE["binomial"]),
    "dispersao": _Molde("dispersao", "dispersao", textos.PORQUE["dispersao"], True),
    "residuos": _Molde("residuos", "residuos", textos.PORQUE["residuos"]),
    "matriz": _Molde("matriz", "matriz", textos.PORQUE["matriz"]),
}


def _pronta(molde: _Molde, titulo: str, resumo: str, figura: Figura) -> FiguraPronta:
    return FiguraPronta(
        id=molde.id,
        rotulo=textos.ROTULOS[molde.tipo_grafico],
        titulo=titulo,
        resumo=resumo,
        porque=molde.porque,
        recomendado=molde.recomendado,
        dados=figura,
    )


def _boxplot(dados: DadosUnivariados, valores: pd.Series) -> FiguraPronta:
    caixa = figuras.resumo_caixa(valores)
    return _pronta(
        MOLDES["boxplot"],
        textos.titulo_boxplot(dados),
        textos.resumo_caixa(caixa),
        figuras.boxplot(caixa, dados.coluna),
    )


def _pizza(dados: DadosUnivariados) -> FiguraPronta:
    maior = max(dados.barras, key=lambda b: b.frequencia)
    resumo = f"{maior.rotulo} representa {formatar_percentual(maior.percentual)} do total."
    return _pronta(MOLDES["pizza"], textos.titulo_pizza(dados), resumo, figuras.pizza(dados.barras))


def _nominal(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    principal = _pronta(
        MOLDES["barras_nominal"],
        textos.titulo_categorias(dados),
        textos.resumo_mais_frequente(dados, "A categoria"),
        figuras.barras_horizontais(dados.barras, dados.coluna),
    )
    if len(dados.barras) > MAX_FATIAS_PIZZA:
        return (principal,)
    return (principal, _pizza(dados))


def _binaria(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    principal = _pronta(
        MOLDES["barras_binaria"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "A categoria"),
        figuras.barras_verticais(dados.barras, dados.coluna),
    )
    return (principal,)


def _ordinal(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    principal = _pronta(
        MOLDES["barras_ordinal"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "A categoria"),
        figuras.barras_verticais(dados.barras, dados.coluna),
    )
    acumulada = _pronta(
        MOLDES["acumulada"],
        textos.titulo_acumulada(dados),
        textos.resumo_acumulada(dados),
        figuras.acumulada_categorias(dados.barras, dados.coluna),
    )
    return (principal, acumulada)


def _discreta(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    valores = dados.valores if dados.valores is not None else pd.Series(dtype="float64")
    principal = _pronta(
        MOLDES["bastoes"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "O valor"),
        figuras.bastoes(dados.barras, dados.coluna),
    )
    acumulada = _pronta(
        MOLDES["acumulada"],
        textos.titulo_acumulada(dados),
        textos.resumo_acumulada(dados),
        figuras.acumulada_escada(dados.barras, dados.coluna),
    )
    return (principal, _boxplot(dados, valores), acumulada)


def _continua(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    valores = dados.valores if dados.valores is not None else pd.Series(dtype="float64")
    principal = _pronta(
        MOLDES["histograma"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "A classe"),
        figuras.histograma(dados.barras, dados.coluna),
    )
    ogiva = _pronta(
        MOLDES["ogiva"],
        textos.titulo_ogiva(dados),
        textos.resumo_acumulada(dados),
        figuras.ogiva(dados.barras, dados.coluna),
    )
    return (principal, _boxplot(dados, valores), ogiva)


FABRICA: dict[TipoVariavel, Callable[[DadosUnivariados], tuple[FiguraPronta, ...]]] = {
    TipoVariavel.NOMINAL: _nominal,
    TipoVariavel.BINARIA: _binaria,
    TipoVariavel.ORDINAL: _ordinal,
    TipoVariavel.DISCRETA: _discreta,
    TipoVariavel.CONTINUA: _continua,
}


def figuras_univariadas(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    """Gráfico principal + complementares do tipo; a 1ª figura é sempre a recomendada."""
    construir = FABRICA.get(dados.tipo)
    return construir(dados) if construir else ()


def _curva_da_forma(dados: DadosForma) -> FiguraPronta | None:
    """Histograma (contínua) ou bastões (discreta) com a curva Normal."""
    if dados.curva is None:
        return None
    resumo = textos.RESUMOS_CURVA[dados.normal_compativel]
    if dados.tipo == TipoVariavel.CONTINUA:
        return _pronta(
            MOLDES["histograma_normal"],
            textos.titulo_histograma_normal(dados.coluna, dados.n),
            resumo,
            desenhos_forma.histograma_normal(dados.barras, dados.curva, dados.coluna),
        )
    return _pronta(
        MOLDES["bastoes_normal"],
        textos.titulo_bastoes_normal(dados.coluna, dados.n),
        resumo,
        desenhos_forma.bastoes_normal(dados.barras, dados.curva, dados.coluna),
    )


def _qqplot(dados: DadosForma) -> FiguraPronta | None:
    if dados.qq is None:
        return None
    return _pronta(
        MOLDES["qqplot"],
        textos.titulo_qqplot(dados.coluna),
        textos.RESUMOS_QQ[dados.normal_compativel],
        desenhos_forma.qqplot(dados.qq, dados.coluna),
    )


def _binomial(dados: DadosForma) -> FiguraPronta | None:
    if dados.binomial is None:
        return None
    binomial = dados.binomial
    return _pronta(
        MOLDES["binomial"],
        textos.titulo_binomial(dados.coluna, binomial.n, binomial.p),
        textos.RESUMOS_BINOMIAL[dados.binomial_compativel],
        desenhos_forma.observado_esperado(binomial, dados.coluna),
    )


def figuras_forma(dados: DadosForma) -> tuple[FiguraPronta, ...]:
    """Figuras da aba Forma (spec 09): só as que têm dados (D94)."""
    candidatas = (_curva_da_forma(dados), _qqplot(dados), _binomial(dados))
    return tuple(figura for figura in candidatas if figura is not None)


def figuras_bivariadas(dados: DadosBivariados) -> tuple[FiguraPronta, ...]:
    """Dispersão com a reta e resíduos × X (spec 10)."""
    n = len(dados.x)
    mostrados = len(desenhos_bivariados.amostrar(dados.x, dados.y)[0])
    dispersao = _pronta(
        MOLDES["dispersao"],
        textos.titulo_dispersao(dados.x_nome, dados.y_nome, n),
        textos.resumo_dispersao(dados.forca, dados.sentido, n, mostrados),
        desenhos_bivariados.dispersao(dados),
    )
    residuos = _pronta(
        MOLDES["residuos"],
        textos.TITULO_RESIDUOS,
        textos.resumo_residuos(dados.y_nome),
        desenhos_bivariados.residuos(dados),
    )
    return (dispersao, residuos)


MIN_COLUNAS_MATRIZ = 2


def figura_matriz(dados: DadosMatriz) -> FiguraPronta | None:
    """Heatmap da matriz de correlação; com menos de 2 colunas não há figura."""
    if len(dados.colunas) < MIN_COLUNAS_MATRIZ:
        return None
    return _pronta(
        MOLDES["matriz"], textos.TITULO_MATRIZ, dados.resumo, desenhos_bivariados.heatmap(dados)
    )
