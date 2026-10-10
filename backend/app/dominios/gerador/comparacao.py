"""Tabela Original × Gerado (spec 11): diferença absoluta, como no print 6a (D110)."""

from dataclasses import dataclass

import pandas as pd

from app.dominios.gerador import textos
from app.dominios.gerador.resultados import LinhaComparacao, ResumoComparavel

PERCENTUAL = 100


def _linha(estatistica: str, original: float | None, gerado: float | None) -> LinhaComparacao:
    diferenca = gerado - original if original is not None and gerado is not None else None
    return LinhaComparacao(estatistica, original, gerado, diferenca)


def _medida(resumo: ResumoComparavel | None, atributo: str) -> float | None:
    if resumo is None:
        return None
    valor = getattr(resumo, atributo)
    return None if valor is None else float(valor)


def comparar_numericos(
    original: ResumoComparavel | None, gerado: ResumoComparavel
) -> tuple[LinhaComparacao, ...]:
    """n, média, mediana, DP, mín, máx, assimetria e curtose."""
    return tuple(
        _linha(nome, _medida(original, atributo), _medida(gerado, atributo))
        for nome, atributo in textos.ESTATISTICAS_NUMERICAS
    )


def _frequencias(valores: pd.Series) -> pd.Series:
    return valores.astype(str).value_counts(normalize=True) * PERCENTUAL


def comparar_categoricos(
    original: pd.Series | None, gerado: pd.Series
) -> tuple[LinhaComparacao, ...]:
    """n e fr% por categoria (diferença em pontos percentuais), na ordem do original."""
    gerados = _frequencias(gerado)
    originais = _frequencias(original) if original is not None else pd.Series(dtype="float64")
    categorias = list(originais.index) + [c for c in gerados.index if c not in originais.index]
    n_original = float(len(original)) if original is not None else None
    linhas = [_linha(textos.ESTATISTICA_N, n_original, float(len(gerado)))]
    for categoria in categorias:
        valor_original = float(originais.get(categoria, 0.0)) if original is not None else None
        linhas.append(
            _linha(
                textos.estatistica_frequencia(str(categoria)),
                valor_original,
                float(gerados.get(categoria, 0.0)),
            )
        )
    return tuple(linhas)


@dataclass(frozen=True, slots=True)
class MedidasPar:
    """Médias, desvios e r de um par (original, alvo ou gerado)."""

    n: int
    media_x: float
    media_y: float
    desvio_x: float
    desvio_y: float
    r: float


def _valores(medidas: MedidasPar) -> tuple[float, ...]:
    return (
        float(medidas.n),
        medidas.media_x,
        medidas.media_y,
        medidas.desvio_x,
        medidas.desvio_y,
        medidas.r,
    )


def comparar_pares(
    x: str, y: str, original: MedidasPar | None, gerado: MedidasPar
) -> tuple[LinhaComparacao, ...]:
    """Bivariado: sem origem, a coluna "original" leva o alvo pedido."""
    gerados = _valores(gerado)
    originais: tuple[float | None, ...] = (
        _valores(original) if original is not None else (None,) * len(gerados)
    )
    return tuple(
        _linha(nome, valor_original, valor_gerado)
        for nome, valor_original, valor_gerado in zip(
            textos.estatisticas_par(x, y), originais, gerados, strict=True
        )
    )
