"""Fachada do detector (spec 12): monta a tabela da versão atual e roda as regras pedidas."""

from collections.abc import Collection

from app.compartilhado.datas import reconhecer_datas
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ColunaAnalise, ServicoDatasets
from app.dominios.detector.registro import regras_pedidas
from app.dominios.detector.resultados import ResultadoDetector
from app.dominios.detector.resumo import montar_resultado
from app.dominios.detector.tabela import (
    ColunaDetector,
    TabelaDetector,
    coluna_detector,
    montar_tabela,
)

__all__ = ["ResultadoDetector", "ServicoDetector"]


def _coluna(analise: ColunaAnalise) -> ColunaDetector:
    """Converte a coluna da versão atual; datas só nas colunas do tipo data (R6)."""
    leitura = reconhecer_datas(analise.textos) if analise.tipo == TipoVariavel.DATA else None
    datas = leitura.valores if leitura is not None else None
    return coluna_detector(analise.nome, analise.tipo, analise.numeros, analise.textos, datas)


class ServicoDetector:
    """Casos de uso do detector; os dados vêm da fachada de datasets.

    A análise entra no M3.3 (R10 usa G₁ e G₂ de `ServicoAnalise.resumo_numerico`).
    """

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
        return montar_resultado([regra.executar(tabela) for regra in regras_pedidas(regras)])
