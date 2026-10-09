"""Textos da forma e das distribuições: motivos, frases e cálculos (spec 09, spec 16)."""

from app.compartilhado.estatistica import ALFA
from app.compartilhado.numeros import formatar_numero, formatar_p_valor
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.resultados import (
    ClasseAssimetria,
    ClasseCurtose,
    Sentido,
    TesteAderencia,
)
from app.dominios.analise.textos import TIPO_LEGIVEL

TESTE_SHAPIRO = "Shapiro-Wilk"
TESTE_DAGOSTINO = "D'Agostino-Pearson K²"
TESTE_QUI_QUADRADO = "Qui-quadrado"
SIMBOLOS_TESTE = {TESTE_SHAPIRO: "W", TESTE_DAGOSTINO: "K²", TESTE_QUI_QUADRADO: "χ²"}

NOMES_FORMA = {
    "forma": "Forma e distribuição",
    "assimetria": "Assimetria",
    "assimetria_pearson_1": "1º coeficiente de Pearson",
    "assimetria_pearson_2": "2º coeficiente de Pearson",
    "curtose": "Curtose",
    "curtose_percentilica": "Curtose percentílica",
    "normal": "Normal",
    "binomial": "Binomial",
}

MOTIVOS_FORMA = {
    "exige_numeros": "as distribuições Normal e Binomial exigem números",
    "categorias": "os valores são categorias",
    "poucos_3": "precisa de pelo menos 3 valores",
    "poucos_4": "precisa de pelo menos 4 valores",
    "sem_variacao": "todos os valores são iguais; não há variação para medir a forma",
    "percentis_iguais": "P10 e P90 são iguais",
    "moda_multipla": "precisa de uma moda única",
    "binomial_continua": "precisa de contagens de sucessos em n tentativas",
    "binomial_nao_contagem": "precisa de contagens inteiras a partir de 0",
    "binomial_zeros": "todos os valores são zero",
    "normal_discreta": "a aproximação pela Normal precisa de pelo menos 30 valores",
    "normal_binaria": "com dois valores, a distribuição é a Bernoulli",
}

FRASES_ASSIMETRIA: dict[tuple[ClasseAssimetria, Sentido], str] = {
    (
        "simetrica",
        "direita",
    ): "Aproximadamente simétrica: a cauda direita é só um pouco mais longa.",
    ("simetrica", "esquerda"): (
        "Aproximadamente simétrica: a cauda esquerda é só um pouco mais longa."
    ),
    ("moderada", "direita"): (
        "Assimetria moderada à direita: há valores altos mais afastados do centro."
    ),
    ("moderada", "esquerda"): (
        "Assimetria moderada à esquerda: há valores baixos mais afastados do centro."
    ),
    ("forte", "direita"): "Assimetria forte à direita: poucos valores muito altos esticam a cauda.",
    ("forte", "esquerda"): (
        "Assimetria forte à esquerda: poucos valores muito baixos esticam a cauda."
    ),
}
SIMETRICA_PERFEITA = "Simétrica: as duas caudas têm o mesmo tamanho."

FRASES_CURTOSE: dict[ClasseCurtose, str] = {
    "mesocurtica": "Mesocúrtica: caudas parecidas com as da Normal.",
    "leptocurtica": (
        "Leptocúrtica: pico mais alto e caudas mais pesadas que a Normal (mais valores extremos)."
    ),
    "platicurtica": "Platicúrtica: mais achatada que a Normal, com poucos valores extremos.",
}

DESCRICOES_ASSIMETRIA: dict[ClasseAssimetria, str] = {
    "simetrica": "aproximadamente simétrica",
    "moderada": "moderadamente assimétrica",
    "forte": "fortemente assimétrica",
}
NOMES_CURTOSE: dict[ClasseCurtose, str] = {
    "mesocurtica": "mesocúrtica",
    "leptocurtica": "leptocúrtica",
    "platicurtica": "platicúrtica",
}

type Assimetria = tuple[ClasseAssimetria, Sentido | None]
type Aderencia = tuple[str, TesteAderencia]


def nao_se_aplica_ao_tipo(item: str, tipo: TipoVariavel, motivo: str) -> str:
    """ "{medida} não se aplica a {tipo}: {motivo}." (spec 16)."""
    return f"{NOMES_FORMA[item]} não se aplica a {TIPO_LEGIVEL[tipo]}: {MOTIVOS_FORMA[motivo]}."


def nao_calculavel(item: str, motivo: str) -> str:
    """Caso de borda numérico: "Curtose não se aplica: precisa de pelo menos 4 valores."."""
    return f"{NOMES_FORMA[item]} não se aplica: {MOTIVOS_FORMA[motivo]}."


def frase_assimetria(classe: ClasseAssimetria, sentido: Sentido | None) -> str:
    """Spec 09: o sinal de G₁ diz de que lado fica a cauda mais longa."""
    if sentido is None:
        return SIMETRICA_PERFEITA
    return FRASES_ASSIMETRIA[(classe, sentido)]


def frase_curtose(classe: ClasseCurtose) -> str:
    return FRASES_CURTOSE[classe]


def frase_aderencia(nome_distribuicao: str, teste: TesteAderencia) -> str:
    """Decisão com α = 0,05 (spec 09)."""
    if teste.compativel:
        return f"Os dados são compatíveis com a distribuição {nome_distribuicao}."
    return f"Os dados se afastam da distribuição {nome_distribuicao}."


def _comparacao_alfa(teste: TesteAderencia) -> str:
    sinal = "≥" if teste.compativel else "<"
    return f"{formatar_p_valor(teste.p_valor)} {sinal} {formatar_numero(ALFA)}"


def calculo_teste(teste: TesteAderencia) -> str:
    """Ex.: "Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05"."""
    partes = [f"{SIMBOLOS_TESTE[teste.nome]} = {formatar_numero(teste.estatistica)}"]
    if teste.gl is not None:
        partes.append(f"gl = {teste.gl}")
    partes.append(_comparacao_alfa(teste))
    return f"{teste.nome}: {' · '.join(partes)}"


def _descrever_assimetria(assimetria: Assimetria) -> str:
    classe, sentido = assimetria
    descricao = DESCRICOES_ASSIMETRIA[classe]
    if classe == "simetrica" or sentido is None:
        return descricao
    return f"{descricao} à {sentido}"


def _descrever_aderencia(aderencia: Aderencia) -> str:
    nome, teste = aderencia
    p = formatar_p_valor(teste.p_valor)
    if teste.compativel:
        return f"compatível com a {nome} ({p})"
    return f"se afasta da {nome} ({p})"


def frase_conjunta(
    assimetria: Assimetria | None, curtose: ClasseCurtose | None, aderencia: Aderencia | None
) -> str | None:
    """Spec 09: "Distribuição aproximadamente simétrica e mesocúrtica; compatível com a Normal"."""
    formas = [_descrever_assimetria(assimetria)] if assimetria else []
    if curtose is not None:
        formas.append(NOMES_CURTOSE[curtose])
    partes = [f"Distribuição {' e '.join(formas)}"] if formas else []
    if aderencia is not None:
        partes.append(_descrever_aderencia(aderencia))
    if not partes:
        return None
    frase = "; ".join(partes)
    return f"{frase[0].upper()}{frase[1:]}."
