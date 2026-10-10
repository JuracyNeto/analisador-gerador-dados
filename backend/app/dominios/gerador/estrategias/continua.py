"""Contínua (spec 11): Normal ou KDE preservando média e desvio, ou Normal com novos parâmetros."""

from collections.abc import Callable

import numpy as np
from scipy import stats

from app.dominios.gerador.estrategias.base import (
    EntradaEstrategia,
    Metodo,
    ResultadoEstrategia,
    como_serie,
    numeros,
)
from app.dominios.gerador.reescala import limitar_faixa, reescalar

type Sorteio = Callable[[int], np.ndarray]


def _normal(media: float, desvio: float, rng: np.random.Generator) -> Sorteio:
    return lambda quantidade: rng.normal(media, desvio, quantidade)


def _kde(originais: np.ndarray, rng: np.random.Generator) -> Sorteio:
    densidade = stats.gaussian_kde(originais)
    return lambda quantidade: densidade.resample(quantidade, seed=rng)[0]


def _sorteio(entrada: EntradaEstrategia, rng: np.random.Generator) -> tuple[Sorteio, Metodo]:
    if entrada.modo == "parametros" or entrada.normal_compativel:
        media, desvio = _alvo(entrada)
        return _normal(media, desvio, rng), "normal"
    return _kde(numeros(entrada.originais), rng), "kde"


def _alvo(entrada: EntradaEstrategia) -> tuple[float, float]:
    if entrada.modo == "parametros":
        return float(entrada.media or 0.0), float(entrada.desvio or 0.0)
    originais = numeros(entrada.originais)
    return float(originais.mean()), float(originais.std(ddof=1))


class Continua:
    """Sorteio + reescala exata (zᵢ = (gᵢ − ḡ)/s_g → x̄ + s·zᵢ) + casas do original."""

    def gerar(self, entrada: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia:
        sortear, metodo = _sorteio(entrada, rng)
        alvo = _alvo(entrada)
        valores = reescalar(sortear(entrada.x), *alvo)
        recortou = False
        if entrada.limitar_faixa:
            originais = numeros(entrada.originais)
            valores, recortou = limitar_faixa(
                sortear, valores, float(originais.min()), float(originais.max()), alvo
            )
        return ResultadoEstrategia(como_serie(valores, entrada.casas), metodo, recortou)
