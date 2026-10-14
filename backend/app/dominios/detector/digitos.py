"""Dígitos final e inicial dos valores (R4, R8, R9; D119)."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.compartilhado import estatistica
from app.compartilhado.estatistica import ResultadoQuiQuadrado
from app.compartilhado.series import casas_decimais
from app.dominios.detector import textos
from app.dominios.detector.resultados import GraficoDigitos, PosicaoDigito

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


@dataclass(frozen=True, slots=True, eq=False)
class FrequenciaDigitos:
    """Dígito de cada valor e as proporções observadas × esperadas, com o qui-quadrado."""

    observados: np.ndarray
    possiveis: np.ndarray
    proporcoes: np.ndarray
    esperadas: np.ndarray
    teste: ResultadoQuiQuadrado

    @property
    def indice_mais_acima(self) -> int:
        """Posição do dígito que mais passa do esperado."""
        return int(np.argmax(self.proporcoes - self.esperadas))

    @property
    def mais_acima(self) -> int:
        return int(self.possiveis[self.indice_mais_acima])

    def grafico(self, coluna: str, posicao: PosicaoDigito) -> GraficoDigitos:
        """Dados da figura observado × esperado (R8, R9; D123)."""
        return GraficoDigitos(
            coluna,
            posicao,
            tuple(int(digito) for digito in self.possiveis),
            tuple(float(proporcao) for proporcao in self.proporcoes),
            tuple(float(esperada) for esperada in self.esperadas),
        )

    @property
    def mad(self) -> float:
        """Desvio absoluto médio: média de |observado − esperado| (Nigrini)."""
        return float(np.mean(np.abs(self.proporcoes - self.esperadas)))


def comparar_frequencias(
    observados: np.ndarray, possiveis: np.ndarray, esperadas: np.ndarray
) -> FrequenciaDigitos:
    """χ² das contagens de cada dígito possível contra as proporções esperadas."""
    contagens = np.bincount(observados, minlength=int(possiveis.max()) + 1)[possiveis]
    n = len(observados)
    teste = estatistica.teste_qui_quadrado(contagens, n * esperadas)
    return FrequenciaDigitos(observados, possiveis, contagens / n, esperadas, teste)
