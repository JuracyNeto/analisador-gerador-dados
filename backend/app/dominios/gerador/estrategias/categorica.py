"""Binária (Bernoulli) e nominal/ordinal (sorteio pelas frequências observadas), spec 11."""

import numpy as np
import pandas as pd

from app.dominios.gerador.estrategias.base import EntradaEstrategia, ResultadoEstrategia


class Binaria:
    """Bernoulli(p̂) com os rótulos do original, ou Bernoulli(p) com novos parâmetros."""

    def gerar(self, entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        fracasso, sucesso = entrada.rotulos or ("0", "1")
        p = self._chance(entrada, sucesso)
        sorteados = np.where(rng.random(entrada.x) < p, sucesso, fracasso)
        return ResultadoEstrategia(pd.Series(sorteados, dtype="object"), "bernoulli")

    @staticmethod
    def _chance(entrada: EntradaEstrategia, sucesso: str) -> float:
        if entrada.modo == "parametros" or entrada.originais is None:
            return float(entrada.p or 0.0)
        return float((entrada.originais.astype(str) == sucesso).mean())


class Categorica:
    """Sorteio com as frequências relativas observadas (só preservar)."""

    def gerar(self, entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        originais = (
            entrada.originais if entrada.originais is not None else pd.Series(dtype="object")
        )
        frequencias = originais.astype(str).value_counts(normalize=True, sort=False)
        sorteados = rng.choice(frequencias.index.to_numpy(), entrada.x, p=frequencias.to_numpy())
        return ResultadoEstrategia(pd.Series(sorteados, dtype="object"), "frequencias")
