"""Títulos, "Por que este gráfico?" e resumos textuais das figuras (spec 08, spec 16)."""

from app.compartilhado.numeros import formatar_numero, formatar_percentual
from app.dominios.graficos.entradas import Barra, DadosUnivariados, ResumoCaixa

METADE_PCT = 50

ROTULOS = {
    "barras": "Barras",
    "bastoes": "Bastões",
    "histograma": "Histograma",
    "boxplot": "Boxplot",
    "ogiva": "Ogiva",
    "acumulada": "Acumulada",
    "pizza": "Pizza",
}

PORQUE = {
    "barras_nominal": (
        "Categorias sem ordem são comparadas pelo tamanho. Ordenamos da maior para a menor "
        "para facilitar a leitura."
    ),
    "barras_binaria": "Com só duas categorias, barras com o percentual mostram tudo de uma vez.",
    "barras_ordinal": "A ordem das categorias tem significado, então as barras seguem a escala.",
    "bastoes": "Valores inteiros são pontos isolados, não intervalos; cada haste é um valor.",
    "histograma": (
        "Para números contínuos, agrupar em classes mostra a forma da distribuição, "
        "onde fica o centro e como são as caudas."
    ),
    "boxplot": ("Mostra a mediana, os quartis e os valores muito afastados em um só desenho."),
    "ogiva": "A curva acumulada mostra quantos valores ficam abaixo de cada limite de classe.",
    "acumulada": "Mostra quanto dos dados já foi somado até cada categoria ou valor.",
    "pizza": "Com até 5 categorias, a pizza mostra bem a parte de cada uma no total.",
}


def titulo_distribuicao(dados: DadosUnivariados) -> str:
    return f"Distribuição de {dados.coluna} (n = {dados.n})"


def titulo_categorias(dados: DadosUnivariados) -> str:
    return f"Frequência de {dados.coluna} (n = {dados.n}), da maior para a menor"


def titulo_boxplot(dados: DadosUnivariados) -> str:
    return f"Boxplot de {dados.coluna}"


def titulo_ogiva(dados: DadosUnivariados) -> str:
    return f"Frequência acumulada (ogiva) de {dados.coluna}"


def titulo_acumulada(dados: DadosUnivariados) -> str:
    return f"Frequência acumulada de {dados.coluna}"


def titulo_pizza(dados: DadosUnivariados) -> str:
    return f"Parte de cada categoria de {dados.coluna}"


def _mais_frequente(barras: tuple[Barra, ...]) -> Barra:
    return max(barras, key=lambda b: b.frequencia)


def resumo_mais_frequente(dados: DadosUnivariados, nome: str) -> str:
    """ "A classe mais comum é 65,5 ⊢ 71,0, com 49 valores (21,6%)."."""
    barra = _mais_frequente(dados.barras)
    valores = "valor" if barra.frequencia == 1 else "valores"
    return (
        f"{nome} mais comum é {barra.rotulo}, com {barra.frequencia} {valores} "
        f"({formatar_percentual(barra.percentual)})."
    )


def resumo_caixa(caixa: ResumoCaixa) -> str:
    texto = (
        f"Metade dos valores fica entre {formatar_numero(caixa.q1)} e "
        f"{formatar_numero(caixa.q3)}; a mediana é {formatar_numero(caixa.mediana)}."
    )
    n = len(caixa.discrepantes)
    if n:
        texto += f" {n} {'valor fica' if n == 1 else 'valores ficam'} muito longe dos demais."
    return texto


def resumo_acumulada(dados: DadosUnivariados) -> str:
    """Onde a frequência acumulada chega a 50%."""
    metade = next(b for b in dados.barras if (b.acumulado_pct or 0) >= METADE_PCT)
    return f"Metade dos valores chega até {metade.rotulo}."
