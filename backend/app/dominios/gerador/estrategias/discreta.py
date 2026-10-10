"""Discreta (spec 11): Poisson ou sorteio empírico; com novos parâmetros, Normal arredondada."""

import numpy as np

from app.dominios.gerador.estrategias.base import (
    EntradaEstrategia,
    ResultadoEstrategia,
    como_serie,
    numeros,
)
from app.dominios.gerador.reescala import limitar_faixa, reescalar, resortear_fora

LIMIAR_POISSON = 0.2  # |x̄ − s²| / x̄ < 0,2: média e variância parecidas, como na Poisson


def parece_poisson(originais: np.ndarray) -> bool:
    """Spec 11: média positiva e |x̄ − s²| / x̄ < 0,2."""
    media = float(originais.mean())
    if media <= 0:
        return False
    return abs(media - float(originais.var(ddof=1))) / media < LIMIAR_POISSON


def _empirica(originais: np.ndarray, rng: np.random.Generator, quantidade: int) -> np.ndarray:
    valores, contagens = np.unique(originais, return_counts=True)
    return rng.choice(valores, quantidade, p=contagens / contagens.sum())


class Discreta:
    """Valores inteiros; com origem sem negativos, o resultado também não tem negativos."""

    def gerar(self, entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        if entrada.modo == "parametros":
            return self._parametros(entrada, rng)
        return self._preservar(entrada, rng)

    @staticmethod
    def _preservar(entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        originais = numeros(entrada.originais)
        if not parece_poisson(originais):
            return ResultadoEstrategia(
                como_serie(_empirica(originais, rng, entrada.x), 0), "empirica"
            )
        media = float(originais.mean())
        valores = rng.poisson(media, entrada.x).astype("float64")
        recortou = False
        if entrada.limitar_faixa:
            valores, recortou = resortear_fora(
                lambda quantidade: rng.poisson(media, quantidade).astype("float64"),
                valores,
                float(originais.min()),
                float(originais.max()),
            )
        return ResultadoEstrategia(como_serie(valores, 0), "poisson", recortou)

    @staticmethod
    def _parametros(entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        alvo = (float(entrada.media or 0.0), float(entrada.desvio or 0.0))
        valores = reescalar(rng.normal(*alvo, entrada.x), *alvo)
        originais = numeros(entrada.originais)
        recortou = False
        if entrada.limitar_faixa and len(originais):
            valores, recortou = limitar_faixa(
                lambda quantidade: rng.normal(*alvo, quantidade),
                valores,
                float(originais.min()),
                float(originais.max()),
                alvo,
            )
        if len(originais) and float(originais.min()) >= 0:
            valores = np.maximum(valores, 0)
        return ResultadoEstrategia(como_serie(valores, 0), "normal_inteira", recortou)
