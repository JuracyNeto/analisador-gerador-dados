"""R10 — Normal perfeita demais: |G₁| < 0,05, |G₂| < 0,1 e p > 0,99 (spec 12, D122).

G₁, G₂ e o p (Shapiro-Wilk até 5.000 valores; acima, D'Agostino) vêm da análise, calculados
pelo serviço na tabela (D108). Com p > 0,9 (spec), 3,7% das amostras Normais sorteadas
disparavam (até 7%); com 0,99, 0,4% — e valores tirados da curva continuam com p = 1.
"""

from app.compartilhado.tipos import Severidade
from app.dominios.detector import textos_blocos
from app.dominios.detector.regras import base
from app.dominios.detector.tabela import FormaColuna

MINIMO_VALORES = 200
LIMITE_ASSIMETRIA = 0.05
LIMITE_CURTOSE = 0.1
P_MINIMO = 0.99
SEM_FORMA = FormaColuna(float("nan"), float("nan"), "", 0.0)
"""Objeto nulo: coluna sem forma calculada (o serviço só calcula nas contínuas) não dispara."""


class RegraNormalPerfeita(base.RegraBase[base.AlvoColuna, FormaColuna]):
    """Forma idêntica à da Normal e aderência quase total → informativo."""

    codigo = "R10"
    nome = "Normal perfeita demais"
    seletor = base.COLUNAS_CONTINUAS
    requisito = base.Todos((base.MinimoDeValores(MINIMO_VALORES), base.valores_variam))

    def medir(self, alvo: base.AlvoColuna) -> FormaColuna:
        return alvo.forma or SEM_FORMA

    def dispara(self, medicao: FormaColuna) -> bool:
        return (
            abs(medicao.assimetria) < LIMITE_ASSIMETRIA
            and abs(medicao.curtose) < LIMITE_CURTOSE
            and medicao.p_normalidade > P_MINIMO
        )

    def conteudo_aviso(self, alvo: base.AlvoColuna, medicao: FormaColuna) -> base.ConteudoAviso:
        return base.ConteudoAviso(
            severidade=Severidade.INFO,
            colunas=(alvo.nome,),
            textos=textos_blocos.r10_textos(alvo.nome, medicao.assimetria, medicao.curtose),
            exemplo=None,
            detalhes=textos_blocos.r10_detalhes(
                medicao.assimetria, medicao.curtose, medicao.teste, medicao.p_normalidade
            ),
        )
