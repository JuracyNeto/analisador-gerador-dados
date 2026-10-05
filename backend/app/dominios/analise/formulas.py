"""Catálogo de fórmulas (LaTeX + texto) usadas na análise univariada (specs 04–07)."""

from app.dominios.analise.resultados import Formula


def _f(chave: str, nome: str, latex: str, texto: str) -> Formula:
    return Formula(chave, nome, latex, texto)


FORMULAS: dict[str, Formula] = {
    f.chave: f
    for f in (
        _f("frequencia_relativa", "Frequência relativa", r"fr_i = \frac{f_i}{n}", "frᵢ = fᵢ / n"),
        _f(
            "frequencia_acumulada",
            "Frequência acumulada",
            r"F_i = \sum_{j \le i} f_j",
            "Fᵢ = Σⱼ≤ᵢ fⱼ",
        ),
        _f(
            "sturges",
            "Número de classes (Sturges)",
            r"k = \lceil 1 + 3{,}322 \log_{10} n \rceil",
            "k = ⌈1 + 3,322 · log₁₀ n⌉",
        ),
        _f(
            "amplitude_classe",
            "Amplitude da classe",
            r"h = \frac{x_{max} - x_{min}}{k}",
            "h = (xₘₐₓ − xₘᵢₙ) / k",
        ),
        _f("ponto_medio", "Ponto médio", r"x_i = \frac{L_i + L_{i+1}}{2}", "xᵢ = (Lᵢ + Lᵢ₊₁) / 2"),
        _f("media", "Média", r"\bar{x} = \frac{\sum x_i}{n}", "x̄ = Σxᵢ / n"),
        _f(
            "mediana",
            "Mediana",
            r"Md = x_{\left(\frac{n+1}{2}\right)}",
            "Md = valor central dos dados ordenados",
        ),
        _f("moda", "Moda", r"Mo = \text{valor de maior } f_i", "Mo = valor mais frequente"),
        _f(
            "moda_czuber",
            "Moda de Czuber",
            r"Mo = L_i + \frac{\Delta_1}{\Delta_1 + \Delta_2} \cdot h",
            "Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h",
        ),
        _f("proporcao", "Proporção", r"p = \frac{\text{sucessos}}{n}", "p = nº de sucessos / n"),
        _f(
            "quantil",
            "Separatriz (interpolação linear)",
            r"Q_p = x_{(\lfloor h \rfloor)} + (h - \lfloor h \rfloor)"
            r"(x_{(\lfloor h \rfloor + 1)} - x_{(\lfloor h \rfloor)}),\ h = (n-1)p",
            "Qp = x₍⌊h⌋₎ + (h − ⌊h⌋)·(x₍⌊h⌋+1₎ − x₍⌊h⌋₎), h = (n − 1)·p",
        ),
        _f(
            "posicao_percentil",
            "Posição percentil",
            r"PR = 100 \cdot \frac{\#(x_i < v) + 0{,}5 \cdot \#(x_i = v)}{n}",
            "PR = 100 · (nº de xᵢ < v + 0,5 · nº de xᵢ = v) / n",
        ),
        _f("amplitude", "Amplitude", r"A = x_{max} - x_{min}", "A = xₘₐₓ − xₘᵢₙ"),
        _f(
            "variancia",
            "Variância amostral",
            r"s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}",
            "s² = Σ(xᵢ − x̄)² / (n − 1)",
        ),
        _f(
            "variancia_populacional",
            "Variância populacional",
            r"\sigma^2 = \frac{\sum (x_i - \mu)^2}{n}",
            "σ² = Σ(xᵢ − μ)² / n",
        ),
        _f("desvio_padrao", "Desvio padrão", r"s = \sqrt{s^2}", "s = √s²"),
        _f("iqr", "Amplitude interquartil", r"IQR = Q_3 - Q_1", "IQR = Q3 − Q1"),
        _f(
            "cv",
            "Coeficiente de variação",
            r"CV = \frac{s}{\bar{x}} \cdot 100\%",
            "CV = (s / x̄) · 100%",
        ),
        _f("variancia_binaria", "Variância (binária)", r"Var = p(1 - p)", "Var = p(1 − p)"),
    )
}


def formulas_usadas(chaves: list[str | None]) -> tuple[Formula, ...]:
    """Fórmulas citadas pelas medidas aplicáveis, sem repetir, na ordem do catálogo."""
    pedidas = set(chaves)
    return tuple(f for chave, f in FORMULAS.items() if chave in pedidas)
