"""Títulos, "Por que este gráfico?" e resumos textuais das figuras (spec 08, spec 16)."""

from app.compartilhado.numeros import formatar_inteiro, formatar_numero, formatar_percentual
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
    "sobreposicao": "Sobreposição",
    "blocos": "Média por bloco",
    "benford": "Benford",
    "ultimo_digito": "Último dígito",
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
    "sobreposicao": (
        "As barras do original e do gerado ficam uma sobre a outra; quanto mais se cobrem, "
        "mais parecidas são as distribuições."
    ),
    "pares_gerados": "Cada ponto é um par gerado; a nuvem mostra a correlação obtida.",
    "blocos": (
        "Cada ponto é a média de um bloco de linhas seguidas; em dados reais elas sobem e "
        "descem em volta da média geral, e um bloco exatamente em cima dela chama atenção."
    ),
    "benford": (
        "Compara quantas vezes cada dígito abre os valores com o que a Lei de Benford prevê "
        "para dados naturais."
    ),
    "ultimo_digito": (
        "Em medições reais, cada último dígito aparece perto de 10% das vezes; barras muito "
        "acima ou abaixo da linha chamam atenção."
    ),
}


def titulo_distribuicao(dados: DadosUnivariados) -> str:
    return f"Distribuição de {dados.coluna} (n = {formatar_inteiro(dados.n)})"


def titulo_categorias(dados: DadosUnivariados) -> str:
    return f"Frequência de {dados.coluna} (n = {formatar_inteiro(dados.n)}), da maior para a menor"


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
    return f"A metade dos valores é alcançada na classe {metade.rotulo}, onde está a mediana."


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
    return f"Histograma de {coluna} com curva Normal (n = {formatar_inteiro(n)})"


def titulo_bastoes_normal(coluna: str, n: int) -> str:
    return f"Distribuição de {coluna} com curva Normal (n = {formatar_inteiro(n)})"


def titulo_qqplot(coluna: str) -> str:
    return f"QQ-plot de {coluna} contra a Normal"


def titulo_binomial(coluna: str, tentativas: int, p: float) -> str:
    n, chance = formatar_inteiro(tentativas), formatar_numero(p)
    return f"{coluna}: observado × Binomial (n = {n}; p = {chance})"


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
    return f"{y} em função de {x} (n = {formatar_inteiro(n)})"


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


LIMIAR_PARECIDAS_PP = 5.0  # pontos percentuais entre as barras das duas séries


def titulo_sobreposicao(coluna: str) -> str:
    return f"{coluna}: original e gerado sobrepostos"


def titulo_gerados(coluna: str) -> str:
    return f"{coluna}: valores gerados"


def resumo_sobreposicao(maior_diferenca: float | None, n_gerado: int) -> str:
    if maior_diferenca is None:
        return f"Distribuição dos {formatar_numero(n_gerado)} valores gerados."
    if maior_diferenca < LIMIAR_PARECIDAS_PP:
        return "As duas distribuições têm formas parecidas."
    return "As distribuições diferem em alguns trechos."


def titulo_pares_gerados(n: int) -> str:
    return f"Pares gerados (n = {formatar_inteiro(n)})"


def resumo_pares_gerados(r: float, n: int, mostrados: int) -> str:
    resumo = f"Correlação obtida: r = {formatar_numero(r)}."
    if mostrados < n:
        resumo += f" Mostramos {formatar_numero(mostrados)} dos {formatar_numero(n)} pontos."
    return resumo


ALGARISMOS_PERCENTUAL = 2
NOME_BENFORD = "Lei de Benford"


def percentual_curto(fracao: float) -> str:
    """0,24 → "24%"; 0,0458 → "4,6%" (2 algarismos)."""
    return f"{formatar_numero(fracao * 100, ALGARISMOS_PERCENTUAL)}%"


def titulo_blocos(coluna: str, k: int) -> str:
    return f"Média de {coluna} por bloco de {k} linhas"


def resumo_blocos(linhas: tuple[int, int], media: float) -> str:
    return (
        f"A média das linhas {linhas[0]}–{linhas[1]} fica em cima da média geral "
        f"({formatar_numero(media)})."
    )


def nome_bloco_destacado(linhas: tuple[int, int]) -> str:
    return f"Bloco alinhado (linhas {linhas[0]}–{linhas[1]})"


def titulo_benford(coluna: str) -> str:
    return f"1º dígito de {coluna}: observado × Benford"


def resumo_benford(digito: int, observada: float, esperada: float) -> str:
    return (
        f"O {digito} abre {percentual_curto(observada)} dos valores; "
        f"pela Lei de Benford seriam {percentual_curto(esperada)}."
    )


def titulo_ultimo_digito(coluna: str) -> str:
    return f"Último dígito de {coluna}"


def resumo_ultimo_digito(digito: int, observada: float, esperada: float) -> str:
    return (
        f"O {digito} aparece em {percentual_curto(observada)} dos valores; "
        f"o esperado é {percentual_curto(esperada)}."
    )


def nome_esperado(esperada: float) -> str:
    return f"Esperado ({percentual_curto(esperada)})"
