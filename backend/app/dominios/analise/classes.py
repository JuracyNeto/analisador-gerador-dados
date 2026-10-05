"""Classes (intervalos) para variáveis contínuas: Sturges, amplitude e contagem (spec 04)."""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.compartilhado.series import casas_decimais

MIN_CLASSES = 3
MAX_CLASSES = 30
MAX_CASAS = 4
_ARREDONDAMENTO_POSICAO = 9


@dataclass(frozen=True, slots=True)
class Classe:
    inferior: float
    superior: float
    frequencia: int

    @property
    def ponto_medio(self) -> float:
        return (self.inferior + self.superior) / 2


@dataclass(frozen=True, slots=True)
class Agrupamento:
    classes: tuple[Classe, ...]
    k: int
    k_sturges: int
    h: float
    casas: int
    metodo: str


def k_sturges(n: int) -> int:
    """k = ⌈1 + 3,322 · log₁₀ n⌉."""
    return math.ceil(1 + 3.322 * math.log10(n)) if n > 0 else 1


def amplitude_de_classe(amplitude_total: float, k: int, casas: int) -> float:
    """h = AT / k, arredondada para cima na casa decimal dos dados."""
    escala = 10.0**casas
    return math.ceil(round(amplitude_total / k * escala, _ARREDONDAMENTO_POSICAO)) / escala


def _contar(numeros: pd.Series, minimo: float, h: float, k: int) -> np.ndarray:
    posicoes = np.floor(np.round((numeros.to_numpy() - minimo) / h, _ARREDONDAMENTO_POSICAO))
    indices = np.clip(posicoes.astype(int), 0, k - 1)
    return np.bincount(indices, minlength=k)


def agrupar(numeros: pd.Series, classes: int | None) -> Agrupamento:
    """Classes [Lᵢ, Lᵢ + h); a última inclui o limite da direita."""
    valores = numeros.dropna()
    sturges = k_sturges(len(valores))
    minimo, maximo = float(valores.min()), float(valores.max())
    casas = min(casas_decimais(valores), MAX_CASAS)
    if maximo == minimo:
        unica = Classe(minimo, maximo, len(valores))
        return Agrupamento((unica,), 1, sturges, 0.0, casas, "sturges")
    k = classes if classes is not None else sturges
    h = amplitude_de_classe(maximo - minimo, k, casas)
    contagens = _contar(valores, minimo, h, k)
    limites = [round(minimo + i * h, MAX_CASAS + 2) for i in range(k + 1)]
    resultado = tuple(Classe(limites[i], limites[i + 1], int(contagens[i])) for i in range(k))
    metodo = "sturges" if classes is None else "usuario"
    return Agrupamento(resultado, k, sturges, h, max(casas, casas_decimais(pd.Series([h]))), metodo)
