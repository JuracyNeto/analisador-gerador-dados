"""Conversão de linhas do DataFrame em células simples para a API (prévia e paginação)."""

import math
from dataclasses import dataclass
from datetime import date, time

import numpy as np
import pandas as pd

from app.compartilhado.datas import formatar_data
from app.dominios.datasets.modelos import Celula, LinhaDados


def celula(valor: object) -> Celula:
    """Valor de uma célula como tipo simples; faltante vira None."""
    if isinstance(valor, np.generic):
        valor = valor.item()
    if valor is pd.NaT:  # NaT também é um datetime
        return None
    if isinstance(valor, date | time):
        return formatar_data(valor)
    if isinstance(valor, float) and math.isnan(valor):
        return None
    if valor is None or valor is pd.NA:
        return None
    if isinstance(valor, str | int | float | bool):
        return valor
    return str(valor)


def linhas_dados(dados: pd.DataFrame) -> tuple[LinhaDados, ...]:
    """Linhas com o número original (índice) e os valores por coluna."""
    registros = dados.to_dict(orient="records")
    return tuple(
        LinhaDados(linha=int(numero), valores={str(c): celula(v) for c, v in valores.items()})
        for numero, valores in zip(dados.index.tolist(), registros, strict=True)
    )


@dataclass(frozen=True, slots=True)
class Pagina:
    linhas: tuple[LinhaDados, ...]
    pagina: int
    tamanho: int
    total_paginas: int


def paginar(dados: pd.DataFrame, pagina: int, tamanho: int) -> Pagina:
    """Recorte das linhas da página pedida (a 1ª página é 1)."""
    total_paginas = max(1, math.ceil(len(dados) / tamanho))
    inicio = (pagina - 1) * tamanho
    return Pagina(
        linhas_dados(dados.iloc[inicio : inicio + tamanho]), pagina, tamanho, total_paginas
    )
