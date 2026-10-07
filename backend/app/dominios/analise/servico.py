"""Fachada do domínio analise: análise univariada e "onde está meu valor?" (D54)."""

from dataclasses import replace

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import erros
from app.dominios.analise.posicao import calcular_posicao
from app.dominios.analise.resultados import (
    Amostra,
    Analise,
    Figura,
    Posicao,
    TabelaFrequencia,
    TipoSeparatriz,
)
from app.dominios.analise.univariada import analisar_amostra
from app.dominios.datasets.servico import ServicoDatasets
from app.dominios.graficos.servico import Barra, DadosUnivariados, figuras_univariadas

__all__ = ["Analise", "Figura", "Posicao", "ServicoAnalise", "TipoSeparatriz"]


def _barras(tabela: TabelaFrequencia) -> tuple[Barra, ...]:
    return tuple(
        Barra(
            rotulo=linha.rotulo,
            frequencia=linha.fi,
            percentual=linha.fr_pct,
            acumulado_pct=linha.fr_acum_pct,
            valor=linha.valor if isinstance(linha.valor, float) else None,
            inferior=linha.limite_inferior,
            superior=linha.limite_superior,
        )
        for linha in tabela.linhas
    )


def _figuras(amostra: Amostra, analise: Analise) -> tuple[Figura, ...]:
    """Pede ao domínio graficos as figuras do tipo (spec 08) a partir da tabela já calculada."""
    numerica = amostra.tipo in TIPOS_NUMERICOS
    dados = DadosUnivariados(
        coluna=amostra.coluna,
        tipo=amostra.tipo,
        n=amostra.n,
        barras=_barras(analise.frequencias),
        valores=amostra.valores if numerica else None,
    )
    return tuple(
        Figura(f.id, f.rotulo, f.titulo, f.resumo, f.porque, f.recomendado, f.dados)
        for f in figuras_univariadas(dados)
    )


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
        """Frequências, tendência, separatrizes, dispersão e gráficos da coluna (specs 04–08)."""
        amostra = self.amostra(dataset_id, coluna)
        analise = analisar_amostra(amostra, classes, sucesso)
        return replace(analise, figuras=_figuras(amostra, analise))

    def posicao(self, dataset_id: str, coluna: str, valor: float, tipo: TipoSeparatriz) -> Posicao:
        """Em que separatriz o valor cai (spec 06)."""
        amostra = self.amostra(dataset_id, coluna)
        if amostra.tipo not in TIPOS_NUMERICOS:
            raise erros.posicao_nao_aplicavel()
        return calcular_posicao(amostra.valores.to_numpy(dtype="float64"), valor, tipo)
