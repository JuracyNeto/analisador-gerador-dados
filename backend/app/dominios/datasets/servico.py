"""Fachada do domínio datasets: casos de uso de importação, consulta e tipos (D54)."""

import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Literal

import pandas as pd

from app.compartilhado.tipos import TIPOS_NUMERICOS, OrigemTipo, TipoVariavel
from app.core.config import Configuracao, obter_configuracao
from app.core.erros import ErroAplicacao
from app.dominios.datasets import erros
from app.dominios.datasets.ajuste_tipo import ajustar_tipo
from app.dominios.datasets.classificacao import (
    ColunaLida,
    Limiares,
    classificar,
    classificar_tabela,
    descrever,
    ler_coluna,
)
from app.dominios.datasets.diagnostico import Diagnostico, Limites, diagnosticar
from app.dominios.datasets.leitura import ler_arquivo
from app.dominios.datasets.limpeza import AcaoLimpeza, aplicar_acoes
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
    "AcaoLimpeza",
    "ColunaAnalise",
    "Diagnostico",
    "Importacao",
    "Limites",
    "OpcoesLeitura",
    "PaginaDataset",
    "ResultadoLimpeza",
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


@dataclass(frozen=True, slots=True)
class ResultadoLimpeza:
    log: tuple[EntradaLog, ...]
    n_linhas: int
    n_linhas_original: int
    colunas: tuple[TipoColuna, ...]


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

    def diagnosticar(self, dataset_id: str, limites: Mapping[str, Limites]) -> Diagnostico:
        """Problemas da versão atual; não altera nada (spec 03)."""
        dataset = self.obter(dataset_id)
        return diagnosticar(dataset.atual, dataset.tipos, dataset.metadados.decimal, limites)

    def limpar(self, dataset_id: str, acoes: list[AcaoLimpeza]) -> ResultadoLimpeza:
        """Aplica as ações sobre a versão atual; o original nunca muda."""
        dataset = self.obter(dataset_id)
        decimal = dataset.metadados.decimal
        resultado = aplicar_acoes(dataset.atual, dataset.tipos, decimal, acoes, datetime.now())
        dataset.atual = resultado.dados
        dataset.log_limpeza.extend(resultado.log)
        self._reclassificar(dataset, resultado.colunas_alteradas)
        return self._resultado_limpeza(dataset)

    def desfazer_limpeza(self, dataset_id: str) -> ResultadoLimpeza:
        """ "Desfazer tudo": a versão atual volta a ser o original e o log é zerado."""
        dataset = self.obter(dataset_id)
        dataset.atual = dataset.original.copy()
        dataset.log_limpeza.clear()
        self._reclassificar(dataset, list(dataset.tipos))
        return self._resultado_limpeza(dataset)

    def _reclassificar(self, dataset: Dataset, colunas: Iterable[str]) -> None:
        for nome in colunas:
            lida = self._coluna_lida(dataset, nome)
            dataset.tipos[nome] = _tipo_atualizado(lida, dataset.tipos[nome])

    @staticmethod
    def _resultado_limpeza(dataset: Dataset) -> ResultadoLimpeza:
        return ResultadoLimpeza(
            log=tuple(dataset.log_limpeza),
            n_linhas=len(dataset.atual),
            n_linhas_original=len(dataset.original),
            colunas=tuple(dataset.tipos.values()),
        )


def _tipo_atualizado(lida: ColunaLida, anterior: TipoColuna) -> TipoColuna:
    """Automáticas são reclassificadas; manuais mantêm o tipo se ainda for válido (spec 03)."""
    if anterior.origem == OrigemTipo.MANUAL:
        try:
            return ajustar_tipo(lida, anterior.tipo, list(anterior.categorias_ordem) or None)
        except ErroAplicacao:
            pass
    return descrever(lida, classificar(lida), OrigemTipo.AUTO)


@lru_cache
def obter_servico_datasets() -> ServicoDatasets:
    """Instância única (repositório em memória compartilhado entre requisições)."""
    config = obter_configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)
