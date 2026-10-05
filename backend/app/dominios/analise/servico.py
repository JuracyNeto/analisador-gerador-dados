"""Fachada do domínio analise: análise univariada e "onde está meu valor?" (D54)."""

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import erros
from app.dominios.analise.posicao import calcular_posicao
from app.dominios.analise.resultados import Amostra, Analise, Posicao, TipoSeparatriz
from app.dominios.analise.univariada import analisar_amostra
from app.dominios.datasets.servico import ServicoDatasets

__all__ = ["Analise", "Posicao", "ServicoAnalise", "TipoSeparatriz"]


class ServicoAnalise:
    """Casos de uso da análise; os dados vêm da fachada do domínio datasets."""

    def __init__(self, datasets: ServicoDatasets) -> None:
        self._datasets = datasets

    def amostra(self, dataset_id: str, coluna: str) -> Amostra:
        """Valores válidos da coluna, já convertidos conforme o tipo."""
        dados = self._datasets.coluna_para_analise(dataset_id, coluna)
        if dados.tipo == TipoVariavel.IDENTIFICADOR:
            raise erros.coluna_ignorada(coluna)
        serie = dados.numeros if dados.numeros is not None else dados.textos
        validos = serie.dropna()
        if validos.empty:
            raise erros.coluna_vazia(coluna)
        return Amostra(coluna, dados.tipo, validos, int(serie.isna().sum()), dados.categorias_ordem)

    def analisar(
        self,
        dataset_id: str,
        coluna: str,
        classes: int | None = None,
        sucesso: str | None = None,
    ) -> Analise:
        """Frequências, tendência, separatrizes e dispersão da coluna (specs 04–07)."""
        return analisar_amostra(self.amostra(dataset_id, coluna), classes, sucesso)

    def posicao(self, dataset_id: str, coluna: str, valor: float, tipo: TipoSeparatriz) -> Posicao:
        """Em que separatriz o valor cai (spec 06)."""
        amostra = self.amostra(dataset_id, coluna)
        if amostra.tipo not in TIPOS_NUMERICOS:
            raise erros.posicao_nao_aplicavel()
        return calcular_posicao(amostra.valores.to_numpy(dtype="float64"), valor, tipo)
