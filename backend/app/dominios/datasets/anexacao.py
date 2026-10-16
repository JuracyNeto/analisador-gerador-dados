"""Linhas vindas de fora (dados gerados) anexadas à versão atual (D111)."""

from datetime import datetime

import pandas as pd

from app.dominios.datasets.modelos import EntradaLog

PROBLEMA_ANEXAR = "anexar"
ACAO_ANEXAR = "anexar_gerados"
MAX_EXEMPLOS = 5


def _no_formato(alvo: pd.Series, novos: pd.Series, decimal: str | None) -> pd.Series:
    """Mesma representação da coluna: número se ela foi lida como número; senão texto."""
    if pd.api.types.is_numeric_dtype(alvo):
        return pd.to_numeric(novos)
    if pd.api.types.is_numeric_dtype(novos):
        separador = decimal or "."
        return novos.map(lambda v: str(v).replace(".", separador))
    return novos.astype(str)


def _proximo_indice(atual: pd.DataFrame) -> int:
    if len(atual) and pd.api.types.is_integer_dtype(atual.index):
        return int(atual.index.max()) + 1
    return len(atual) + 1


def preparar_linhas(atual: pd.DataFrame, linhas: pd.DataFrame, decimal: str | None) -> pd.DataFrame:
    """Linhas com o formato das colunas e índices depois da última linha atual."""
    inicio = _proximo_indice(atual)
    convertidas = pd.DataFrame(
        {coluna: _no_formato(atual[coluna], linhas[coluna], decimal) for coluna in linhas.columns}
    )
    convertidas.index = pd.RangeIndex(inicio, inicio + len(linhas))
    return convertidas


def entrada_anexacao(novas: pd.DataFrame, frase: str, quando: datetime) -> EntradaLog:
    colunas = list(novas.columns)
    primeira = novas[colunas[0]].head(MAX_EXEMPLOS)
    return EntradaLog(
        problema=PROBLEMA_ANEXAR,
        acao=ACAO_ANEXAR,
        coluna=colunas[0] if len(colunas) == 1 else None,
        linhas_afetadas=tuple(int(i) for i in novas.index),
        antes_exemplo="",
        depois_exemplo=", ".join(str(v) for v in primeira),
        quando=quando,
        frase=frase,
    )
