"""R8 — Lei de Benford: 1º dígito × log₁₀(1 + 1/d), χ² (gl = 8) e MAD de Nigrini (spec 12).

Contam os positivos a partir de 10 passos do instrumento (D145): abaixo disso, a grade do
instrumento decide o 1º dígito (chuva de 0,2 em 0,2 mm abre com 2, 4, 6 ou 8 abaixo de 1 mm).
"""

from dataclasses import dataclass, replace

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
PASSOS_MINIMOS = 10
"""O 1º dígito é livre a partir de 10 passos do instrumento (D145)."""


@dataclass(frozen=True, slots=True, eq=False)
class Contados:
    """Os positivos que entram na contagem (marcas na ordem da coluna) e o passo do instrumento."""

    marcas: np.ndarray
    passo: float
    pequenos: int
    """Positivos abaixo de 10 passos, fora da contagem."""

    @property
    def limite(self) -> float:
        return PASSOS_MINIMOS * self.passo

    def motivo(self, motivo: str | None) -> str | None:
        """O motivo diz o limite quando valores perto do passo saíram."""
        if motivo is None or not self.pequenos:
            return motivo
        return textos.fora_os_pequenos(motivo, PASSOS_MINIMOS, self.passo)


def contados(valores: np.ndarray) -> Contados:
    """Positivos a partir de 10 passos (o maior divisor comum dos valores na precisão, D134)."""
    positivos = valores > 0
    if not positivos.any():
        return Contados(positivos, 0.0, 0)
    casas = digitos.resolucao(valores[positivos])
    passo = digitos.passo_da_medida(valores[positivos], casas)
    marcas = positivos & (np.round(valores * 10**casas) >= PASSOS_MINIMOS * passo)
    return Contados(marcas, passo / 10**casas, int(positivos.sum() - marcas.sum()))


def _sem_negativos(alvo: base.AlvoColuna) -> str | None:
    return textos.VALORES_NEGATIVOS if np.any(alvo.valores < 0) else None


def _positivos_suficientes(alvo: base.AlvoColuna) -> str | None:
    usados = contados(alvo.valores)
    n = int(usados.marcas.sum())
    poucos = textos.poucos_positivos(MINIMO_POSITIVOS, n) if n < MINIMO_POSITIVOS else None
    return usados.motivo(poucos)


def _varias_ordens(alvo: base.AlvoColuna) -> str | None:
    usados = contados(alvo.valores)
    baixo, alto = np.quantile(alvo.valores[usados.marcas], PONTAS)
    return usados.motivo(textos.POUCAS_ORDENS if alto < MINIMO_RAZAO_ORDENS * baixo else None)


class RegraBenford(base.RegraBase[base.AlvoColuna, FrequenciaDigitos]):
    """Não conformidade: p < 0,01 e MAD > 0,015 (positivos, n ≥ 100, P99/P1 ≥ 100; D119)."""

    codigo = "R8"
    nome = "Lei de Benford"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.Todos((_sem_negativos, _positivos_suficientes, _varias_ordens))

    def medir(self, alvo: base.AlvoColuna) -> FrequenciaDigitos:
        primeiros = digitos.primeiros_digitos(alvo.valores[contados(alvo.valores).marcas])
        return digitos.comparar_frequencias(primeiros, PRIMEIROS_POSSIVEIS, BENFORD)

    def dispara(self, medicao: FrequenciaDigitos) -> bool:
        return medicao.teste.p_valor < base.LIMIAR_P and medicao.mad > LIMITE_MAD

    def conteudo_aviso(
        self, alvo: base.AlvoColuna, medicao: FrequenciaDigitos
    ) -> base.ConteudoAviso:
        indice = medicao.indice_mais_acima
        usados = contados(alvo.valores)
        marcas = np.zeros(alvo.n, dtype=bool)
        marcas[usados.marcas] = medicao.observados == medicao.mais_acima
        conteudo = base.conteudo_da_coluna(
            alvo,
            textos.r08_textos(
                alvo.nome,
                medicao.mais_acima,
                float(medicao.proporcoes[indice]),
                float(BENFORD[indice]),
            ),
            textos.r08_detalhes(medicao.mad, medicao.teste.p_valor, usados.pequenos, usados.limite),
            marcas,
        )
        return replace(conteudo, grafico=medicao.grafico(alvo.nome, "primeiro"))
