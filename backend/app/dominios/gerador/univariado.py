"""Geração univariada: uma estratégia por tipo de variável (tabela de despacho, spec 11)."""

import numpy as np

from app.compartilhado.tipos import TipoVariavel
from app.dominios.gerador.estrategias.base import (
    EntradaEstrategia,
    Estrategia,
    ResultadoEstrategia,
)
from app.dominios.gerador.estrategias.categorica import Binaria, Categorica
from app.dominios.gerador.estrategias.continua import Continua
from app.dominios.gerador.estrategias.discreta import Discreta

ESTRATEGIAS: dict[TipoVariavel, Estrategia] = {
    TipoVariavel.CONTINUA: Continua(),
    TipoVariavel.DISCRETA: Discreta(),
    TipoVariavel.BINARIA: Binaria(),
    TipoVariavel.NOMINAL: Categorica(),
    TipoVariavel.ORDINAL: Categorica(),
}
TIPOS_GERAVEIS = frozenset(ESTRATEGIAS)
TIPOS_SO_PRESERVAR = frozenset({TipoVariavel.NOMINAL, TipoVariavel.ORDINAL})


def gerar_univariado(
    tipo: TipoVariavel, entrada: EntradaEstrategia, semente: int
) -> ResultadoEstrategia:
    """Mesma semente e mesmo pedido → mesmos valores."""
    return ESTRATEGIAS[tipo].gerar(entrada, np.random.default_rng(semente))
