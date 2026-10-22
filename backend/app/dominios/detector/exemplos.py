"""Exemplo concreto de cada aviso: linhas e valores (spec 16, parte 5)."""

from collections.abc import Sequence

import numpy as np

from app.dominios.detector import textos
from app.dominios.detector.resultados import ExemploAviso

MAX_LINHAS_EXEMPLO = 20
MAX_LINHAS_BLOCO = 194
"""Um bloco seguido vai inteiro até 194 linhas: com as 3 de contexto de cada lado, o "Ver na
tabela" o busca num pedido só (a API devolve até 200 linhas; D172)."""
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


def exemplo_de_textos(
    linhas: Sequence[int] | np.ndarray, valores: Sequence[str], maximo: int = MAX_LINHAS_EXEMPLO
) -> ExemploAviso:
    """Até `maximo` linhas com os valores já escritos; `total_linhas` conta todas."""
    numeros = tuple(int(linha) for linha in linhas[:maximo])
    escritos = tuple(valores[:maximo])
    return ExemploAviso(numeros, escritos, textos.texto_exemplo(numeros, escritos), len(linhas))


def exemplo_de_valores(
    linhas: np.ndarray, valores: np.ndarray, maximo: int = MAX_LINHAS_EXEMPLO
) -> ExemploAviso:
    """Até `maximo` linhas com os valores no formato pt-BR."""
    escritos = [textos.valor(float(v)) for v in valores[:maximo]]
    return exemplo_de_textos(linhas, escritos, maximo)


def exemplo_do_bloco(linhas: np.ndarray, valores: np.ndarray) -> ExemploAviso:
    """Linhas seguidas (R1, R2): o bloco inteiro, até 194 linhas, como o resumo o cita."""
    return exemplo_de_valores(linhas, valores, MAX_LINHAS_BLOCO)


def exemplo_do_trecho(linhas: np.ndarray, valores: np.ndarray, marcas: np.ndarray) -> ExemploAviso:
    """O trecho do arquivo onde as marcas se concentram ("Linhas 120 a 138: 70, 75…")."""
    trecho = trecho_concentrado(marcas)
    return exemplo_de_valores(linhas[trecho], valores[trecho])
