"""R5 — Duplicatas: linhas iguais sempre; quase iguais até 5.000 linhas (spec 12, D120)."""

from dataclasses import dataclass, replace

import numpy as np

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector import textos
from app.dominios.detector.duplicatas import (
    GrupoRepetido,
    chaves_das_colunas,
    repetidos_exatos,
    repetidos_ou_quase,
)
from app.dominios.detector.exemplos import MAX_LINHAS_EXEMPLO
from app.dominios.detector.regras import base
from app.dominios.detector.resultados import ExemploAviso
from app.dominios.detector.tabela import ColunaDetector, TabelaDetector

LIMITE_QUASE = 5_000
"""Acima disso, só linhas idênticas: a busca por quase iguais compara pares de linhas."""
MINIMO_COLUNAS = 2
MINIMO_LINHAS = 2
MINIMO_SEGUIDAS = 3


@dataclass(frozen=True, slots=True, eq=False)
class AlvoArquivo:
    """O arquivo todo: as colunas comparáveis (todas menos os identificadores, D50)."""

    linhas: np.ndarray
    colunas: tuple[ColunaDetector, ...]

    @property
    def rotulo(self) -> None:
        return None

    @property
    def n(self) -> int:
        return len(self.linhas)

    @property
    def n_numericas(self) -> int:
        return sum(coluna.numeros is not None for coluna in self.colunas)

    @property
    def compara_quase_iguais(self) -> bool:
        return self.n <= LIMITE_QUASE and self.n_numericas > 0

    def linha_como_texto(self, posicao: int) -> str:
        return textos.linha_como_texto([coluna.textos[posicao] for coluna in self.colunas])


@dataclass(frozen=True, slots=True)
class ArquivoTodo:
    """Seletor da R5: um alvo só, com as colunas que não são identificadores."""

    motivo_sem_alvos: str = textos.SO_IDENTIFICADORES

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoArquivo, ...]:
        colunas = tuple(
            coluna
            for coluna in tabela.colunas.values()
            if coluna.tipo != TipoVariavel.IDENTIFICADOR
        )
        return (AlvoArquivo(tabela.linhas, colunas),) if colunas else ()


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoDuplicatas:
    grupos: tuple[GrupoRepetido, ...]

    @property
    def copias(self) -> int:
        return sum(grupo.copias for grupo in self.grupos)

    @property
    def grupos_quase(self) -> int:
        return sum(not grupo.exato for grupo in self.grupos)

    @property
    def destaque(self) -> GrupoRepetido:
        """O grupo com mais linhas seguidas (e, no empate, com mais linhas)."""
        return max(self.grupos, key=lambda g: (len(g.maior_sequencia), len(g.posicoes)))


def _colunas_suficientes(alvo: AlvoArquivo) -> str | None:
    return textos.POUCAS_COLUNAS if len(alvo.colunas) < MINIMO_COLUNAS else None


def _linhas_suficientes(alvo: AlvoArquivo) -> str | None:
    return textos.poucas_linhas(MINIMO_LINHAS, alvo.n) if alvo.n < MINIMO_LINHAS else None


def _exemplo(alvo: AlvoArquivo, grupo: GrupoRepetido) -> ExemploAviso:
    posicoes = grupo.posicoes[:MAX_LINHAS_EXEMPLO]
    linhas = tuple(int(linha) for linha in alvo.linhas[posicoes])
    valores = tuple(alvo.linha_como_texto(int(posicao)) for posicao in posicoes)
    escrever = textos.r05_texto_exemplo if grupo.exato else textos.r05_texto_exemplo_quase
    return ExemploAviso(linhas, valores, escrever(linhas, valores[0]))


class RegraDuplicatas(base.RegraBase[AlvoArquivo, MedicaoDuplicatas]):
    """Qualquer cópia → atenção; 3 linhas iguais seguidas ou mais → suspeita alta."""

    codigo = "R5"
    nome = "Duplicatas"
    seletor = ArquivoTodo()
    requisito = base.Todos((_colunas_suficientes, _linhas_suficientes))

    def executar(self, tabela: TabelaDetector) -> base.ResultadoRegra:
        """Como na base; em arquivos grandes, avisa que as quase iguais ficaram de fora."""
        resultado = super().executar(tabela)
        if not resultado.verificada or tabela.n_linhas <= LIMITE_QUASE or not tabela.numericas():
            return resultado
        motivo, frase = textos.r05_ressalva(tabela.n_linhas, LIMITE_QUASE)
        ressalva = self.nao_aplicada(None, motivo, frase)
        return replace(resultado, nao_aplicadas=(*resultado.nao_aplicadas, ressalva))

    def medir(self, alvo: AlvoArquivo) -> MedicaoDuplicatas:
        chaves = chaves_das_colunas(alvo.colunas)
        if alvo.compara_quase_iguais:
            return MedicaoDuplicatas(repetidos_ou_quase(chaves))
        return MedicaoDuplicatas(repetidos_exatos(chaves))

    def dispara(self, medicao: MedicaoDuplicatas) -> bool:
        return bool(medicao.grupos)

    def conteudo_aviso(self, alvo: AlvoArquivo, medicao: MedicaoDuplicatas) -> base.ConteudoAviso:
        destaque = medicao.destaque
        sequencia = destaque.maior_sequencia
        seguidas = (
            (int(alvo.linhas[sequencia[0]]), int(alvo.linhas[sequencia[-1]]))
            if len(sequencia) >= MINIMO_SEGUIDAS
            else None
        )
        formula = (
            textos.r05_formula_quase(alvo.n_numericas)
            if alvo.compara_quase_iguais
            else textos.R05_FORMULA_IDENTICAS
        )
        return base.ConteudoAviso(
            severidade=Severidade.ALTA if seguidas else Severidade.ATENCAO,
            colunas=(),
            textos=textos.r05_textos(medicao.copias, medicao.grupos_quase, seguidas),
            exemplo=_exemplo(alvo, destaque),
            detalhes=textos.r05_detalhes(medicao.copias, len(medicao.grupos), formula),
        )
