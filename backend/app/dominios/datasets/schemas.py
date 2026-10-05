"""Contratos HTTP do domínio datasets (spec 14; nomes na visão geral do M1)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.compartilhado.tipos import OrigemTipo, TipoVariavel

type Celula = str | float | int | bool | None


class Modelo(BaseModel):
    """Base: aceita dataclasses do domínio via atributos."""

    model_config = ConfigDict(from_attributes=True)


class Aviso(Modelo):
    codigo: str
    mensagem: str


class MetadadosLeitura(Modelo):
    formato: Literal["txt", "csv", "tsv", "xlsx", "json"]
    codificacao: str | None
    separador: str | None
    decimal: str | None
    tem_cabecalho: bool | None
    n_linhas: int
    n_colunas: int
    abas: list[str]
    avisos: list[Aviso]
    motivos: dict[str, str]


class TipoColuna(Modelo):
    coluna: str
    tipo: TipoVariavel
    motivo: str
    origem: OrigemTipo
    n_validos: int
    n_faltantes: int
    n_distintos: int
    exemplos: list[str]
    categorias_ordem: list[str]
    contagens: dict[str, int]


class LinhaDados(Modelo):
    linha: int
    valores: dict[str, Celula]


class DatasetCriado(Modelo):
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    previa: list[LinhaDados]
    colunas: list[TipoColuna]


class EntradaLog(Modelo):
    problema: str
    acao: str
    coluna: str | None
    linhas_afetadas: list[int]
    antes_exemplo: str
    depois_exemplo: str
    quando: datetime
    frase: str


class ResumoDataset(Modelo):
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    n_linhas: int
    n_linhas_original: int
    n_colunas: int
    log_limpeza: list[EntradaLog]


class PaginaDataset(Modelo):
    resumo: ResumoDataset
    versao: Literal["atual", "original"]
    pagina: int
    tamanho: int
    total_paginas: int
    linhas: list[LinhaDados]


class AlteracaoTipo(BaseModel):
    tipo: TipoVariavel
    categorias_ordem: list[str] | None = None
