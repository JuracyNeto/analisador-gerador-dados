"""Value objects da análise bivariada (spec 10): par de colunas, correlação, regressão, matriz."""

from dataclasses import dataclass
from typing import Literal

import numpy as np

from app.dominios.analise.resultados import Figura, Formula, Medida

type Forca = Literal["fraca", "moderada", "forte"]
type Sentido = Literal["positiva", "negativa", "nula"]


@dataclass(frozen=True, slots=True, eq=False)
class Par:
    """Duas colunas numéricas, só com as linhas em que as duas têm valor."""

    x: str
    y: str
    valores_x: np.ndarray
    valores_y: np.ndarray
    n_descartados: int = 0


@dataclass(frozen=True, slots=True)
class Faixa:
    minimo: float
    maximo: float


@dataclass(frozen=True, slots=True)
class Regressao:
    """Ŷ = a + bX, com R² (em %, 0–100) e o erro padrão da estimativa."""

    a: float
    b: float
    equacao: str
    reta: Medida
    r2: Medida
    se: Medida


@dataclass(frozen=True, slots=True)
class Bivariada:
    x: str
    y: str
    n: int
    n_descartados: int
    pearson: Medida
    teste_t: Medida
    spearman: Medida
    forca: Forca
    sentido: Sentido
    regressao: Regressao
    faixa_x: Faixa
    interpretacoes: tuple[str, ...]
    formulas: tuple[Formula, ...]
    figuras: tuple[Figura, ...] = ()


@dataclass(frozen=True, slots=True)
class Previsao:
    """ŷ = a + b·x; fora de [mín X, máx X] é extrapolação (spec 10)."""

    x: float
    y_previsto: float
    extrapolacao: bool
    faixa_x: Faixa
    frase: str
    aviso: str | None = None


@dataclass(frozen=True, slots=True)
class MatrizCorrelacao:
    colunas: tuple[str, ...]
    valores: tuple[tuple[float | None, ...], ...]
    resumo: str
    figura: Figura | None = None
