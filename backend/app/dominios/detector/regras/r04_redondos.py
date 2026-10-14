"""R4 — Valores redondos: terminados em 0 ou 5 e em 0, no último dígito (spec 12, D119)."""

from dataclasses import dataclass

import numpy as np

from app.compartilhado import estatistica
from app.dominios.detector import digitos, textos
from app.dominios.detector.regras.base import (
    COLUNAS_NUMERICAS,
    LIMIAR_P,
    AlvoColuna,
    ConteudoAviso,
    RegraBase,
    conteudo_da_coluna,
)

MINIMO_VALORES = 50
RAZAO_MINIMA = 1.5


@dataclass(frozen=True, slots=True)
class Arredondamento:
    """Múltiplos de 5 (final 0 ou 5, esperado 20%) ou de 10 (final 0, esperado 10%)."""

    multiplo: int
    finais: tuple[int, ...]
    esperado: float


ARREDONDAMENTOS = (Arredondamento(5, (0, 5), 0.2), Arredondamento(10, (0,), 0.1))


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoRedondos:
    arredondamento: Arredondamento
    casas: int
    redondos: np.ndarray
    p_valor: float

    @property
    def k(self) -> int:
        return int(self.redondos.sum())

    @property
    def proporcao(self) -> float:
        return self.k / len(self.redondos)

    @property
    def razao(self) -> float:
        return self.proporcao / self.arredondamento.esperado

    @property
    def acima_do_esperado(self) -> bool:
        return self.p_valor < LIMIAR_P and self.razao >= RAZAO_MINIMA


def _medir(finais: np.ndarray, casas: int, arredondamento: Arredondamento) -> MedicaoRedondos:
    redondos = np.isin(finais, arredondamento.finais)
    k = int(redondos.sum())
    p = estatistica.teste_binomial_unilateral(k, len(finais), arredondamento.esperado)
    return MedicaoRedondos(arredondamento, casas, redondos, p)


class RegraRedondos(RegraBase[AlvoColuna, MedicaoRedondos]):
    """Binomial unilateral p < 0,01 e pelo menos 1,5× o esperado; avisa o mais forte."""

    codigo = "R4"
    nome = "Valores redondos"
    motivo_sem_alvos = textos.SEM_NUMERICAS
    seletor = COLUNAS_NUMERICAS

    def motivo_nao_aplicavel(self, alvo: AlvoColuna) -> str | None:
        return digitos.motivo_digito_final(alvo.valores, MINIMO_VALORES)

    def medir(self, alvo: AlvoColuna) -> MedicaoRedondos:
        casas = digitos.resolucao(alvo.valores)
        finais = digitos.digitos_finais(alvo.valores, casas)
        medicoes = [_medir(finais, casas, tipo) for tipo in ARREDONDAMENTOS]
        return min(medicoes, key=lambda m: (not m.acima_do_esperado, m.p_valor))

    def dispara(self, medicao: MedicaoRedondos) -> bool:
        return medicao.acima_do_esperado

    def conteudo_aviso(self, alvo: AlvoColuna, medicao: MedicaoRedondos) -> ConteudoAviso:
        tipo = medicao.arredondamento
        passo = tipo.multiplo / 10**medicao.casas
        return conteudo_da_coluna(
            alvo,
            textos.r04_textos(alvo.nome, medicao.proporcao, tipo.esperado, tipo.multiplo, passo),
            textos.r04_detalhes(tipo.multiplo, medicao.k, alvo.n, tipo.esperado, medicao.p_valor),
            medicao.redondos,
        )
