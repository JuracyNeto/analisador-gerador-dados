"""Textos da análise: "não se aplica", interpretações e frases (spec 16)."""

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.tipos import TipoVariavel

LIMIAR_SIMETRIA = 0.1
NOMES_NO_PLURAL = frozenset({"separatrizes"})

TIPO_LEGIVEL = {
    TipoVariavel.NOMINAL: "qualitativas nominais",
    TipoVariavel.ORDINAL: "qualitativas ordinais",
    TipoVariavel.BINARIA: "binárias",
    TipoVariavel.DISCRETA: "quantitativas discretas",
    TipoVariavel.CONTINUA: "quantitativas contínuas",
    TipoVariavel.IDENTIFICADOR: "identificadores",
}

MOTIVOS = {
    "acumulada": 'as categorias não têm ordem para somar "até aqui"',
    "media": "não dá para somar categorias",
    "media_binaria": "use a proporção, que é a média de uma variável 0/1",
    "mediana": "as categorias não têm ordem",
    "moda_czuber": "ela só vale para dados contínuos agrupados em classes",
    "proporcao": "ela só vale para variáveis com dois valores",
    "separatrizes": "as categorias não têm ordem para dividir em partes",
    "posicao": "precisa de valores numéricos",
    "dispersao": "precisa de distâncias entre números",
    "distancias": "precisa de distâncias entre números",
    "poucos_valores": "precisa de pelo menos 2 valores",
}

NOMES = {
    "acumulada": "Frequência acumulada",
    "media": "Média",
    "mediana": "Mediana",
    "moda_czuber": "Moda de Czuber",
    "proporcao": "Proporção",
    "separatrizes": "Separatrizes",
    "posicao": '"Onde está meu valor?"',
    "dispersao": "Dispersão",
    "amplitude": "Amplitude",
    "variancia": "Variância",
    "variancia_populacional": "Variância populacional",
    "desvio_padrao": "Desvio padrão",
    "desvio_padrao_populacional": "Desvio padrão populacional",
    "iqr": "Amplitude interquartil",
    "cv": "Coeficiente de variação",
}


def nao_se_aplica(item: str, tipo: TipoVariavel, motivo: str) -> str:
    """ "{medida} não se aplica a {tipo}: {motivo}." (spec 16)."""
    verbo = "se aplicam" if item in NOMES_NO_PLURAL else "se aplica"
    return f"{NOMES[item]} não {verbo} a {TIPO_LEGIVEL[tipo]}: {MOTIVOS[motivo]}."


def nao_calculavel(item: str, motivo: str) -> str:
    """Caso de borda numérico (spec 07), ex.: "Variância não se aplica: precisa de 2 valores"."""
    return f"{NOMES[item]} não se aplica: {MOTIVOS[motivo]}."


def interpretar_media_mediana(media: float, mediana: float, desvio: float) -> str | None:
    """Spec 05: compara média e mediana em relação ao desvio padrão."""
    if desvio == 0:
        return None
    diferenca = formatar_numero(abs(media - mediana))
    if abs(media - mediana) / desvio < LIMIAR_SIMETRIA:
        return (
            f"Média e mediana próximas (diferença de {diferenca}): a distribuição parece simétrica."
        )
    if media > mediana:
        return "Média maior que a mediana: há valores altos puxando a média (assimetria à direita)."
    return "Média menor que a mediana: há valores baixos puxando a média (assimetria à esquerda)."


CV_MEDIA_ZERO = "O CV não pode ser calculado porque a média é zero."
