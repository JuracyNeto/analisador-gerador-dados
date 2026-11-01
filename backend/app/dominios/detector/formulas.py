"""Catálogo das fórmulas das regras do detector, em texto (spec 12; fonte única, D169).

Cada entrada é uma fórmula. Os detalhes de um alerta juntam as da regra com " · " e preenchem
os campos entre chaves com os valores do alerta ("P(X ≥ 46), X ~ Binomial(100; 0,2)"); fora
do alerta (relatório final), os campos recebem os símbolos de `SIMBOLOS`.
"""

SEPARADOR = " · "

# R1 — Bloco alinhado
DISTANCIA_MEDIAS = "dᵤ = |x̄_bloco − x̄_resto| / s_resto"
DISTANCIA_DESVIOS = "dₛ = |s_bloco − s_resto| / s_resto"

# R2 — Correlação por blocos
PEARSON = "r = Σ(x − x̄)(y − ȳ) / √[Σ(x − x̄)² · Σ(y − ȳ)²]"

# R3 — Formato numérico
INTEIROS_A_PASSO = "Esperados = nº de inteiros · P(intervalo = passo)^repetições"

# R4 — Valores redondos
BINOMIAL_REDONDOS = "P(X ≥ {k}), X ~ Binomial({n}; {esperado})"

# R5 — Duplicatas
QUASE_IGUAIS = (
    "Quase iguais: distância entre as linhas padronizadas < 0,01·√p "
    "(p = {numericas} colunas numéricas, fora as vazias nas duas linhas) e as demais "
    "colunas iguais; contam quando passam do acaso, estimado pelos pares vizinhos na "
    "precisão de cada coluna"
)
SO_IDENTICAS = "Só linhas idênticas"

# R6 — Comparação temporal
RAZAO_DAS_VARIANCIAS = "F = s²_depois / s²_antes"
BINOMIAL_COPIAS = "P(X ≥ k), X ~ Binomial(linhas novas; fração das antigas que se repetem)"

# R7 — Valores distantes: cercas de Tukey, escore z e boxplot ajustado (D136)
TUKEY = "IQR = Q3 − Q1"
ESCORE_Z = "z = (x − x̄) / s"
BOXPLOT_AJUSTADO = (
    "MC = {medcouple}; com MC > 0 a cerca de cima vai a Q3 + k·e^(3·MC)·IQR, "
    "nunca abaixo de Q3 + k·IQR; a etapa Limpeza usa as cercas sem o ajuste"
)

# R8 — Lei de Benford
BENFORD = "P(d) = log₁₀(1 + 1/d)"
MAD = "MAD = média de |observado − esperado|"

# R9 — Último dígito
QUI_QUADRADO_DIGITOS = "χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ, com Eᵢ = n / 10"

# R10 — Normal perfeita demais
FORMA_NORMAL = "G₁ e G₂ amostrais, como na aba Forma; p do teste de aderência à Normal"

# R11 — Sequência
RUNS = "Z = (R − μ_R) / σ_R"
AUTOCORRELACAO = "ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²"

FORMULAS_REGRAS: dict[str, tuple[str, ...]] = {
    "R1": (DISTANCIA_MEDIAS, DISTANCIA_DESVIOS),
    "R2": (PEARSON,),
    "R3": (INTEIROS_A_PASSO,),
    "R4": (BINOMIAL_REDONDOS,),
    "R5": (QUASE_IGUAIS, SO_IDENTICAS),
    "R6": (RAZAO_DAS_VARIANCIAS, BINOMIAL_COPIAS),
    "R7": (TUKEY, ESCORE_Z, BOXPLOT_AJUSTADO),
    "R8": (BENFORD, MAD),
    "R9": (QUI_QUADRADO_DIGITOS,),
    "R10": (FORMA_NORMAL,),
    "R11": (RUNS, AUTOCORRELACAO),
}

SIMBOLOS = {
    "k": "k",
    "n": "n",
    "esperado": "p₀",
    "numericas": "nº de",
    "medcouple": "medcouple da coluna",
}
"""O que aparece no lugar de cada campo fora de um alerta."""


def juntar(*formulas: str) -> str:
    """As fórmulas de um alerta numa linha: "dᵤ = … · dₛ = …"."""
    return SEPARADOR.join(formulas)


def genericas(codigo: str) -> tuple[str, ...]:
    """As fórmulas da regra com os símbolos no lugar dos valores: "P(X ≥ k), X ~ …(n; p₀)"."""
    return tuple(formula.format_map(SIMBOLOS) for formula in FORMULAS_REGRAS[codigo])
