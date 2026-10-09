"""Entradas e saídas da fábrica de figuras (independentes do domínio analise)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app.compartilhado.tipos import TipoVariavel


@dataclass(frozen=True, slots=True)
class Barra:
    """Uma categoria, valor ou classe da tabela de frequências, já na ordem de exibição."""

    rotulo: str
    frequencia: int
    percentual: float
    acumulado_pct: float | None = None
    valor: float | None = None
    inferior: float | None = None
    superior: float | None = None


@dataclass(frozen=True, slots=True, eq=False)
class DadosUnivariados:
    coluna: str
    tipo: TipoVariavel
    n: int
    barras: tuple[Barra, ...]
    valores: pd.Series | None = None


@dataclass(frozen=True, slots=True)
class ResumoCaixa:
    """Estatísticas do boxplot pré-calculadas (ADR 0003: nada de pontos brutos)."""

    minimo: float
    q1: float
    mediana: float
    q3: float
    maximo: float
    media: float
    bigode_inferior: float
    bigode_superior: float
    discrepantes: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class FiguraPronta:
    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CurvaFigura:
    """Curva Normal já escalada para frequência (pontos x, y), com μ e σ para a legenda."""

    x: tuple[float, ...]
    y: tuple[float, ...]
    media: float
    desvio: float


@dataclass(frozen=True, slots=True)
class QQFigura:
    """Quantis teóricos (Normal padrão) × observados; referência y = μ + σ·z."""

    teoricos: tuple[float, ...]
    observados: tuple[float, ...]
    media: float
    desvio: float


@dataclass(frozen=True, slots=True)
class BinomialFigura:
    k: tuple[int, ...]
    observados: tuple[int, ...]
    esperados: tuple[float, ...]
    n: int
    p: float


@dataclass(frozen=True, slots=True)
class DadosForma:
    """O que as figuras da forma precisam (spec 09); `None` = figura que não se aplica."""

    coluna: str
    tipo: TipoVariavel
    n: int
    barras: tuple[Barra, ...]
    curva: CurvaFigura | None = None
    qq: QQFigura | None = None
    binomial: BinomialFigura | None = None
    normal_compativel: bool | None = None
    binomial_compativel: bool | None = None
