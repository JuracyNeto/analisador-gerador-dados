"""Value objects do domínio datasets (specs 01–03, ADR 0004)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from app.compartilhado.tipos import OrigemTipo, TipoVariavel

type Celula = str | float | int | bool | None


@dataclass(frozen=True, slots=True)
class OpcoesLeitura:
    """Escolhas do usuário que sobrescrevem a detecção automática (spec 01)."""

    separador: str | None = None
    decimal: str | None = None
    codificacao: str | None = None
    aba: str | None = None
    linha_cabecalho: int | None = None
    """Nº da linha do cabeçalho no arquivo; 0 = sem cabeçalho."""


@dataclass(frozen=True, slots=True)
class Aviso:
    codigo: str
    mensagem: str


@dataclass(frozen=True, slots=True)
class LinhaArquivo:
    """Uma das primeiras linhas do arquivo como está escrita (vazia = sem células)."""

    numero: int
    celulas: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MetadadosLeitura:
    formato: str
    codificacao: str | None
    separador: str | None
    decimal: str | None
    linha_cabecalho: int | None
    n_linhas: int
    n_colunas: int
    abas: tuple[str, ...] = ()
    avisos: tuple[Aviso, ...] = ()
    motivos: Mapping[str, str] = field(default_factory=dict)
    linhas_iniciais: tuple[LinhaArquivo, ...] = ()


@dataclass(frozen=True, slots=True, eq=False)
class ResultadoLeitura:
    dados: pd.DataFrame
    metadados: MetadadosLeitura


@dataclass(frozen=True, slots=True)
class TipoColuna:
    """Resultado da classificação de uma coluna (spec 02)."""

    coluna: str
    tipo: TipoVariavel
    motivo: str
    origem: OrigemTipo
    n_validos: int
    n_faltantes: int
    n_distintos: int
    exemplos: tuple[str, ...] = ()
    categorias_ordem: tuple[str, ...] = ()
    contagens: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EntradaLog:
    """Uma ação de limpeza registrada para o usuário e para o relatório (spec 03)."""

    problema: str
    acao: str
    coluna: str | None
    linhas_afetadas: tuple[int, ...]
    antes_exemplo: str
    depois_exemplo: str
    quando: datetime
    frase: str


@dataclass(frozen=True, slots=True)
class LinhaDados:
    linha: int
    valores: Mapping[str, Celula]


@dataclass(slots=True, eq=False)
class Dataset:
    """Estado de um conjunto importado: original intocado e atual após a limpeza (ADR 0004)."""

    id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    original: pd.DataFrame
    atual: pd.DataFrame
    tipos: dict[str, TipoColuna]
    log_limpeza: list[EntradaLog] = field(default_factory=list)
    criado_em: datetime = field(default_factory=datetime.now)
