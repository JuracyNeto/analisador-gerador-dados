"""Conteúdo do mini relatório já em texto (spec 13); a montagem só encaixa no template."""

from dataclasses import dataclass
from typing import Literal

type Secao = Literal["leitura", "tipos", "limpeza", "analises", "distribuicoes", "bivariada"]

SECOES_PADRAO: tuple[Secao, ...] = (
    "leitura",
    "tipos",
    "limpeza",
    "analises",
    "distribuicoes",
    "bivariada",
)


@dataclass(frozen=True, slots=True)
class DadosLeitura:
    formato: str
    separador: str | None
    decimal: str | None
    codificacao: str | None
    linha_cabecalho: int | None
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
    nota: str | None = None


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
class BlocoAnalises:
    """Frequências, medidas, separatrizes, figura principal e interpretações (seção analises)."""

    cabecalho_tabela: tuple[str, ...]
    linhas_tabela: tuple[tuple[str, ...], ...]
    medidas: tuple[ItemMedida, ...]
    separatrizes: str | None
    interpretacoes: tuple[str, ...]
    figura: FiguraRelatorio | None


@dataclass(frozen=True, slots=True)
class SecaoForma:
    """Assimetria, curtose, ajustes e a 1ª figura da forma (seção distribuicoes)."""

    medidas: tuple[ItemMedida, ...] = ()
    ajustes: tuple[str, ...] = ()
    interpretacao: str | None = None
    figura: FiguraRelatorio | None = None
    motivo: str | None = None


@dataclass(frozen=True, slots=True)
class SecaoColuna:
    """Cada bloco só aparece com a sua caixa marcada na tela 8."""

    coluna: str
    tipo: str
    n: int
    n_faltantes: int
    analises: BlocoAnalises | None
    forma: SecaoForma | None
    formulas: tuple[FormulaTexto, ...]


@dataclass(frozen=True, slots=True)
class ParRelatorio:
    x: str
    y: str
    medidas: tuple[ItemMedida, ...]
    equacao: str
    interpretacoes: tuple[str, ...]
    figura: FiguraRelatorio | None


@dataclass(frozen=True, slots=True)
class SecaoBivariada:
    """Matriz de correlação e os pares mais fortes (|r| ≥ 0,3)."""

    matriz: FiguraRelatorio | None
    resumo: str
    pares: tuple[ParRelatorio, ...]
    vazio: str | None
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
    bivariada: SecaoBivariada | None = None
