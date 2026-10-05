"""Fachada do domínio datasets: casos de uso de importação, consulta e tipos (D54)."""

import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import pandas as pd

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.core.config import Configuracao, obter_configuracao
from app.dominios.datasets import erros
from app.dominios.datasets.ajuste_tipo import ajustar_tipo
from app.dominios.datasets.classificacao import (
    ColunaLida,
    Limiares,
    classificar_tabela,
    ler_coluna,
)
from app.dominios.datasets.leitura import ler_arquivo
from app.dominios.datasets.modelos import (
    Dataset,
    EntradaLog,
    LinhaDados,
    MetadadosLeitura,
    OpcoesLeitura,
    TipoColuna,
)
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.tabela import linhas_dados, paginar

__all__ = [
    "ColunaAnalise",
    "Importacao",
    "OpcoesLeitura",
    "PaginaDataset",
    "Resumo",
    "ServicoDatasets",
    "obter_servico_datasets",
]

type Versao = Literal["atual", "original"]


@dataclass(frozen=True, slots=True)
class Importacao:
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    previa: tuple[LinhaDados, ...]
    colunas: tuple[TipoColuna, ...]


@dataclass(frozen=True, slots=True)
class Resumo:
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    n_linhas: int
    n_linhas_original: int
    n_colunas: int
    log_limpeza: tuple[EntradaLog, ...]


@dataclass(frozen=True, slots=True)
class PaginaDataset:
    resumo: Resumo
    versao: Versao
    pagina: int
    tamanho: int
    total_paginas: int
    linhas: tuple[LinhaDados, ...]


@dataclass(frozen=True, slots=True, eq=False)
class ColunaAnalise:
    """O que o domínio analise precisa de uma coluna: tipo, números ou textos e a ordem."""

    nome: str
    tipo: TipoVariavel
    numeros: pd.Series | None
    textos: pd.Series
    categorias_ordem: tuple[str, ...]


class ServicoDatasets:
    """Casos de uso sobre datasets em memória (ADR 0004)."""

    def __init__(self, repositorio: RepositorioDatasets, config: Configuracao) -> None:
        self._repositorio = repositorio
        self._config = config

    @property
    def limiares(self) -> Limiares:
        return Limiares(
            discreta=self._config.limiar_discreta,
            unicos_identificador=self._config.limiar_unicos_identificador,
            numerico=self._config.limiar_numerico,
        )

    def importar(self, conteudo: bytes, nome_arquivo: str, opcoes: OpcoesLeitura) -> Importacao:
        """Lê o arquivo, classifica as colunas e guarda o dataset."""
        if len(conteudo) > self._config.limite_arquivo_bytes:
            raise erros.arquivo_grande(self._config.limite_arquivo_mb)
        leitura = ler_arquivo(conteudo, nome_arquivo, opcoes)
        tipos = classificar_tabela(leitura.dados, leitura.metadados.decimal, self.limiares)
        dataset = Dataset(
            id=uuid.uuid4().hex,
            nome_arquivo=nome_arquivo,
            metadados=leitura.metadados,
            original=leitura.dados,
            atual=leitura.dados.copy(),
            tipos=tipos,
        )
        self._repositorio.adicionar(dataset)
        previa = linhas_dados(dataset.atual.head(self._config.tamanho_previa))
        return Importacao(
            dataset.id, nome_arquivo, dataset.metadados, previa, tuple(tipos.values())
        )

    def importar_exemplo(self) -> Importacao:
        """Importa o arquivo de demonstração de dados-exemplo/ (D52)."""
        caminho = self._config.pasta_exemplos / self._config.arquivo_exemplo
        return self.importar(caminho.read_bytes(), caminho.name, OpcoesLeitura())

    def obter(self, dataset_id: str) -> Dataset:
        return self._repositorio.obter(dataset_id)

    def remover(self, dataset_id: str) -> None:
        self._repositorio.remover(dataset_id)

    def resumo(self, dataset_id: str) -> Resumo:
        dataset = self.obter(dataset_id)
        return Resumo(
            dataset_id=dataset.id,
            nome_arquivo=dataset.nome_arquivo,
            metadados=dataset.metadados,
            n_linhas=len(dataset.atual),
            n_linhas_original=len(dataset.original),
            n_colunas=dataset.atual.shape[1],
            log_limpeza=tuple(dataset.log_limpeza),
        )

    def pagina(self, dataset_id: str, pagina: int, tamanho: int, versao: Versao) -> PaginaDataset:
        """Linhas paginadas da versão atual (após limpeza) ou original."""
        dataset = self.obter(dataset_id)
        dados = dataset.atual if versao == "atual" else dataset.original
        recorte = paginar(dados, pagina, tamanho)
        return PaginaDataset(
            self.resumo(dataset_id), versao, pagina, tamanho, recorte.total_paginas, recorte.linhas
        )

    def colunas(self, dataset_id: str) -> list[TipoColuna]:
        return list(self.obter(dataset_id).tipos.values())

    def _coluna_lida(self, dataset: Dataset, coluna: str) -> ColunaLida:
        if coluna not in dataset.tipos:
            raise erros.coluna_nao_encontrada(coluna)
        serie = dataset.atual[coluna]
        return ler_coluna(coluna, serie, dataset.metadados.decimal, self.limiares)

    def alterar_tipo(
        self,
        dataset_id: str,
        coluna: str,
        tipo: TipoVariavel,
        categorias_ordem: list[str] | None = None,
    ) -> TipoColuna:
        """Ajuste manual do tipo (spec 02); a escolha vale até o próximo ajuste."""
        dataset = self.obter(dataset_id)
        novo = ajustar_tipo(self._coluna_lida(dataset, coluna), tipo, categorias_ordem)
        dataset.tipos[coluna] = novo
        return novo

    def coluna_para_analise(self, dataset_id: str, coluna: str) -> ColunaAnalise:
        """Dados de uma coluna da versão atual, já convertidos conforme o tipo."""
        dataset = self.obter(dataset_id)
        lida = self._coluna_lida(dataset, coluna)
        tipo = dataset.tipos[coluna]
        numeros = lida.numeros if tipo.tipo in TIPOS_NUMERICOS else None
        return ColunaAnalise(coluna, tipo.tipo, numeros, lida.textos, tipo.categorias_ordem)


@lru_cache
def obter_servico_datasets() -> ServicoDatasets:
    """Instância única (repositório em memória compartilhado entre requisições)."""
    config = obter_configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)
