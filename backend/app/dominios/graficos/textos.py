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
    "histograma_normal": "Histograma + Normal",
    "bastoes_normal": "Bastões + Normal",
    "qqplot": "QQ-plot",
    "binomial": "Observado × Binomial",
    "dispersao": "Dispersão",
    "residuos": "Resíduos",
    "matriz": "Matriz",
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
    "histograma_normal": (
        "A curva mostra como seria uma Normal com a mesma média e o mesmo desvio; "
        "quanto mais as barras a acompanham, mais os dados se parecem com ela."
    ),
    "bastoes_normal": (
        "A curva mostra a aproximação pela Normal com a mesma média e o mesmo desvio."
    ),
    "qqplot": (
        "Compara cada valor com o que se esperaria numa Normal; "
        "pontos sobre a reta indicam dados normais."
    ),
    "binomial": "Compara quantas vezes cada contagem apareceu com o que a Binomial prevê.",
    "dispersao": (
        "Cada ponto é uma linha da tabela; a reta resume a tendência e serve para prever Y."
    ),
    "residuos": (
        "Mostra quanto cada ponto fica acima ou abaixo da reta; ajuda a ver se uma reta "
        "é um bom resumo da relação."
    ),
    "matriz": (
        "Mostra de uma vez a correlação de cada par de colunas numéricas: azul quando "
        "crescem juntas, laranja quando uma cresce e a outra diminui."
    ),
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


RESUMOS_CURVA = {
    True: "As barras acompanham a curva.",
    False: "As barras se afastam da curva em alguns trechos.",
    None: "Compare as barras com a curva.",
}
RESUMOS_QQ = {
    True: "Os pontos ficam perto da reta: os dados se comportam como uma Normal.",
    False: "Os pontos se afastam da reta nas pontas: as caudas fogem da Normal.",
    None: "Pontos perto da reta indicam dados parecidos com uma Normal.",
}
RESUMOS_BINOMIAL = {
    True: "As barras observadas acompanham as esperadas.",
    False: "Há diferenças entre o observado e o esperado.",
    None: "Compare as barras observadas com as esperadas.",
}


def titulo_histograma_normal(coluna: str, n: int) -> str:
    return f"Histograma de {coluna} com curva Normal (n = {n})"


def titulo_bastoes_normal(coluna: str, n: int) -> str:
    return f"Distribuição de {coluna} com curva Normal (n = {n})"


def titulo_qqplot(coluna: str) -> str:
    return f"QQ-plot de {coluna} contra a Normal"


def titulo_binomial(coluna: str, tentativas: int, p: float) -> str:
    return f"{coluna}: observado × Binomial (n = {tentativas}; p = {formatar_numero(p)})"


RESUMOS_DISPERSAO = {
    ("forte", "positiva"): "Os pontos sobem da esquerda para a direita e ficam perto da reta.",
    ("moderada", "positiva"): (
        "Os pontos sobem da esquerda para a direita, mas se espalham em volta da reta."
    ),
    ("forte", "negativa"): "Os pontos descem da esquerda para a direita e ficam perto da reta.",
    ("moderada", "negativa"): (
        "Os pontos descem da esquerda para a direita, mas se espalham em volta da reta."
    ),
}
SEM_DIRECAO = "Os pontos não seguem uma direção clara."
TITULO_RESIDUOS = "Resíduos da regressão"
TITULO_MATRIZ = "Matriz de correlação (Pearson)"


def titulo_dispersao(x: str, y: str, n: int) -> str:
    return f"{y} em função de {x} (n = {formatar_numero(n)})"


def resumo_dispersao(forca: str, sentido: str, n: int, mostrados: int) -> str:
    """Direção dos pontos (força e sentido de r) e o aviso de amostra, quando houver (D101)."""
    texto = RESUMOS_DISPERSAO.get((forca, sentido), SEM_DIRECAO)
    if mostrados < n:
        texto += f" Mostramos {formatar_numero(mostrados)} dos {formatar_numero(n)} pontos."
    return texto


def resumo_residuos(y: str) -> str:
    return (
        f"Resíduo é a diferença entre o {y} real e o previsto. Pontos espalhados em volta do "
        "zero, sem formar curva, indicam que a reta é um bom resumo da relação."
    )
