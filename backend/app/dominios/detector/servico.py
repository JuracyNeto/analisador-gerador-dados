"""Fachada do detector (spec 12): monta a tabela da versão atual e roda as regras pedidas."""

from collections.abc import Collection
from dataclasses import replace

import numpy as np
import pandas as pd

from app.compartilhado.datas import reconhecer_datas
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ColunaAnalise, ServicoDatasets
from app.dominios.detector.registro import regras_pedidas
from app.dominios.detector.resultados import (
    Aviso,
    Grafico,
    GraficoBlocos,
    GraficoDigitos,
    ResultadoDetector,
)
from app.dominios.detector.resumo import montar_resultado
from app.dominios.detector.tabela import (
    ColunaDetector,
    FormaColuna,
    TabelaDetector,
    coluna_detector,
    montar_tabela,
)
from app.dominios.graficos.servico import (
    DadosBlocos,
    DadosDigitos,
    FiguraPronta,
    figura_benford,
    figura_blocos,
    figura_ultimo_digito,
)

__all__ = ["ResultadoDetector", "ServicoDetector", "forma_da_coluna"]

MINIMO_FORMA = 4
"""A curtose (G₂) precisa de 4 valores."""


def forma_da_coluna(numeros: pd.Series) -> FormaColuna | None:
    """G₁, G₂ e o teste de normalidade com as fórmulas da análise (R10; D108)."""
    valores = numeros.dropna().to_numpy(dtype="float64")
    if len(valores) < MINIMO_FORMA or np.ptp(valores) == 0:
        return None
    resumo = ServicoAnalise.resumo_numerico(valores)
    if resumo.assimetria is None or resumo.curtose is None:
        return None
    teste = ServicoAnalise.teste_normalidade(valores)
    return FormaColuna(resumo.assimetria, resumo.curtose, teste.nome, teste.p_valor)


def _coluna(analise: ColunaAnalise) -> ColunaDetector:
    """Converte a coluna da versão atual; datas nas colunas de data (R6), forma nas contínuas."""
    leitura = reconhecer_datas(analise.textos) if analise.tipo == TipoVariavel.DATA else None
    datas = leitura.valores if leitura is not None else None
    coluna = coluna_detector(analise.nome, analise.tipo, analise.numeros, analise.textos, datas)
    if analise.tipo != TipoVariavel.CONTINUA or analise.numeros is None:
        return coluna
    return replace(coluna, forma=forma_da_coluna(analise.numeros))


FIGURAS_DIGITOS = {"primeiro": figura_benford, "ultimo": figura_ultimo_digito}


def _figura_digitos(grafico: GraficoDigitos) -> FiguraPronta:
    dados = DadosDigitos(grafico.coluna, grafico.digitos, grafico.observadas, grafico.esperadas)
    return FIGURAS_DIGITOS[grafico.posicao](dados)


def _figura_blocos(grafico: GraficoBlocos) -> FiguraPronta:
    inicio, fim, media_alinhada = grafico.alinhado
    media, desvio = grafico.geral
    return figura_blocos(
        DadosBlocos(
            grafico.coluna,
            grafico.tamanho,
            grafico.linhas_do_meio,
            grafico.medias,
            media,
            desvio,
            (inicio, fim),
            media_alinhada,
        )
    )


def _figura(grafico: Grafico) -> FiguraPronta:
    """Pede ao domínio graficos a figura dos dados que a regra deixou no aviso (D123)."""
    if isinstance(grafico, GraficoBlocos):
        return _figura_blocos(grafico)
    return _figura_digitos(grafico)


def _com_figura(aviso: Aviso) -> Aviso:
    return aviso if aviso.grafico is None else replace(aviso, figura=_figura(aviso.grafico))


class ServicoDetector:
    """Casos de uso do detector; os dados vêm da fachada de datasets."""

    def __init__(self, datasets: ServicoDatasets, analise: ServicoAnalise) -> None:
        self._datasets = datasets
        self._analise = analise

    def tabela(self, dataset_id: str) -> TabelaDetector:
        """Entrada pura das regras: todas as colunas da versão atual, na ordem do arquivo."""
        colunas = [
            self._datasets.coluna_para_analise(dataset_id, tipo.coluna)
            for tipo in self._datasets.colunas(dataset_id)
        ]
        return montar_tabela(colunas[0].textos.index, [_coluna(coluna) for coluna in colunas])

    def analisar(self, dataset_id: str, regras: Collection[str] | None = None) -> ResultadoDetector:
        """Roda as regras pedidas (sem códigos, todas) e monta o resumo da tela 7."""
        tabela = self.tabela(dataset_id)
        resultado = montar_resultado([regra.executar(tabela) for regra in regras_pedidas(regras)])
        return replace(resultado, avisos=tuple(_com_figura(aviso) for aviso in resultado.avisos))
