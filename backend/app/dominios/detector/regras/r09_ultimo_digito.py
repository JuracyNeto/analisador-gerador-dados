"""R9 — Último dígito: qui-quadrado de uniformidade dos dígitos finais (spec 12, D119)."""

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

MINIMO_VALORES = 50
N_DIGITOS = 10


@dataclass(frozen=True, slots=True, eq=False)
class MedicaoUltimoDigito:
    finais: np.ndarray
    contagens: np.ndarray
    teste: ResultadoQuiQuadrado

    @property
    def mais_frequente(self) -> int:
        return int(np.argmax(self.contagens))

    @property
    def proporcao(self) -> float:
        return float(self.contagens[self.mais_frequente] / len(self.finais))


class RegraUltimoDigito(RegraBase[AlvoColuna, MedicaoUltimoDigito]):
    """Dígitos finais 0–9 deveriam ser uniformes; χ² com gl = 9 e p < 0,01."""

    codigo = "R9"
    nome = "Último dígito"
    motivo_sem_alvos = textos.SEM_NUMERICAS
    seletor = COLUNAS_NUMERICAS

    def motivo_nao_aplicavel(self, alvo: AlvoColuna) -> str | None:
        return digitos.motivo_digito_final(alvo.valores, MINIMO_VALORES)

    def medir(self, alvo: AlvoColuna) -> MedicaoUltimoDigito:
        finais = digitos.digitos_finais(alvo.valores, digitos.resolucao(alvo.valores))
        contagens = np.bincount(finais, minlength=N_DIGITOS)
        esperados = np.full(N_DIGITOS, len(finais) / N_DIGITOS)
        return MedicaoUltimoDigito(
            finais, contagens, estatistica.teste_qui_quadrado(contagens, esperados)
        )

    def dispara(self, medicao: MedicaoUltimoDigito) -> bool:
        return medicao.teste.p_valor < LIMIAR_P

    def conteudo_aviso(self, alvo: AlvoColuna, medicao: MedicaoUltimoDigito) -> ConteudoAviso:
        digito = medicao.mais_frequente
        return conteudo_da_coluna(
            alvo,
            textos.r09_textos(alvo.nome, digito, medicao.proporcao),
            textos.r09_detalhes(digito, medicao.proporcao, medicao.teste.p_valor),
            medicao.finais == digito,
        )
