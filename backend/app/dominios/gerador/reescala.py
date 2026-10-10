"""Ajustes depois do sorteio (spec 11): reescala exata, casas decimais e limite de faixa."""

from collections.abc import Callable

import numpy as np

MAX_CASAS = 6
TOLERANCIA_CASAS = 1e-9
RODADAS_FAIXA = 20


def reescalar(valores: np.ndarray, media: float, desvio: float) -> np.ndarray:
    """zᵢ = (gᵢ − ḡ) / s_g → gᵢ' = x̄ + s·zᵢ: média e desvio amostral exatos."""
    numeros = np.asarray(valores, dtype="float64")
    desvio_atual = float(np.std(numeros, ddof=1)) if len(numeros) > 1 else 0.0
    if desvio_atual == 0:
        return np.full(len(numeros), media)
    return media + desvio * (numeros - numeros.mean()) / desvio_atual


def casas_decimais(valores: np.ndarray) -> int:
    """Maior número de casas decimais usado nos valores (até 6)."""
    numeros = np.asarray(valores, dtype="float64")
    for casas in range(MAX_CASAS):
        escalados = numeros * 10**casas
        if np.allclose(escalados, np.round(escalados), rtol=0, atol=TOLERANCIA_CASAS * 10**casas):
            return casas
    return MAX_CASAS


def arredondar(valores: np.ndarray, casas: int) -> np.ndarray:
    return np.round(np.asarray(valores, dtype="float64"), casas)


def limitar_faixa(
    sortear: Callable[[int], np.ndarray],
    valores: np.ndarray,
    minimo: float,
    maximo: float,
    alvo: tuple[float, float],
) -> tuple[np.ndarray, bool]:
    """Sorteia de novo o que sai de [mín, máx] e refaz a reescala (D112); devolve se recortou."""
    atuais = np.asarray(valores, dtype="float64").copy()
    for _ in range(RODADAS_FAIXA):
        fora = (atuais < minimo) | (atuais > maximo)
        if not fora.any():
            return atuais, False
        atuais[fora] = sortear(int(fora.sum()))
        atuais = reescalar(atuais, *alvo)
    fora = (atuais < minimo) | (atuais > maximo)
    return np.clip(atuais, minimo, maximo), bool(fora.any())
