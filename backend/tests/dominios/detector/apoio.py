"""Montagem de tabelas do detector para os testes (linhas numeradas a partir de 1)."""

from collections.abc import Mapping, Sequence
from dataclasses import replace

import numpy as np
import pandas as pd
from scipy import stats

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.detector.servico import forma_da_coluna
from app.dominios.detector.tabela import TabelaDetector, coluna_detector, montar_tabela


def _textos(serie: pd.Series) -> pd.Series:
    return serie.map(lambda v: None if pd.isna(v) else str(v))


def tabela_de(dados: pd.DataFrame, tipos: Mapping[str, TipoVariavel]) -> TabelaDetector:
    """Tabela a partir de um DataFrame, como o serviço monta; as linhas viram 1, 2, 3…"""
    numerado = dados.set_axis(pd.RangeIndex(1, len(dados) + 1), axis="index")
    colunas = []
    for nome, tipo in tipos.items():
        serie = numerado[nome]
        numeros = pd.to_numeric(serie, errors="coerce") if tipo in TIPOS_NUMERICOS else None
        datas = pd.to_datetime(serie, errors="coerce") if tipo == TipoVariavel.DATA else None
        coluna = coluna_detector(nome, tipo, numeros, _textos(serie), datas)
        if tipo == TipoVariavel.CONTINUA and numeros is not None:
            coluna = replace(coluna, forma=forma_da_coluna(numeros))
        colunas.append(coluna)
    return montar_tabela(numerado.index, colunas)


def tabela_numerica(
    valores: Sequence[float], tipo: TipoVariavel = TipoVariavel.CONTINUA, nome: str = "x"
) -> TabelaDetector:
    """Tabela com uma coluna numérica só."""
    return tabela_de(pd.DataFrame({nome: list(valores)}), {nome: tipo})


def chuva(dias: int, com_chuva: int) -> np.ndarray:
    """Dias sem chuva (zero) e, espalhados, quantis da Gama(0,7; 15) no pluviômetro de 0,2 mm."""
    milimetros = stats.gamma.ppf((np.arange(1, com_chuva + 1) - 0.5) / com_chuva, 0.7, scale=15)
    valores = np.zeros(dias)
    dias_de_chuva = np.linspace(0, dias - 1, com_chuva).round().astype(int)
    valores[dias_de_chuva] = np.maximum(np.round(milimetros / 0.2) * 0.2, 0.2)
    return np.round(valores, 1)
