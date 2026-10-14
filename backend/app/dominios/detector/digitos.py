"""Dígitos final e inicial dos valores (R4, R8, R9; D119)."""

import numpy as np
import pandas as pd

from app.compartilhado.series import casas_decimais
from app.dominios.detector import textos

MIN_PASSOS_CENTRAIS = 10
"""A metade central precisa cobrir 10 passos da resolução para o último dígito variar à toa."""
FOLGA_MANTISSA = 1e-9
QUARTIS = (0.25, 0.75)


def resolucao(valores: np.ndarray) -> int:
    """Casas decimais da coluna: o maior número de casas observado (até 6)."""
    return casas_decimais(pd.Series(valores, dtype="float64"))


def digitos_finais(valores: np.ndarray, casas: int) -> np.ndarray:
    """Último dígito na resolução da coluna: round(|x| · 10^casas) mod 10."""
    escalados = np.round(np.abs(valores) * 10**casas).astype("int64")
    return np.asarray(escalados % 10, dtype="int64")


def primeiros_digitos(valores: np.ndarray) -> np.ndarray:
    """Primeiro dígito significativo de |x|, sem os zeros: 0,0123 → 1; 456 → 4."""
    positivos = np.abs(valores[valores != 0])
    mantissas = positivos / 10.0 ** np.floor(np.log10(positivos))
    digitos = np.floor(mantissas + FOLGA_MANTISSA).astype("int64")
    return np.asarray(np.clip(digitos, 1, 9), dtype="int64")


def passos_centrais(valores: np.ndarray, casas: int) -> float:
    """Amplitude interquartil medida em passos da resolução (0,01 com 2 casas)."""
    q1, q3 = np.quantile(valores, QUARTIS)
    return float((q3 - q1) * 10**casas)


def motivo_digito_final(valores: np.ndarray, minimo: int) -> str | None:
    """Por que o último dígito não pode ser testado (R4 e R9), ou None se pode."""
    if len(valores) < minimo:
        return textos.poucos_valores(minimo, len(valores))
    casas = resolucao(valores)
    if np.unique(digitos_finais(valores, casas)).size == 1:
        return textos.DIGITO_CONSTANTE
    if passos_centrais(valores, casas) < MIN_PASSOS_CENTRAIS:
        return textos.POUCA_VARIACAO
    return None
