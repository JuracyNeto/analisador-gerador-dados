"""R11 — Sequência: a ordem dos valores segue um padrão (spec 12).

Três medidas na ordem das linhas: runs acima/abaixo da mediana (Wald-Wolfowitz; os iguais à
mediana saem), progressões aritméticas (5 diferenças iguais e não nulas seguidas, na precisão da
coluna) e autocorrelação lag-1. Progressões contam quando passam do acaso: com valores
sorteados, 6 seguidos em progressão têm chance de no máximo p_max⁴ (p_max = frequência do valor
mais comum), então esperadas = (n − 5) · p_max⁴ (Poisson, p < 0,01) — como na R3 (D121).
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from app.compartilhado import estatistica
from app.compartilhado.estatistica import ResultadoRuns
from app.compartilhado.tipos import Severidade
from app.dominios.detector import blocos, digitos, textos_blocos
from app.dominios.detector.regras import base

MINIMO_VALORES = 30
MINIMO_DIFERENCAS = 5
LIMITE_AUTOCORRELACAO = 0.8


@dataclass(frozen=True, slots=True)
class Progressoes:
    """Quantas progressões há, onde está a maior e quantas o acaso daria."""

    quantidade: int
    inicio: int
    tamanho: int
    """Valores da maior progressão (diferenças + 1)."""
    esperadas: float

    @property
    def p_valor(self) -> float:
        return estatistica.teste_poisson_unilateral(self.quantidade, self.esperadas)


def progressoes(valores: np.ndarray) -> Progressoes:
    """Trechos de 5 diferenças iguais e não nulas seguidas, na precisão da coluna."""
    casas = digitos.resolucao(valores)
    diferencas = np.round(np.diff(valores), casas)
    inicios, tamanhos = blocos.trechos_iguais(diferencas)
    longas = (tamanhos >= MINIMO_DIFERENCAS) & (diferencas[inicios] != 0)
    _, contagens = np.unique(np.round(valores, casas), return_counts=True)
    mais_comum = contagens.max() / len(valores)
    esperadas = (len(valores) - MINIMO_DIFERENCAS) * mais_comum ** (MINIMO_DIFERENCAS - 1)
    if not longas.any():
        return Progressoes(0, 0, 0, esperadas)
    maior = int(np.argmax(np.where(longas, tamanhos, -1)))
    return Progressoes(int(longas.sum()), int(inicios[maior]), int(tamanhos[maior]) + 1, esperadas)


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoSequencia:
    runs: ResultadoRuns
    progressoes: Progressoes
    autocorrelacao: float
    lados: np.ndarray
    """+1 acima da mediana, −1 abaixo, 0 igual a ela (na ordem das linhas)."""

    @property
    def padrao(self) -> str | None:
        """O padrão mais específico: progressão, depois autocorrelação, depois runs."""
        if self.progressoes.quantidade and self.progressoes.p_valor < base.LIMIAR_P:
            return "progressao"
        if abs(self.autocorrelacao) > LIMITE_AUTOCORRELACAO:
            return "parecidos" if self.autocorrelacao > 0 else "alterna"
        if self.runs.p_valor < base.LIMIAR_P:
            return "alterna" if self.runs.z > 0 else "sequencias"
        return None


def _marcas_progressao(medicao: MedicaoSequencia) -> np.ndarray:
    marcas = np.zeros(len(medicao.lados), dtype=bool)
    inicio = medicao.progressoes.inicio
    marcas[inicio : inicio + medicao.progressoes.tamanho] = True
    return marcas


def _marcas_parecidos(medicao: MedicaoSequencia) -> np.ndarray:
    return np.ones(len(medicao.lados), dtype=bool)


def _marcas_alterna(medicao: MedicaoSequencia) -> np.ndarray:
    """Valores do lado oposto ao do anterior (e esse anterior)."""
    lados = medicao.lados
    trocas = lados[1:] * lados[:-1] == -1
    marcas = np.zeros(len(lados), dtype=bool)
    marcas[1:] |= trocas
    marcas[:-1] |= trocas
    return marcas


def _marcas_sequencias(medicao: MedicaoSequencia) -> np.ndarray:
    """A maior sequência de valores do mesmo lado da mediana."""
    inicios, tamanhos = blocos.trechos_iguais(medicao.lados)
    maior = int(np.argmax(np.where(medicao.lados[inicios] != 0, tamanhos, -1)))
    marcas = np.zeros(len(medicao.lados), dtype=bool)
    marcas[inicios[maior] : inicios[maior] + tamanhos[maior]] = True
    return marcas


MARCAS: dict[str, Callable[[MedicaoSequencia], np.ndarray]] = {
    "progressao": _marcas_progressao,
    "parecidos": _marcas_parecidos,
    "alterna": _marcas_alterna,
    "sequencias": _marcas_sequencias,
}


def _p_do_padrao(medicao: MedicaoSequencia, padrao: str) -> float | None:
    """p do teste que mostra o padrão (a autocorrelação não tem teste)."""
    if padrao == "progressao":
        return medicao.progressoes.p_valor
    return None if padrao == "parecidos" else medicao.runs.p_valor


def _severidade(alvo: base.AlvoColuna) -> Severidade:
    """Numa série no tempo, qualquer padrão é informativo: a ordem não é aleatória (D137)."""
    return Severidade.ATENCAO if alvo.linha_do_tempo is None else Severidade.INFO


class RegraSequencia(base.RegraBase[base.AlvoColuna, MedicaoSequencia]):
    """Runs p < 0,01, progressão além do acaso ou |ρ₁| > 0,8 → atenção (série no tempo: info)."""

    codigo = "R11"
    nome = "Sequência"
    seletor = base.NaLinhaDoTempo(base.COLUNAS_NUMERICAS)
    requisito = base.Todos((base.MinimoDeValores(MINIMO_VALORES), base.valores_variam))

    def medir(self, alvo: base.AlvoColuna) -> MedicaoSequencia:
        valores = alvo.valores
        lados = np.sign(valores - np.median(valores))
        return MedicaoSequencia(
            runs=estatistica.teste_runs(lados[lados != 0] > 0),
            progressoes=progressoes(valores),
            autocorrelacao=estatistica.autocorrelacao_lag1(valores),
            lados=lados,
        )

    def dispara(self, medicao: MedicaoSequencia) -> bool:
        return medicao.padrao is not None

    def conteudo_aviso(
        self, alvo: base.AlvoColuna, medicao: MedicaoSequencia
    ) -> base.ConteudoAviso:
        padrao = medicao.padrao or ""
        marcas = MARCAS[padrao](medicao)
        posicoes = np.flatnonzero(marcas)
        linhas = (int(alvo.linhas[posicoes[0]]), int(alvo.linhas[posicoes[-1]]))
        medidas = (
            medicao.runs.runs,
            medicao.runs.z,
            medicao.autocorrelacao,
            medicao.progressoes.quantidade,
        )
        escrito = textos_blocos.r11_textos(
            alvo.nome, textos_blocos.r11_padrao(padrao, linhas), alvo.linha_do_tempo
        )
        return base.conteudo_da_coluna(
            alvo,
            escrito,
            textos_blocos.r11_detalhes(medidas, padrao, _p_do_padrao(medicao, padrao)),
            marcas,
            _severidade(alvo),
        )
