"""Quartis, decis e percentis por interpolação linear; ordinais por categoria (spec 06)."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise.frequencias import ordem_completa
from app.dominios.analise.resultados import (
    Amostra,
    Separatrizes,
    TipoSeparatriz,
    ValorSeparatriz,
)

_TOLERANCIA = 1e-12


@dataclass(frozen=True, slots=True)
class Divisao:
    """Em quantas partes iguais os dados são divididos e o prefixo do rótulo (Q, D, P)."""

    prefixo: str
    partes: int

    @property
    def proporcoes(self) -> tuple[float, ...]:
        return tuple(i / self.partes for i in range(1, self.partes))

    def rotulo(self, p: float) -> str:
        return f"{self.prefixo}{round(p * self.partes)}"


DIVISOES: dict[TipoSeparatriz, Divisao] = {
    "quartil": Divisao("Q", 4),
    "decil": Divisao("D", 10),
    "percentil": Divisao("P", 100),
}
DESTAQUES = ("P1", "P5", "P10", "P25", "P50", "P75", "P90", "P95", "P99")


def quantis(valores: np.ndarray, divisao: Divisao) -> tuple[ValorSeparatriz, ...]:
    """Qp com h = (n − 1)·p e interpolação linear (numpy.quantile, método linear)."""
    resultado = np.quantile(valores, divisao.proporcoes, method="linear")
    return tuple(
        ValorSeparatriz(divisao.rotulo(p), p, float(q))
        for p, q in zip(divisao.proporcoes, resultado, strict=True)
    )


def quantis_ordinais(amostra: Amostra, divisao: Divisao) -> tuple[ValorSeparatriz, ...]:
    """Categoria cuja frequência relativa acumulada atinge p."""
    ordem = ordem_completa(amostra)
    contagens = amostra.valores.astype(str).value_counts()
    acumuladas = np.cumsum([int(contagens.get(c, 0)) for c in ordem]) / amostra.n
    posicoes = np.searchsorted(acumuladas, np.array(divisao.proporcoes) - _TOLERANCIA)
    return tuple(
        ValorSeparatriz(divisao.rotulo(p), p, ordem[min(int(i), len(ordem) - 1)])
        for p, i in zip(divisao.proporcoes, posicoes, strict=True)
    )


def _montar(calcular: Callable[[Divisao], tuple[ValorSeparatriz, ...]]) -> Separatrizes:
    return Separatrizes(
        quartis=calcular(DIVISOES["quartil"]),
        decis=calcular(DIVISOES["decil"]),
        percentis=calcular(DIVISOES["percentil"]),
        destaques=DESTAQUES,
    )


def separatrizes(amostra: Amostra) -> Separatrizes | None:
    """Numéricas por interpolação; ordinais como categoria; nominal/binária não se aplica."""
    if amostra.tipo in TIPOS_NUMERICOS:
        valores = amostra.valores.to_numpy(dtype="float64")
        return _montar(lambda divisao: quantis(valores, divisao))
    if amostra.tipo == TipoVariavel.ORDINAL:
        return _montar(lambda divisao: quantis_ordinais(amostra, divisao))
    return None
