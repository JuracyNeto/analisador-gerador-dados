"""R5 — Duplicatas: linhas iguais e quase iguais (até 5.000 linhas) além do acaso (D120)."""

from dataclasses import dataclass, replace

import numpy as np

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector import textos, textos_duplicatas
from app.dominios.detector.duplicatas import (
    SEM_PARES,
    TRINCA,
    ContraOAcaso,
    GrupoRepetido,
    acaso_das_repeticoes,
    chaves_das_colunas,
    linhas_comparaveis,
    pares_quase_iguais,
    repetidos,
    seguidas_contra_o_acaso,
)
from app.dominios.detector.exemplos import MAX_LINHAS_EXEMPLO
from app.dominios.detector.regras import base
from app.dominios.detector.resultados import DetalhesAviso, ExemploAviso
from app.dominios.detector.tabela import ColunaDetector, TabelaDetector

LIMITE_QUASE = 5_000
"""Acima disso, só linhas idênticas: a busca por quase iguais compara pares de linhas."""
MINIMO_COLUNAS = 2
MINIMO_LINHAS = 2


@dataclass(frozen=True, slots=True, eq=False)
class AlvoArquivo:
    """O arquivo todo: as colunas comparáveis (todas menos os identificadores, D50).

    Só as linhas com algum número e 2 células preenchidas entram (D138, D171); o limite das
    quase iguais vale para o arquivo.
    """

    linhas: np.ndarray
    colunas: tuple[ColunaDetector, ...]
    linhas_no_arquivo: int

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
        return self.linhas_no_arquivo <= LIMITE_QUASE and self.n_numericas > 0

    def linha_como_texto(self, posicao: int) -> str:
        return textos.linha_como_texto(
            [(coluna.nome, coluna.textos[posicao]) for coluna in self.colunas]
        )


@dataclass(frozen=True, slots=True)
class ArquivoTodo:
    """Seletor da R5: um alvo só, com as colunas que não são identificadores."""

    motivo_sem_alvos: str = textos_duplicatas.SO_IDENTIFICADORES

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoArquivo, ...]:
        colunas = tuple(
            coluna
            for coluna in tabela.colunas.values()
            if coluna.tipo != TipoVariavel.IDENTIFICADOR
        )
        if not colunas:
            return ()
        # Linhas sem nenhum número (estação desligada, D138) ou com uma célula só (valores
        # anexados pelo Gerador, D171) não são cópias umas das outras.
        comparaveis = linhas_comparaveis(colunas)
        recortadas = tuple(coluna.nas_linhas(comparaveis) for coluna in colunas)
        return (AlvoArquivo(tabela.linhas[comparaveis], recortadas, tabela.n_linhas),)


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoDuplicatas:
    """Grupos de linhas repetidas e as comparações com o acaso que decidem o aviso."""

    grupos: tuple[GrupoRepetido, ...]
    iguais: ContraOAcaso
    seguidas: ContraOAcaso
    quase: ContraOAcaso | None
    """None quando as quase iguais não foram procuradas (arquivo grande)."""

    @property
    def quase_alem_do_acaso(self) -> bool:
        return self.quase is not None and self.quase.p_valor < base.LIMIAR_P

    @property
    def alem_do_acaso(self) -> bool:
        return self.iguais.p_valor < base.LIMIAR_P or self.quase_alem_do_acaso

    @property
    def em_sequencia(self) -> bool:
        return self.seguidas.p_valor < base.LIMIAR_P

    @property
    def avisados(self) -> tuple[GrupoRepetido, ...]:
        """Todos os grupos se as repetições passam do acaso; senão, só os seguidos improváveis."""
        if self.alem_do_acaso:
            return self.grupos
        if self.em_sequencia:
            return tuple(g for g in self.grupos if len(g.maior_sequencia) >= TRINCA)
        return ()

    @property
    def copias(self) -> int:
        return sum(grupo.copias for grupo in self.avisados)

    @property
    def grupos_quase(self) -> int:
        return sum(not grupo.exato for grupo in self.avisados)

    @property
    def destaque(self) -> GrupoRepetido:
        """O grupo com mais linhas seguidas (e, no empate, com mais linhas)."""
        return max(self.avisados, key=lambda g: (len(g.maior_sequencia), len(g.posicoes)))

    @property
    def teste(self) -> tuple[str, ContraOAcaso]:
        """A comparação com o acaso que justificou o aviso (para os detalhes)."""
        if self.iguais.p_valor < base.LIMIAR_P:
            return "iguais", self.iguais
        if self.quase is not None and self.quase_alem_do_acaso:
            return "quase", self.quase
        return "seguidas", self.seguidas


def _colunas_suficientes(alvo: AlvoArquivo) -> str | None:
    return textos_duplicatas.POUCAS_COLUNAS if len(alvo.colunas) < MINIMO_COLUNAS else None


def _linhas_suficientes(alvo: AlvoArquivo) -> str | None:
    return textos.poucas_linhas(MINIMO_LINHAS, alvo.n) if alvo.n < MINIMO_LINHAS else None


def _exemplo(alvo: AlvoArquivo, grupo: GrupoRepetido) -> ExemploAviso:
    posicoes = grupo.posicoes[:MAX_LINHAS_EXEMPLO]
    linhas = tuple(int(linha) for linha in alvo.linhas[posicoes])
    valores = tuple(alvo.linha_como_texto(int(posicao)) for posicao in posicoes)
    escrever = (
        textos_duplicatas.r05_texto_exemplo
        if grupo.exato
        else textos_duplicatas.r05_texto_exemplo_quase
    )
    return ExemploAviso(linhas, valores, escrever(linhas, valores[0]))


def _detalhes(alvo: AlvoArquivo, medicao: MedicaoDuplicatas) -> DetalhesAviso:
    formula = (
        textos_duplicatas.r05_formula_quase(alvo.n_numericas)
        if medicao.quase is not None
        else textos_duplicatas.R05_FORMULA_IDENTICAS
    )
    tipo, acaso = medicao.teste
    return textos_duplicatas.r05_detalhes(
        medicao.copias, len(medicao.avisados), formula, tipo, acaso
    )


class RegraDuplicatas(base.RegraBase[AlvoArquivo, MedicaoDuplicatas]):
    """Repetições além do acaso → atenção; 3 iguais seguidas, improváveis ao acaso → alta."""

    codigo = "R5"
    nome = "Duplicatas"
    seletor = ArquivoTodo()
    requisito = base.Todos((_colunas_suficientes, _linhas_suficientes))

    def executar(self, tabela: TabelaDetector) -> base.ResultadoRegra:
        """Como na base; em arquivos grandes, avisa que as quase iguais ficaram de fora."""
        resultado = super().executar(tabela)
        if not resultado.verificada or tabela.n_linhas <= LIMITE_QUASE or not tabela.numericas():
            return resultado
        motivo, frase = textos_duplicatas.r05_ressalva(tabela.n_linhas, LIMITE_QUASE)
        ressalva = self.nao_aplicada(None, motivo, frase)
        return replace(resultado, nao_aplicadas=(*resultado.nao_aplicadas, ressalva))

    def medir(self, alvo: AlvoArquivo) -> MedicaoDuplicatas:
        chaves = chaves_das_colunas(alvo.colunas)
        identicos = repetidos(chaves, SEM_PARES)
        if not alvo.compara_quase_iguais:
            acaso = acaso_das_repeticoes(chaves, identicos, SEM_PARES)
            seguidas = seguidas_contra_o_acaso(identicos, alvo.n)
            return MedicaoDuplicatas(identicos, acaso.iguais, seguidas, None)
        quase = pares_quase_iguais(chaves)
        acaso = acaso_das_repeticoes(chaves, identicos, quase)
        grupos = repetidos(chaves, quase) if acaso.quase.p_valor < base.LIMIAR_P else identicos
        seguidas = seguidas_contra_o_acaso(grupos, alvo.n)
        return MedicaoDuplicatas(grupos, acaso.iguais, seguidas, acaso.quase)

    def dispara(self, medicao: MedicaoDuplicatas) -> bool:
        return bool(medicao.avisados)

    def conteudo_aviso(self, alvo: AlvoArquivo, medicao: MedicaoDuplicatas) -> base.ConteudoAviso:
        destaque = medicao.destaque
        sequencia = destaque.maior_sequencia
        seguidas = (
            (int(alvo.linhas[sequencia[0]]), int(alvo.linhas[sequencia[-1]]))
            if medicao.em_sequencia and len(sequencia) >= TRINCA
            else None
        )
        return base.ConteudoAviso(
            severidade=Severidade.ALTA if seguidas else Severidade.ATENCAO,
            colunas=(),
            textos=textos_duplicatas.r05_textos(medicao.copias, medicao.grupos_quase, seguidas),
            exemplo=_exemplo(alvo, destaque),
            detalhes=_detalhes(alvo, medicao),
        )
