"""R9 — Último dígito: qui-quadrado de uniformidade dos dígitos finais (spec 12, D119)."""

from dataclasses import replace

import numpy as np

from app.dominios.detector import digitos, textos
from app.dominios.detector.digitos import FrequenciaDigitos
from app.dominios.detector.regras import base

MINIMO_VALORES = 50
FINAIS_POSSIVEIS = np.arange(10)
ESPERADO = 0.1
UNIFORME = np.full(10, ESPERADO)


class RegraUltimoDigito(base.RegraBase[base.AlvoColuna, FrequenciaDigitos]):
    """Dígitos finais 0–9 deveriam ser uniformes; χ² p < 0,01 e o mais comum ≥ 15% (D134)."""

    codigo = "R9"
    nome = "Último dígito"
    seletor = base.NUMERICAS_SEM_ZEROS
    requisito = base.DigitoFinalTestavel(MINIMO_VALORES)

    def medir(self, alvo: base.AlvoColuna) -> FrequenciaDigitos:
        finais = digitos.digitos_finais(alvo.valores, digitos.resolucao(alvo.valores))
        return digitos.comparar_frequencias(finais, FINAIS_POSSIVEIS, UNIFORME)

    def dispara(self, medicao: FrequenciaDigitos) -> bool:
        # Com milhares de valores, um excesso pequeno (13% contra 10%) já passa no teste (D134).
        mais_comum = float(medicao.proporcoes[medicao.indice_mais_acima])
        efeito = mais_comum >= digitos.RAZAO_MINIMA * ESPERADO
        return medicao.teste.p_valor < base.LIMIAR_P and efeito

    def conteudo_aviso(
        self, alvo: base.AlvoColuna, medicao: FrequenciaDigitos
    ) -> base.ConteudoAviso:
        digito = medicao.mais_acima
        proporcao = float(medicao.proporcoes[medicao.indice_mais_acima])
        conteudo = base.conteudo_da_coluna(
            alvo,
            textos.r09_textos(alvo.nome, digito, proporcao),
            textos.r09_detalhes(digito, proporcao, medicao.teste.p_valor),
            medicao.observados == digito,
        )
        return replace(conteudo, grafico=medicao.grafico(alvo.nome, "ultimo"))
