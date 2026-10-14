"""Entrada pura das regras do detector: a tabela já convertida pelo serviço (D118)."""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel


@dataclass(frozen=True, slots=True, eq=False)
class ColunaDetector:
    """Uma coluna na ordem das linhas: números (NaN nos faltantes), textos e datas."""

    nome: str
    tipo: TipoVariavel
    numeros: np.ndarray | None
    textos: tuple[str | None, ...]
    datas: np.ndarray | None = None


@dataclass(frozen=True, slots=True, eq=False)
class TabelaDetector:
    """Versão atual do dataset: números das linhas (os da prévia) e as colunas."""

    n_linhas: int
    linhas: np.ndarray
    colunas: Mapping[str, ColunaDetector]

    def do_tipo(self, tipos: Collection[TipoVariavel]) -> tuple[ColunaDetector, ...]:
        return tuple(coluna for coluna in self.colunas.values() if coluna.tipo in tipos)

    def numericas(self) -> tuple[ColunaDetector, ...]:
        return self.do_tipo(TIPOS_NUMERICOS)

    def numeros(self, coluna: ColunaDetector) -> np.ndarray:
        """Números da coluna na ordem das linhas; sem números, tudo NaN."""
        if coluna.numeros is None:
            return np.full(self.n_linhas, np.nan)
        return coluna.numeros

    def valores_validos(self, coluna: ColunaDetector) -> tuple[np.ndarray, np.ndarray]:
        """Números das linhas com valor e os valores, na ordem do arquivo."""
        numeros = self.numeros(coluna)
        validos = ~np.isnan(numeros)
        return self.linhas[validos], numeros[validos]


def _textos(textos: pd.Series) -> tuple[str | None, ...]:
    return tuple(None if pd.isna(valor) else str(valor) for valor in textos.tolist())


def coluna_detector(
    nome: str,
    tipo: TipoVariavel,
    numeros: pd.Series | None,
    textos: pd.Series,
    datas: pd.Series | None = None,
) -> ColunaDetector:
    """Converte as séries da coluna (índice = linhas) em arrays na ordem das linhas."""
    return ColunaDetector(
        nome=nome,
        tipo=tipo,
        numeros=None if numeros is None else numeros.to_numpy(dtype="float64"),
        textos=_textos(textos),
        datas=None
        if datas is None
        else datas.reindex(textos.index).to_numpy(dtype="datetime64[ns]"),
    )


def montar_tabela(linhas: pd.Index, colunas: Sequence[ColunaDetector]) -> TabelaDetector:
    """Tabela com as linhas do dataset e as colunas na ordem dada."""
    return TabelaDetector(
        n_linhas=len(linhas),
        linhas=linhas.to_numpy(dtype="int64"),
        colunas={coluna.nome: coluna for coluna in colunas},
    )
