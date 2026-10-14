"""R8 — Lei de Benford: 1º dígito × log₁₀(1 + 1/d), χ² (gl = 8) e MAD de Nigrini (spec 12)."""

from dataclasses import dataclass

import numpy as np

from app.compartilhado import estatistica
from app.compartilhado.estatistica import ResultadoQuiQuadrado
from app.dominios.detector import digitos, textos
from app.dominios.detector.regras.base import (
    COLUNAS_NUMERICAS,
    LIMIAR_P,
    AlvoColuna,
    ConteudoAviso,
    RegraBase,
    conteudo_da_coluna,
)

MINIMO_POSITIVOS = 100
MINIMO_RAZAO_MAX_MIN = 100
"""Duas ordens de grandeza entre o maior e o menor valor positivo."""
LIMITE_MAD = 0.015
DIGITOS = np.arange(1, 10)
BENFORD = np.log10(1 + 1 / DIGITOS)


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoBenford:
    positivos: np.ndarray
    """Máscara dos valores maiores que zero (os que entram na contagem)."""
    primeiros: np.ndarray
    proporcoes: np.ndarray
    teste: ResultadoQuiQuadrado

    @property
    def mad(self) -> float:
        return float(np.mean(np.abs(self.proporcoes - BENFORD)))

    @property
    def indice_mais_acima(self) -> int:
        """Posição (0 a 8) do dígito que mais passa do esperado."""
        return int(np.argmax(self.proporcoes - BENFORD))


class RegraBenford(RegraBase[AlvoColuna, MedicaoBenford]):
    """Não conformidade: p < 0,01 e MAD > 0,015 (só valores positivos, n ≥ 100)."""

    codigo = "R8"
    nome = "Lei de Benford"
    motivo_sem_alvos = textos.SEM_NUMERICAS
    seletor = COLUNAS_NUMERICAS

    def motivo_nao_aplicavel(self, alvo: AlvoColuna) -> str | None:
        if np.any(alvo.valores < 0):
            return textos.VALORES_NEGATIVOS
        positivos = alvo.valores[alvo.valores > 0]
        if len(positivos) < MINIMO_POSITIVOS:
            return textos.poucos_positivos(MINIMO_POSITIVOS, len(positivos))
        if positivos.max() < MINIMO_RAZAO_MAX_MIN * positivos.min():
            return textos.POUCAS_ORDENS
        return None

    def medir(self, alvo: AlvoColuna) -> MedicaoBenford:
        positivos = alvo.valores > 0
        primeiros = digitos.primeiros_digitos(alvo.valores[positivos])
        contagens = np.bincount(primeiros, minlength=10)[DIGITOS]
        teste = estatistica.teste_qui_quadrado(contagens, len(primeiros) * BENFORD)
        return MedicaoBenford(positivos, primeiros, contagens / len(primeiros), teste)

    def dispara(self, medicao: MedicaoBenford) -> bool:
        return medicao.teste.p_valor < LIMIAR_P and medicao.mad > LIMITE_MAD

    def conteudo_aviso(self, alvo: AlvoColuna, medicao: MedicaoBenford) -> ConteudoAviso:
        indice = medicao.indice_mais_acima
        digito = int(DIGITOS[indice])
        marcas = np.zeros(alvo.n, dtype=bool)
        marcas[medicao.positivos] = medicao.primeiros == digito
        return conteudo_da_coluna(
            alvo,
            textos.r08_textos(
                alvo.nome, digito, float(medicao.proporcoes[indice]), float(BENFORD[indice])
            ),
            textos.r08_detalhes(medicao.mad, medicao.teste.p_valor),
            marcas,
        )
