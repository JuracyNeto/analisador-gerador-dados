"""Contrato das estratégias de geração univariada (Strategy, uma por tipo de variável)."""

from dataclasses import dataclass
from typing import Literal, Protocol

import numpy as np
import pandas as pd

type Modo = Literal["preservar", "parametros"]
type Metodo = Literal[
    "normal", "kde", "poisson", "empirica", "normal_inteira", "bernoulli", "frequencias"
]


@dataclass(frozen=True, slots=True, eq=False)
class EntradaEstrategia:
    """Pedido já validado pelo serviço; `originais` são os valores válidos da coluna de origem."""

    x: int
    modo: Modo
    originais: pd.Series | None = None
    media: float | None = None
    desvio: float | None = None
    p: float | None = None
    rotulos: tuple[str, str] | None = None  # (fracasso, sucesso) na binária
    normal_compativel: bool = False
    casas: int = 2
    limitar_faixa: bool = False


@dataclass(frozen=True, slots=True, eq=False)
class ResultadoEstrategia:
    valores: pd.Series
    metodo: Metodo
    recortou: bool = False


class Estrategia(Protocol):
    def gerar(self, entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        """Sorteia `entrada.x` valores."""
        ...


def numeros(serie: pd.Series | None) -> np.ndarray:
    """Valores de origem como float (as estratégias numéricas só rodam com origem válida)."""
    if serie is None:
        return np.array([], dtype="float64")
    return serie.to_numpy(dtype="float64")


def como_serie(valores: np.ndarray, casas: int) -> pd.Series:
    """Arredonda nas casas pedidas; sem casas, inteiros."""
    arredondados = np.round(valores, casas)
    return pd.Series(arredondados.astype("int64") if casas == 0 else arredondados)
