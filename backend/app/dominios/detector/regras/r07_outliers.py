"""R7 — Valores distantes: cercas de Tukey (1,5·IQR e 3·IQR) e escore z (spec 12, D128).

Moderado = fora de 1,5·IQR ou |z| > 3 (informativo); extremo = fora de 3·IQR (atenção). As
cercas se alargam do lado da cauda longa (boxplot ajustado de Hubert e Vandervieren, D136):
valores de dinheiro e rajadas de vento têm cauda longa sem que a ponta seja erro.
"""

import math
from dataclasses import dataclass

import numpy as np

from app.compartilhado import estatistica
from app.compartilhado.tipos import Severidade
from app.dominios.detector import textos
from app.dominios.detector.exemplos import exemplo_de_valores
from app.dominios.detector.regras import base

MINIMO_VALORES = 10
FATOR_MODERADO = 1.5
FATOR_EXTREMO = 3.0
Z_DISTANTE = 3.0
QUARTIS = (0.25, 0.75)
EXPOENTE_CAUDA = 3.0
EXPOENTE_OUTRO_LADO = 4.0


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoDistantes:
    """Quartis, máscaras de moderados e extremos e o escore z de cada valor."""

    q1: float
    q3: float
    mc: float
    """Medcouple: a assimetria que alarga as cercas."""
    z: np.ndarray
    moderados: np.ndarray
    extremos: np.ndarray

    @property
    def distantes(self) -> np.ndarray:
        return np.asarray(self.moderados | self.extremos, dtype=bool)

    def cercas(self, fator: float) -> tuple[float, float]:
        return _cercas(self.q1, self.q3, fator, self.mc)


def _cercas(q1: float, q3: float, fator: float, mc: float) -> tuple[float, float]:
    """[Q1 − fator·e^(−4·MC)·IQR, Q3 + fator·e^(3·MC)·IQR] com MC ≥ 0 (espelhado com MC < 0).

    Só alarga: cada lado fica no mínimo em Q1 − fator·IQR e Q3 + fator·IQR (Tukey).
    """
    iqr = q3 - q1
    cauda_acima = math.exp(EXPOENTE_CAUDA * mc) if mc >= 0 else math.exp(EXPOENTE_OUTRO_LADO * mc)
    cauda_abaixo = (
        math.exp(-EXPOENTE_OUTRO_LADO * mc) if mc >= 0 else math.exp(-EXPOENTE_CAUDA * mc)
    )
    return (
        q1 - fator * max(1.0, cauda_abaixo) * iqr,
        q3 + fator * max(1.0, cauda_acima) * iqr,
    )


def _fora(valores: np.ndarray, cercas: tuple[float, float]) -> np.ndarray:
    return (valores < cercas[0]) | (valores > cercas[1])


def _quartis(valores: np.ndarray) -> tuple[float, float]:
    q1, q3 = np.quantile(valores, QUARTIS)
    return float(q1), float(q3)


def _centro_varia(alvo: base.AlvoColuna) -> str | None:
    q1, q3 = _quartis(alvo.valores)
    return textos.METADE_CENTRAL_IGUAL if q1 == q3 else None


class RegraOutliers(base.RegraBase[base.AlvoColuna, MedicaoDistantes]):
    """Moderado (fora de 1,5·IQR ou |z| > 3) → informativo; extremo (3·IQR) → atenção."""

    codigo = "R7"
    nome = "Valores distantes"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.Todos(
        (base.MinimoDeValores(MINIMO_VALORES), base.valores_variam, _centro_varia)
    )

    def medir(self, alvo: base.AlvoColuna) -> MedicaoDistantes:
        valores = alvo.valores
        q1, q3 = _quartis(valores)
        mc = estatistica.medcouple(valores)
        z = (valores - valores.mean()) / valores.std(ddof=1)
        # |z| > 3 sozinho é moderado: numa Normal de 500 valores ele aparece em 73% das amostras.
        extremos = _fora(valores, _cercas(q1, q3, FATOR_EXTREMO, mc))
        distantes = _fora(valores, _cercas(q1, q3, FATOR_MODERADO, mc)) | (np.abs(z) > Z_DISTANTE)
        moderados = distantes & ~extremos
        return MedicaoDistantes(q1, q3, mc, z, moderados, extremos)

    def dispara(self, medicao: MedicaoDistantes) -> bool:
        return bool(medicao.distantes.any())

    def conteudo_aviso(
        self, alvo: base.AlvoColuna, medicao: MedicaoDistantes
    ) -> base.ConteudoAviso:
        distantes = medicao.distantes
        mais_longe = int(np.argmax(np.where(distantes, np.abs(medicao.z), -np.inf)))
        exemplo = float(alvo.valores[mais_longe])
        baixo, alto = medicao.cercas(FATOR_MODERADO)
        extremos = int(medicao.extremos.sum())
        return base.ConteudoAviso(
            severidade=Severidade.ATENCAO if extremos else Severidade.INFO,
            colunas=(alvo.nome,),
            textos=textos.r07_textos(
                alvo.nome, int(distantes.sum()), exemplo, alto if exemplo > medicao.q3 else baixo
            ),
            exemplo=exemplo_de_valores(alvo.linhas[distantes], alvo.valores[distantes]),
            detalhes=textos.r07_detalhes(
                int(medicao.moderados.sum()),
                extremos,
                (baixo, alto, *medicao.cercas(FATOR_EXTREMO)),
                medicao.mc,
            ),
        )
