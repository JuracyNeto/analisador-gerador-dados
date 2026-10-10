"""Fachada do domínio analise: univariada, forma, "onde está meu valor?" e bivariada (D54)."""

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from app.compartilhado.tipos import TIPOS_AUXILIARES, TIPOS_NUMERICOS
from app.dominios.analise import erros
from app.dominios.analise.bivariada import analisar_par, montar_par, prever_no_par
from app.dominios.analise.correlacao import matriz_correlacao
from app.dominios.analise.formulas import CHAVES_FORMA
from app.dominios.analise.pontos_forma import PontosForma, pontos_da_forma
from app.dominios.analise.posicao import calcular_posicao
from app.dominios.analise.resultados import (
    Ajuste,
    Amostra,
    Analise,
    Figura,
    Forma,
    Formula,
    Medida,
    Posicao,
    TabelaFrequencia,
    TipoSeparatriz,
)
from app.dominios.analise.resultados_bivariada import Bivariada, MatrizCorrelacao, Par, Previsao
from app.dominios.analise.univariada import analisar_amostra
from app.dominios.datasets.servico import ServicoDatasets
from app.dominios.graficos.servico import (
    Barra,
    BinomialFigura,
    CurvaFigura,
    DadosBivariados,
    DadosForma,
    DadosMatriz,
    DadosUnivariados,
    FiguraPronta,
    QQFigura,
    figura_matriz,
    figuras_bivariadas,
    figuras_forma,
    figuras_univariadas,
)

__all__ = [
    "CHAVES_FORMA",
    "Ajuste",
    "Analise",
    "Bivariada",
    "Figura",
    "Forma",
    "Formula",
    "MatrizCorrelacao",
    "Medida",
    "OpcoesAnalise",
    "Posicao",
    "Previsao",
    "ServicoAnalise",
    "TipoSeparatriz",
]


@dataclass(frozen=True, slots=True)
class OpcoesAnalise:
    """Ajustes que o usuário pode pedir na análise de uma coluna."""

    classes: int | None = None
    sucesso: str | None = None
    tentativas: int | None = None


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
    return _como_figuras(figuras_univariadas(dados))


def _como_figuras(prontas: tuple[FiguraPronta, ...]) -> tuple[Figura, ...]:
    return tuple(
        Figura(f.id, f.rotulo, f.titulo, f.resumo, f.porque, f.recomendado, f.dados)
        for f in prontas
    )


def _dados_forma(amostra: Amostra, analise: Analise, pontos: PontosForma) -> DadosForma:
    """Converte os pontos do domínio analise nas entradas do domínio graficos."""
    forma = analise.forma
    normal = forma.normal.teste if forma else None
    binomial = forma.binomial.teste if forma else None
    curva, qq, comparacao = pontos.curva, pontos.qq, pontos.binomial
    return DadosForma(
        coluna=amostra.coluna,
        tipo=amostra.tipo,
        n=amostra.n,
        barras=_barras(analise.frequencias),
        curva=CurvaFigura(curva.x, curva.y, curva.media, curva.desvio) if curva else None,
        qq=QQFigura(qq.teoricos, qq.observados, qq.media, qq.desvio) if qq else None,
        binomial=BinomialFigura(
            comparacao.k, comparacao.observados, comparacao.esperados, comparacao.n, comparacao.p
        )
        if comparacao
        else None,
        normal_compativel=normal.compativel if normal else None,
        binomial_compativel=binomial.compativel if binomial else None,
    )


def _com_figuras_da_forma(amostra: Amostra, analise: Analise) -> Forma | None:
    """Figuras da aba Forma (D94), a partir dos pontos calculados no domínio analise."""
    if analise.forma is None:
        return None
    valores = (
        amostra.valores.to_numpy(dtype="float64")
        if amostra.tipo in TIPOS_NUMERICOS
        else np.array([])
    )
    dados = _dados_forma(amostra, analise, pontos_da_forma(valores, analise))
    return replace(analise.forma, figuras=_como_figuras(figuras_forma(dados)))


def _figuras_bivariadas(par: Par, bivariada: Bivariada) -> tuple[Figura, ...]:
    """Dispersão com a reta e resíduos × X, a partir do par já sem faltantes (spec 10)."""
    reta = bivariada.regressao
    dados = DadosBivariados(
        x_nome=par.x,
        y_nome=par.y,
        x=tuple(float(v) for v in par.valores_x),
        y=tuple(float(v) for v in par.valores_y),
        a=reta.a,
        b=reta.b,
        equacao=reta.equacao,
        forca=bivariada.forca,
        sentido=bivariada.sentido,
    )
    return _como_figuras(figuras_bivariadas(dados))


def _com_figura_da_matriz(matriz: MatrizCorrelacao) -> MatrizCorrelacao:
    pronta = figura_matriz(DadosMatriz(matriz.colunas, matriz.valores, matriz.resumo))
    figuras = _como_figuras((pronta,)) if pronta else ()
    return replace(matriz, figura=figuras[0] if figuras else None)


class ServicoAnalise:
    """Casos de uso da análise; os dados vêm da fachada do domínio datasets."""

    def __init__(self, datasets: ServicoDatasets) -> None:
        self._datasets = datasets

    def amostra(self, dataset_id: str, coluna: str) -> Amostra:
        """Valores válidos da coluna, já convertidos conforme o tipo."""
        dados = self._datasets.coluna_para_analise(dataset_id, coluna)
        if dados.tipo in TIPOS_AUXILIARES:
            raise erros.coluna_ignorada(coluna, dados.tipo)
        serie = dados.numeros if dados.numeros is not None else dados.textos
        validos = serie.dropna()
        if validos.empty:
            raise erros.coluna_vazia(coluna)
        return Amostra(coluna, dados.tipo, validos, int(serie.isna().sum()), dados.categorias_ordem)

    def analisar(
        self, dataset_id: str, coluna: str, opcoes: OpcoesAnalise | None = None
    ) -> Analise:
        """Frequências, tendência, separatrizes, dispersão, forma e gráficos (specs 04–09)."""
        pedido = opcoes or OpcoesAnalise()
        amostra = self.amostra(dataset_id, coluna)
        analise = analisar_amostra(amostra, pedido.classes, pedido.sucesso, pedido.tentativas)
        return replace(
            analise,
            figuras=_figuras(amostra, analise),
            forma=_com_figuras_da_forma(amostra, analise),
        )

    def posicao(self, dataset_id: str, coluna: str, valor: float, tipo: TipoSeparatriz) -> Posicao:
        """Em que separatriz o valor cai (spec 06)."""
        amostra = self.amostra(dataset_id, coluna)
        if amostra.tipo not in TIPOS_NUMERICOS:
            raise erros.posicao_nao_aplicavel()
        return calcular_posicao(amostra.valores.to_numpy(dtype="float64"), valor, tipo)

    def _numeros(self, dataset_id: str, coluna: str) -> pd.Series:
        """Números da coluna; a bivariada só aceita discretas e contínuas (spec 10)."""
        dados = self._datasets.coluna_para_analise(dataset_id, coluna)
        if dados.tipo not in TIPOS_NUMERICOS or dados.numeros is None:
            raise erros.coluna_nao_numerica(coluna)
        return dados.numeros

    def par(self, dataset_id: str, x: str, y: str) -> Par:
        """X e Y só nas linhas em que as duas têm valor (D100)."""
        return montar_par(x, y, self._numeros(dataset_id, x), self._numeros(dataset_id, y))

    def bivariada(self, dataset_id: str, x: str, y: str) -> Bivariada:
        """Correlação, regressão, resíduos e figuras do par (spec 10)."""
        par = self.par(dataset_id, x, y)
        resultado = analisar_par(par)
        return replace(resultado, figuras=_figuras_bivariadas(par, resultado))

    def prever(self, dataset_id: str, x: str, y: str, valor: float) -> Previsao:
        """Ŷ para um X, com aviso de extrapolação (spec 10)."""
        return prever_no_par(self.par(dataset_id, x, y), valor)

    def correlacoes(self, dataset_id: str) -> MatrizCorrelacao:
        """Pearson par a par de todas as colunas discretas e contínuas, com o heatmap."""
        nomes = [c.coluna for c in self._datasets.colunas(dataset_id) if c.tipo in TIPOS_NUMERICOS]
        tabela = pd.DataFrame({nome: self._numeros(dataset_id, nome) for nome in nomes})
        return _com_figura_da_matriz(matriz_correlacao(tabela))
