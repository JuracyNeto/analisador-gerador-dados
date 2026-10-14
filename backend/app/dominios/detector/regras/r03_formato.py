"""R3 — Formato numérico: inteiros agrupados ou regulares numa coluna de decimais (spec 12)."""

from dataclasses import dataclass

import numpy as np

from app.compartilhado import estatistica
from app.compartilhado.tipos import Severidade
from app.dominios.detector import textos
from app.dominios.detector.exemplos import exemplo_de_valores
from app.dominios.detector.regras import base

MINIMO_VALORES = 30
MINIMO_DECIMAIS = 0.8
MINIMO_SEGUIDOS = 5
MINIMO_REPETICOES_PASSO = 4
"""Passo constante entre inteiros repetido 4 vezes (5 inteiros a cada k linhas)."""
TOLERANCIA = 1e-9


@dataclass(frozen=True, slots=True)
class PadraoInteiros:
    """Inteiros seguidos (passo 1) ou a cada `passo` posições, da posição início à fim."""

    inicio: int
    fim: int
    quantidade: int
    passo: int
    esperados: float = 0.0
    """Quantos padrões assim o acaso daria (inteiros espalhados ao acaso)."""

    @property
    def posicoes(self) -> np.ndarray:
        return np.arange(self.inicio, self.fim + 1, self.passo)

    @property
    def encontrado(self) -> bool:
        return self.quantidade > 0


SEM_PADRAO = PadraoInteiros(0, 0, 0, 1)


@dataclass(frozen=True, slots=True)
class MedicaoFormato:
    proporcao_decimais: float
    padrao: PadraoInteiros

    @property
    def p_valor(self) -> float:
        """Chance de aparecer um padrão assim por acaso (Poisson)."""
        return estatistica.teste_poisson_unilateral(1, self.padrao.esperados)


def _sequencias_iguais(valores: np.ndarray) -> list[tuple[int, int, int]]:
    """(início, tamanho, valor) de cada sequência de valores iguais seguidos."""
    if len(valores) == 0:
        return []
    inicios = np.concatenate(([0], np.flatnonzero(np.diff(valores) != 0) + 1))
    tamanhos = np.diff(np.concatenate((inicios, [len(valores)])))
    return [(int(i), int(t), int(valores[i])) for i, t in zip(inicios, tamanhos, strict=True)]


def _forma_padrao(passo: int, repeticoes: int) -> bool:
    if passo == 1:
        return repeticoes + 1 >= MINIMO_SEGUIDOS
    return repeticoes >= MINIMO_REPETICOES_PASSO


def _esperados(inteiros: int, chance: float, passo: int, repeticoes: int) -> float:
    """Com cada valor inteiro ao acaso (chance q): nº de inteiros · P(intervalo = passo)^r."""
    return inteiros * ((1 - chance) ** (passo - 1) * chance) ** repeticoes


def padrao_dos_inteiros(inteiros: np.ndarray) -> PadraoInteiros:
    """O grupo de inteiros seguidos ou a passo constante mais improvável ao acaso."""
    posicoes = np.flatnonzero(inteiros)
    chance = float(inteiros.mean())
    candidatos = [
        PadraoInteiros(
            int(posicoes[i]),
            int(posicoes[i + t]),
            t + 1,
            passo,
            _esperados(len(posicoes), chance, passo, t),
        )
        for i, t, passo in _sequencias_iguais(np.diff(posicoes))
        if _forma_padrao(passo, t)
    ]
    return min(candidatos, key=lambda p: p.esperados, default=SEM_PADRAO)


class RegraFormato(base.RegraBase[base.AlvoColuna, MedicaoFormato]):
    """≥ 80% com decimais e inteiros agrupados ou regulares, improváveis ao acaso (p < 0,01)."""

    codigo = "R3"
    nome = "Formato numérico"
    seletor = base.COLUNAS_CONTINUAS
    requisito = base.MinimoDeValores(MINIMO_VALORES)

    def medir(self, alvo: base.AlvoColuna) -> MedicaoFormato:
        inteiros = np.abs(alvo.valores - np.round(alvo.valores)) < TOLERANCIA
        return MedicaoFormato(1 - float(inteiros.mean()), padrao_dos_inteiros(inteiros))

    def dispara(self, medicao: MedicaoFormato) -> bool:
        decimais = medicao.proporcao_decimais >= MINIMO_DECIMAIS
        return decimais and medicao.padrao.encontrado and medicao.p_valor < base.LIMIAR_P

    def conteudo_aviso(self, alvo: base.AlvoColuna, medicao: MedicaoFormato) -> base.ConteudoAviso:
        padrao = medicao.padrao
        posicoes = padrao.posicoes
        linhas = (int(alvo.linhas[padrao.inicio]), int(alvo.linhas[padrao.fim]))
        return base.ConteudoAviso(
            severidade=Severidade.ATENCAO,
            colunas=(alvo.nome,),
            textos=textos.r03_textos(
                alvo.nome, medicao.proporcao_decimais, padrao.quantidade, padrao.passo, linhas
            ),
            exemplo=exemplo_de_valores(alvo.linhas[posicoes], alvo.valores[posicoes]),
            detalhes=textos.r03_detalhes(
                medicao.proporcao_decimais, padrao.quantidade, padrao.passo, medicao.p_valor
            ),
        )
