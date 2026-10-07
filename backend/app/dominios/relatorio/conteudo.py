"""Conteúdo do mini relatório já em texto (spec 13); a montagem só encaixa no template."""

from dataclasses import dataclass
from typing import Literal

type Secao = Literal["leitura", "tipos", "limpeza", "analises"]

SECOES_M1: tuple[Secao, ...] = ("leitura", "tipos", "limpeza", "analises")


@dataclass(frozen=True, slots=True)
class DadosLeitura:
    formato: str
    separador: str | None
    decimal: str | None
    codificacao: str | None
    tem_cabecalho: bool | None
    n_linhas: int
    n_colunas: int


@dataclass(frozen=True, slots=True)
class LinhaTipo:
    coluna: str
    tipo: str
    motivo: str


@dataclass(frozen=True, slots=True)
class ItemMedida:
    rotulo: str
    valor: str


@dataclass(frozen=True, slots=True)
class FormulaTexto:
    nome: str
    latex: str
    texto: str


@dataclass(frozen=True, slots=True)
class FiguraRelatorio:
    titulo: str
    resumo: str
    html: str


@dataclass(frozen=True, slots=True)
class SecaoColuna:
    coluna: str
    tipo: str
    n: int
    n_faltantes: int
    cabecalho_tabela: tuple[str, ...]
    linhas_tabela: tuple[tuple[str, ...], ...]
    medidas: tuple[ItemMedida, ...]
    separatrizes: str | None
    interpretacoes: tuple[str, ...]
    figura: FiguraRelatorio | None
    formulas: tuple[FormulaTexto, ...]


@dataclass(frozen=True, slots=True)
class ConteudoRelatorio:
    nome_arquivo: str
    gerado_em: str
    subtitulo: str
    script_plotly: str
    leitura: str | None = None
    tipos: tuple[LinhaTipo, ...] | None = None
    limpeza: tuple[str, ...] | None = None
    colunas: tuple[SecaoColuna, ...] | None = None
