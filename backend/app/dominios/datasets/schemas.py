"""Contratos HTTP do domínio datasets (spec 14; nomes na visão geral do M1)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from app.compartilhado.tipos import OrigemTipo, TipoVariavel

type Celula = str | float | int | bool | None


class Modelo(BaseModel):
    """Base: aceita dataclasses do domínio via atributos."""

    model_config = ConfigDict(from_attributes=True)


class Aviso(Modelo):
    codigo: str
    mensagem: str


class LinhaArquivo(Modelo):
    numero: int
    celulas: list[str]


class MetadadosLeitura(Modelo):
    formato: Literal["txt", "csv", "tsv", "xlsx", "json"]
    codificacao: str | None
    separador: str | None
    decimal: str | None
    linha_cabecalho: int | None
    n_linhas: int
    n_colunas: int
    abas: list[str]
    avisos: list[Aviso]
    motivos: dict[str, str]
    linhas_iniciais: list[LinhaArquivo]


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


class PedidoLeitura(Modelo):
    """Opções que sobrescrevem a detecção; vazio = detectar tudo de novo (spec 01)."""

    separador: str | None = None
    decimal: Literal[",", "."] | None = None
    codificacao: str | None = None
    aba: str | None = None
    linha_cabecalho: int | None = Field(default=None, ge=0)


class ResumoDataset(Modelo):
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    n_linhas: int
    n_linhas_original: int
    n_colunas: int
    log_limpeza: list[EntradaLog]
    opcoes_leitura: PedidoLeitura
    tem_ajustes: bool


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


class Limites(Modelo):
    min: float | None = None
    max: float | None = None


LIMITES_POR_COLUNA = TypeAdapter(dict[str, Limites])


class ValoresSugeridos(Modelo):
    media: float | None
    mediana: float | None
    moda: Celula


class FaltantesColuna(Modelo):
    coluna: str
    n: int
    linhas: list[int]
    sugeridos: ValoresSugeridos


class GrupoDuplicado(Modelo):
    linha_original: int
    copias: list[int]


class Ocorrencia(Modelo):
    linha: int
    valor: Celula


class ForaDeFaixaColuna(Modelo):
    coluna: str
    limite_inferior: float
    limite_superior: float
    origem: Literal["iqr", "usuario"]
    ocorrencias: list[Ocorrencia]


class Grafia(Modelo):
    texto: str
    n: int


class GrupoGrafias(Modelo):
    forma_preferida: str
    variacoes: list[Grafia]


class InconsistenciaColuna(Modelo):
    coluna: str
    grupos: list[GrupoGrafias]


class TipoMistoColuna(Modelo):
    coluna: str
    ocorrencias: list[Ocorrencia]


class Diagnostico(Modelo):
    n_linhas: int
    faltantes: list[FaltantesColuna]
    duplicados: list[GrupoDuplicado]
    fora_de_faixa: list[ForaDeFaixaColuna]
    inconsistencias: list[InconsistenciaColuna]
    tipo_misto: list[TipoMistoColuna]


type Problema = Literal["faltantes", "duplicados", "fora_de_faixa", "inconsistencia", "tipo_misto"]
type Acao = Literal[
    "manter",
    "remover_linhas",
    "preencher_media",
    "preencher_mediana",
    "preencher_moda",
    "preencher_valor",
    "remover",
    "limitar",
    "marcar_faltante",
    "unificar",
]


class AcaoLimpeza(BaseModel):
    problema: Problema
    acao: Acao
    coluna: str | None = None
    valor: Celula = None
    limites: Limites | None = None
    grupo: str | None = None


class PedidoLimpeza(BaseModel):
    acoes: list[AcaoLimpeza]


class ResultadoLimpeza(Modelo):
    log: list[EntradaLog]
    n_linhas: int
    n_linhas_original: int
    colunas: list[TipoColuna]
