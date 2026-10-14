"""R6 — Comparação temporal: antes × depois da data do meio (spec 12).

Ordena pela 1ª coluna de data e divide na data do meio (a mediana, uma data do arquivo). Duas
partes com o mesmo código: a variação de cada numérica (DP depois < 0,5 × DP antes, com F
unilateral p < 0,01) e as linhas novas iguais a antigas fora a data (≥ 10% e acima do que as
antigas se repetem entre si, binomial p < 0,01) — as duas contra o acaso, como a R5 (D120).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from app.compartilhado import estatistica
from app.compartilhado.datas import formatar_data
from app.compartilhado.tipos import TIPOS_AUXILIARES, Severidade, TipoVariavel
from app.dominios.detector import textos, textos_blocos
from app.dominios.detector.duplicatas import chaves_das_colunas, ids_exatos
from app.dominios.detector.exemplos import MAX_LINHAS_EXEMPLO, exemplo_de_valores
from app.dominios.detector.regras import base
from app.dominios.detector.resultados import ExemploAviso, RegraNaoAplicada
from app.dominios.detector.tabela import ColunaDetector, TabelaDetector

CODIGO = "R6"
NOME = "Comparação temporal"
MINIMO_LINHAS = 40
MINIMO_POR_PERIODO = 10
RAZAO_DESVIO = 0.5
MINIMO_COPIAS = 0.1


@dataclass(frozen=True, slots=True, eq=False)
class Periodos:
    """Posições das linhas com data, em ordem de data, e quantas ficam até a data do meio."""

    posicoes: np.ndarray
    datas: np.ndarray
    corte: int

    @property
    def n(self) -> int:
        return len(self.posicoes)

    @property
    def data_do_meio(self) -> str:
        return formatar_data(pd.Timestamp(self.datas[self.corte - 1]).to_pydatetime())

    def so_com(self, validos: np.ndarray) -> "Periodos":
        """Só as linhas marcadas em `validos` (na ordem da tabela), com a mesma data do meio."""
        manter = validos[self.posicoes]
        return Periodos(self.posicoes[manter], self.datas[manter], int(manter[: self.corte].sum()))


def periodos(datas: np.ndarray) -> Periodos:
    """Linhas ordenadas pela data; antes = até a data do meio (mediana inferior), inclusive."""
    posicoes = np.flatnonzero(~np.isnat(datas))
    ordem = posicoes[np.argsort(datas[posicoes], kind="stable")]
    ordenadas = datas[ordem]
    if len(ordenadas) == 0:
        return Periodos(ordem, ordenadas, 0)
    meio = ordenadas[(len(ordenadas) - 1) // 2]
    return Periodos(ordem, ordenadas, int(np.searchsorted(ordenadas, meio, side="right")))


def _coluna_de_datas(tabela: TabelaDetector) -> ColunaDetector | None:
    return next((c for c in tabela.do_tipo({TipoVariavel.DATA}) if c.datas is not None), None)


def _periodos_da_tabela(tabela: TabelaDetector) -> Periodos | None:
    coluna = _coluna_de_datas(tabela)
    return None if coluna is None or coluna.datas is None else periodos(coluna.datas)


def _dois_periodos(alvo: "AlvoVariacao | AlvoCopias") -> str | None:
    corte, n = alvo.periodos.corte, alvo.periodos.n
    if min(corte, n - corte) < MINIMO_POR_PERIODO:
        return textos_blocos.poucas_linhas_por_periodo(MINIMO_POR_PERIODO)
    return None


# Variação de cada numérica ------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class AlvoVariacao:
    """Uma numérica em ordem de data (só as linhas com data e valor)."""

    nome: str
    linhas: np.ndarray
    valores: np.ndarray
    periodos: Periodos

    @property
    def rotulo(self) -> str:
        return self.nome

    @property
    def n(self) -> int:
        return len(self.valores)


def _variacao(tabela: TabelaDetector, coluna: ColunaDetector, todos: Periodos) -> AlvoVariacao:
    numeros = tabela.numeros(coluna)
    validos = todos.so_com(~np.isnan(numeros))
    return AlvoVariacao(
        coluna.nome, tabela.linhas[validos.posicoes], numeros[validos.posicoes], validos
    )


@dataclass(frozen=True, slots=True)
class NumericasNoTempo:
    motivo_sem_alvos: str = textos.SEM_NUMERICAS

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoVariacao, ...]:
        todos = _periodos_da_tabela(tabela)
        if todos is None:
            return ()
        return tuple(_variacao(tabela, coluna, todos) for coluna in tabela.numericas())


@dataclass(frozen=True, slots=True)
class MedicaoVariacao:
    desvios: tuple[float, float]
    """(antes, depois)."""
    p_valor: float


def _teste_f(antes: np.ndarray, depois: np.ndarray) -> float:
    """P(F ≤ s²_depois / s²_antes): chance de o DP cair tanto por acaso."""
    variancia_antes = float(np.var(antes, ddof=1))
    if variancia_antes == 0:
        return 1.0
    razao = float(np.var(depois, ddof=1)) / variancia_antes
    return float(stats.f.cdf(razao, len(depois) - 1, len(antes) - 1))


class VariacaoTemporal(base.RegraBase[AlvoVariacao, MedicaoVariacao]):
    """DP depois < 0,5 × DP antes, improvável ao acaso (F unilateral, p < 0,01)."""

    codigo = CODIGO
    nome = NOME
    seletor = NumericasNoTempo()
    requisito = base.Todos((base.MinimoDeValores(MINIMO_LINHAS), _dois_periodos))

    def medir(self, alvo: AlvoVariacao) -> MedicaoVariacao:
        antes, depois = alvo.valores[: alvo.periodos.corte], alvo.valores[alvo.periodos.corte :]
        desvios = (float(np.std(antes, ddof=1)), float(np.std(depois, ddof=1)))
        return MedicaoVariacao(desvios, _teste_f(antes, depois))

    def dispara(self, medicao: MedicaoVariacao) -> bool:
        antes, depois = medicao.desvios
        return depois < RAZAO_DESVIO * antes and medicao.p_valor < base.LIMIAR_P

    def conteudo_aviso(self, alvo: AlvoVariacao, medicao: MedicaoVariacao) -> base.ConteudoAviso:
        corte = alvo.periodos.corte
        depois = slice(corte, corte + MAX_LINHAS_EXEMPLO)
        data = alvo.periodos.data_do_meio
        return base.ConteudoAviso(
            severidade=Severidade.ALTA,
            colunas=(alvo.nome,),
            textos=textos_blocos.r06_textos_variacao(alvo.nome, data, medicao.desvios),
            exemplo=exemplo_de_valores(alvo.linhas[depois], alvo.valores[depois]),
            detalhes=textos_blocos.r06_detalhes_variacao(
                data, medicao.desvios, (corte, alvo.n - corte), medicao.p_valor
            ),
        )


# Linhas novas iguais a antigas --------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class AlvoCopias:
    """O arquivo em ordem de data, com as colunas comparadas (fora datas e identificadores)."""

    linhas: np.ndarray
    colunas: tuple[ColunaDetector, ...]
    periodos: Periodos

    @property
    def rotulo(self) -> None:
        return None

    @property
    def n(self) -> int:
        return self.periodos.n

    def linha_como_texto(self, posicao: int) -> str:
        return textos.linha_como_texto([coluna.textos[posicao] for coluna in self.colunas])


@dataclass(frozen=True, slots=True)
class ArquivoNoTempo:
    motivo_sem_alvos: str = textos_blocos.SO_DATAS

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoCopias, ...]:
        todos = _periodos_da_tabela(tabela)
        colunas = tuple(c for c in tabela.colunas.values() if c.tipo not in TIPOS_AUXILIARES)
        if todos is None or not colunas:
            return ()
        return (AlvoCopias(tabela.linhas, colunas, todos),)


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoCopias:
    novas: np.ndarray
    """Posições (na tabela) das linhas novas iguais a alguma antiga, em ordem de data."""
    antigas: np.ndarray
    """Para cada uma, a primeira linha antiga igual."""
    total_novas: int
    acaso: float
    """Fração das linhas antigas que se repetem entre si."""

    @property
    def proporcao(self) -> float:
        return len(self.novas) / self.total_novas

    @property
    def p_valor(self) -> float:
        return estatistica.teste_binomial_unilateral(len(self.novas), self.total_novas, self.acaso)


def _linhas_suficientes(alvo: AlvoCopias) -> str | None:
    return textos.poucas_linhas(MINIMO_LINHAS, alvo.n) if alvo.n < MINIMO_LINHAS else None


class CopiasTemporais(base.RegraBase[AlvoCopias, MedicaoCopias]):
    """≥ 10% das linhas novas iguais a antigas e acima do acaso (binomial, p < 0,01)."""

    codigo = CODIGO
    nome = NOME
    seletor = ArquivoNoTempo()
    requisito = base.Todos((_linhas_suficientes, _dois_periodos))

    def medir(self, alvo: AlvoCopias) -> MedicaoCopias:
        posicoes, corte = alvo.periodos.posicoes, alvo.periodos.corte
        ids = ids_exatos(chaves_das_colunas(alvo.colunas))[posicoes]
        antes, depois = ids[:corte], ids[corte:]
        unicos, primeiras, contagens = np.unique(antes, return_index=True, return_counts=True)
        repetem = np.isin(depois, antes)
        primeira_igual = primeiras[np.searchsorted(unicos, depois[repetem])]
        return MedicaoCopias(
            novas=posicoes[corte:][repetem],
            antigas=posicoes[primeira_igual],
            total_novas=len(depois),
            acaso=float(np.mean(contagens[np.searchsorted(unicos, antes)] > 1)),
        )

    def dispara(self, medicao: MedicaoCopias) -> bool:
        return medicao.proporcao >= MINIMO_COPIAS and medicao.p_valor < base.LIMIAR_P

    def conteudo_aviso(self, alvo: AlvoCopias, medicao: MedicaoCopias) -> base.ConteudoAviso:
        data = alvo.periodos.data_do_meio
        copias = len(medicao.novas)
        return base.ConteudoAviso(
            severidade=Severidade.ALTA,
            colunas=(),
            textos=textos_blocos.r06_textos_copias(data, copias, medicao.total_novas),
            exemplo=_exemplo_copias(alvo, medicao),
            detalhes=textos_blocos.r06_detalhes_copias(
                copias, medicao.total_novas, medicao.acaso, medicao.p_valor
            ),
        )


def _exemplo_copias(alvo: AlvoCopias, medicao: MedicaoCopias) -> ExemploAviso:
    novas = medicao.novas[:MAX_LINHAS_EXEMPLO]
    linhas = tuple(int(linha) for linha in alvo.linhas[novas])
    antigas = tuple(int(linha) for linha in alvo.linhas[medicao.antigas[:MAX_LINHAS_EXEMPLO]])
    valores = tuple(alvo.linha_como_texto(int(posicao)) for posicao in novas)
    return ExemploAviso(linhas, valores, textos_blocos.r06_texto_exemplo_copias(linhas, antigas))


# A regra ------------------------------------------------------------------------------------


class RegraTemporal:
    """As duas partes da R6; sem coluna de data, a regra não se aplica ao arquivo."""

    codigo = CODIGO
    nome = NOME
    partes = (VariacaoTemporal(), CopiasTemporais())

    def executar(self, tabela: TabelaDetector) -> base.ResultadoRegra:
        if _coluna_de_datas(tabela) is None:
            motivo = textos_blocos.SEM_DATA
            frase = textos.frase_nao_aplicada(NOME, None, motivo)
            sem_data = RegraNaoAplicada(CODIGO, NOME, None, motivo, frase)
            return base.ResultadoRegra((), (sem_data,), verificada=False)
        return base.executar_em_partes(self.partes, tabela)
