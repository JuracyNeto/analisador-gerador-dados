"""Pares (X, Y) com médias, desvios e correlação alvo pelo método de Cholesky (spec 11)."""

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class ParametrosBivariado:
    n: int
    media_x: float
    media_y: float
    desvio_x: float
    desvio_y: float
    rho: float


def _centrar_e_padronizar(valores: np.ndarray) -> np.ndarray:
    centrados = valores - valores.mean()
    return centrados / centrados.std(ddof=1)


def ortonormalizar(z1: np.ndarray, z2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Gram-Schmidt: Z₂ ⟂ Z₁ com média 0 e DP 1 exatos (corr amostral = 0)."""
    primeiro = _centrar_e_padronizar(z1)
    segundo = z2 - z2.mean()
    segundo = segundo - (segundo @ primeiro) / (primeiro @ primeiro) * primeiro
    return primeiro, _centrar_e_padronizar(segundo)


def combinar(
    parametros: ParametrosBivariado, z1: np.ndarray, z2: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """X = μx + σx·Z₁ · Y = μy + σy·(ρ·Z₁ + √(1 − ρ²)·Z₂)  (Σ = L·Lᵀ)."""
    rho = parametros.rho
    x = parametros.media_x + parametros.desvio_x * z1
    y = parametros.media_y + parametros.desvio_y * (rho * z1 + math.sqrt(1 - rho**2) * z2)
    return x, y


def sortear_normais(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    return rng.standard_normal(n), rng.standard_normal(n)


def gerar_pares_exatos(
    parametros: ParametrosBivariado, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Com ajuste exato: médias, desvios e r amostral iguais aos pedidos."""
    return combinar(parametros, *ortonormalizar(*sortear_normais(parametros.n, rng)))


def gerar_pares(
    parametros: ParametrosBivariado, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Sem ajuste: r ≈ ρ, com a variação de uma amostra real."""
    return combinar(parametros, *sortear_normais(parametros.n, rng))
