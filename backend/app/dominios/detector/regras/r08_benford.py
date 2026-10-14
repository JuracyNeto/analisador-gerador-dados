"""R8 — Lei de Benford: 1º dígito × log₁₀(1 + 1/d), χ² (gl = 8) e MAD de Nigrini (spec 12)."""

from dataclasses import replace

import numpy as np

from app.dominios.detector import digitos, textos
from app.dominios.detector.digitos import FrequenciaDigitos
from app.dominios.detector.regras import base

MINIMO_POSITIVOS = 100
MINIMO_RAZAO_ORDENS = 100
"""Duas ordens de grandeza entre P99 e P1 dos positivos (robusto a valores digitados errado)."""
PONTAS = (0.01, 0.99)
LIMITE_MAD = 0.015
PRIMEIROS_POSSIVEIS = np.arange(1, 10)
BENFORD = np.log10(1 + 1 / PRIMEIROS_POSSIVEIS)


def _sem_negativos(alvo: base.AlvoColuna) -> str | None:
    return textos.VALORES_NEGATIVOS if np.any(alvo.valores < 0) else None


def _positivos_suficientes(alvo: base.AlvoColuna) -> str | None:
    n = int(np.count_nonzero(alvo.valores > 0))
    return textos.poucos_positivos(MINIMO_POSITIVOS, n) if n < MINIMO_POSITIVOS else None


def _varias_ordens(alvo: base.AlvoColuna) -> str | None:
    baixo, alto = np.quantile(alvo.valores[alvo.valores > 0], PONTAS)
    return textos.POUCAS_ORDENS if alto < MINIMO_RAZAO_ORDENS * baixo else None


class RegraBenford(base.RegraBase[base.AlvoColuna, FrequenciaDigitos]):
    """Não conformidade: p < 0,01 e MAD > 0,015 (positivos, n ≥ 100, P99/P1 ≥ 100; D119)."""

    codigo = "R8"
    nome = "Lei de Benford"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.Todos((_sem_negativos, _positivos_suficientes, _varias_ordens))

    def medir(self, alvo: base.AlvoColuna) -> FrequenciaDigitos:
        primeiros = digitos.primeiros_digitos(alvo.valores[alvo.valores > 0])
        return digitos.comparar_frequencias(primeiros, PRIMEIROS_POSSIVEIS, BENFORD)

    def dispara(self, medicao: FrequenciaDigitos) -> bool:
        return medicao.teste.p_valor < base.LIMIAR_P and medicao.mad > LIMITE_MAD

    def conteudo_aviso(
        self, alvo: base.AlvoColuna, medicao: FrequenciaDigitos
    ) -> base.ConteudoAviso:
        indice = medicao.indice_mais_acima
        marcas = np.zeros(alvo.n, dtype=bool)
        marcas[alvo.valores > 0] = medicao.observados == medicao.mais_acima
        conteudo = base.conteudo_da_coluna(
            alvo,
            textos.r08_textos(
                alvo.nome,
                medicao.mais_acima,
                float(medicao.proporcoes[indice]),
                float(BENFORD[indice]),
            ),
            textos.r08_detalhes(medicao.mad, medicao.teste.p_valor),
            marcas,
        )
        return replace(conteudo, grafico=medicao.grafico(alvo.nome, "primeiro"))
