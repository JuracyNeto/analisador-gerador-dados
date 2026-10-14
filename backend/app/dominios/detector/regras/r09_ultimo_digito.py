"""R9 — Último dígito: qui-quadrado de uniformidade dos dígitos finais (spec 12, D119)."""

import numpy as np

from app.dominios.detector import digitos, textos
from app.dominios.detector.digitos import FrequenciaDigitos
from app.dominios.detector.regras import base

MINIMO_VALORES = 50
FINAIS_POSSIVEIS = np.arange(10)
UNIFORME = np.full(10, 0.1)


class RegraUltimoDigito(base.RegraBase[base.AlvoColuna, FrequenciaDigitos]):
    """Dígitos finais 0–9 deveriam ser uniformes; χ² com gl = 9 e p < 0,01."""

    codigo = "R9"
    nome = "Último dígito"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.DigitoFinalTestavel(MINIMO_VALORES)

    def medir(self, alvo: base.AlvoColuna) -> FrequenciaDigitos:
        finais = digitos.digitos_finais(alvo.valores, digitos.resolucao(alvo.valores))
        return digitos.comparar_frequencias(finais, FINAIS_POSSIVEIS, UNIFORME)

    def dispara(self, medicao: FrequenciaDigitos) -> bool:
        return medicao.teste.p_valor < base.LIMIAR_P

    def conteudo_aviso(
        self, alvo: base.AlvoColuna, medicao: FrequenciaDigitos
    ) -> base.ConteudoAviso:
        digito = medicao.mais_acima
        proporcao = float(medicao.proporcoes[medicao.indice_mais_acima])
        return base.conteudo_da_coluna(
            alvo,
            textos.r09_textos(alvo.nome, digito, proporcao),
            textos.r09_detalhes(digito, proporcao, medicao.teste.p_valor),
            medicao.observados == digito,
        )
