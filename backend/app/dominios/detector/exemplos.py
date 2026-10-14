"""Exemplo concreto de cada aviso: linhas e valores (spec 16, parte 5)."""

from collections.abc import Sequence

import numpy as np

from app.dominios.detector import textos
from app.dominios.detector.resultados import ExemploAviso

MAX_LINHAS_EXEMPLO = 20
MAX_LACUNA = 2
"""Linhas sem o padrão que ainda deixam as marcadas no mesmo trecho."""


def trecho_concentrado(marcas: np.ndarray) -> slice:
    """Trecho com mais posições marcadas, aceitando até 2 sem marca entre elas."""
    posicoes = np.flatnonzero(marcas)
    if len(posicoes) == 0:
        return slice(0, 0)
    quebras = np.flatnonzero(np.diff(posicoes) > MAX_LACUNA + 1)
    inicios = np.concatenate(([0], quebras + 1))
    fins = np.concatenate((quebras, [len(posicoes) - 1]))
    melhor = int(np.argmax(fins - inicios))
    return slice(int(posicoes[inicios[melhor]]), int(posicoes[fins[melhor]]) + 1)


def exemplo_de_textos(linhas: Sequence[int] | np.ndarray, valores: Sequence[str]) -> ExemploAviso:
    """Até 20 linhas com os valores já escritos."""
    numeros = tuple(int(linha) for linha in linhas[:MAX_LINHAS_EXEMPLO])
    escritos = tuple(valores[:MAX_LINHAS_EXEMPLO])
    return ExemploAviso(numeros, escritos, textos.texto_exemplo(numeros, escritos))


def exemplo_de_valores(linhas: np.ndarray, valores: np.ndarray) -> ExemploAviso:
    """Até 20 linhas com os valores no formato pt-BR."""
    escritos = [textos.valor(float(v)) for v in valores[:MAX_LINHAS_EXEMPLO]]
    return exemplo_de_textos(linhas, escritos)


def exemplo_do_trecho(linhas: np.ndarray, valores: np.ndarray, marcas: np.ndarray) -> ExemploAviso:
    """O trecho do arquivo onde as marcas se concentram ("Linhas 120 a 138: 70, 75…")."""
    trecho = trecho_concentrado(marcas)
    return exemplo_de_valores(linhas[trecho], valores[trecho])
