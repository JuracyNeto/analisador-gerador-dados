"""Utilitários estatísticos sem regra de negócio, usados por mais de um domínio (padroes §2)."""

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy import stats

ALFA = 0.05  # nível de significância padrão (00-visao-geral.md)
MINIMO_ESPERADO = 5.0
AMOSTRA_MEDCOUPLE = 2_000
"""O medcouple compara pares de valores (O(n²)); acima disso, numa amostra fixa."""
SEMENTE_MEDCOUPLE = 0


@dataclass(frozen=True, slots=True)
class ResultadoQuiQuadrado:
    estatistica: float
    gl: int
    p_valor: float


@dataclass(frozen=True, slots=True)
class ResultadoRuns:
    runs: int
    z: float
    p_valor: float


def _juntar(observados: list[float], esperados: list[float], i: int, j: int) -> None:
    """Soma o grupo j no grupo i e apaga o j (i e j vizinhos)."""
    observados[i] += observados.pop(j)
    esperados[i] += esperados.pop(j)


def _indice_pequeno(esperados: list[float], minimo: float) -> int | None:
    return next((i for i, valor in enumerate(esperados) if valor < minimo), None)


def _vizinho_menor(esperados: list[float], i: int) -> int:
    if i == 0:
        return 1
    if i == len(esperados) - 1:
        return i - 1
    return i - 1 if esperados[i - 1] <= esperados[i + 1] else i + 1


def agrupar_esperados_pequenos(
    observados: Sequence[float], esperados: Sequence[float], minimo: float = MINIMO_ESPERADO
) -> tuple[list[float], list[float]]:
    """Junta grupos vizinhos até cada esperado ser ≥ mínimo (condição do qui-quadrado)."""
    obs, esp = list(observados), list(esperados)
    while len(esp) > 1:
        i = _indice_pequeno(esp, minimo)
        if i is None:
            break
        vizinho = _vizinho_menor(esp, i)
        _juntar(obs, esp, min(i, vizinho), max(i, vizinho))
    return obs, esp


def teste_binomial_unilateral(k: int, n: int, p0: float) -> float:
    """P(X ≥ k) com X ~ Binomial(n, p₀): chance de ver k ou mais sucessos por acaso."""
    return float(stats.binom.sf(k - 1, n, p0))


def teste_qui_quadrado(observados: np.ndarray, esperados: np.ndarray) -> ResultadoQuiQuadrado:
    """χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ com gl = k − 1 (esperados na mesma escala dos observados)."""
    obs = np.asarray(observados, dtype="float64")
    esp = np.asarray(esperados, dtype="float64")
    estatistica = float(np.sum((obs - esp) ** 2 / esp))
    gl = len(obs) - 1
    return ResultadoQuiQuadrado(estatistica, gl, float(stats.chi2.sf(estatistica, gl)))


def teste_runs(acima: np.ndarray) -> ResultadoRuns:
    """Runs de Wald-Wolfowitz: Z = (R − μ_R)/σ_R e p bilateral (spec 12)."""
    marcas = np.asarray(acima, dtype=bool)
    runs = int(np.count_nonzero(marcas[1:] != marcas[:-1])) + 1 if len(marcas) else 0
    n1 = int(np.count_nonzero(marcas))
    n2 = len(marcas) - n1
    soma = n1 + n2
    variancia = 2 * n1 * n2 * (2 * n1 * n2 - soma) / (soma**2 * (soma - 1)) if soma > 1 else 0
    if variancia <= 0:
        return ResultadoRuns(runs, 0.0, 1.0)
    media = 2 * n1 * n2 / soma + 1
    z = (runs - media) / math.sqrt(variancia)
    return ResultadoRuns(runs, z, float(2 * stats.norm.sf(abs(z))))


def autocorrelacao_lag1(valores: np.ndarray) -> float:
    """ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²; valores constantes → 0."""
    desvios = np.asarray(valores, dtype="float64") - float(np.mean(valores))
    denominador = float(np.sum(desvios**2))
    if denominador == 0:
        return 0.0
    return float(np.sum(desvios[:-1] * desvios[1:])) / denominador


def teste_poisson_unilateral(k: int, media: float) -> float:
    """P(X ≥ k) com X ~ Poisson(média): chance de ver k casos ou mais por acaso."""
    if k <= 0:
        return 1.0
    if media <= 0:
        return 0.0
    return float(stats.poisson.sf(k - 1, media))


def medcouple(valores: np.ndarray) -> float:
    """Medcouple: assimetria robusta, entre −1 e 1 (Brys, Hubert e Struyf).

    MC = mediana de h(xᵢ, xⱼ) = ((xᵢ − m) − (m − xⱼ)) / (xᵢ − xⱼ), com xᵢ ≥ m ≥ xⱼ e m a
    mediana; os pares com xᵢ = xⱼ = m contam 0.
    """
    x = np.asarray(valores, dtype="float64")
    if len(x) > AMOSTRA_MEDCOUPLE:
        x = np.random.default_rng(SEMENTE_MEDCOUPLE).choice(x, AMOSTRA_MEDCOUPLE, replace=False)
    m = float(np.median(x))
    acima, abaixo = x[x >= m][:, np.newaxis], x[x <= m][np.newaxis, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        h = ((acima - m) - (m - abaixo)) / (acima - abaixo)
    return float(np.median(np.where(acima == abaixo, 0.0, h)))
