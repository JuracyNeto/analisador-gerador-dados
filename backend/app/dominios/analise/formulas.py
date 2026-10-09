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
        _f(
            "assimetria",
            "Assimetria (Fisher)",
            r"G_1 = \frac{\sqrt{n(n-1)}}{n-2} \cdot \frac{m_3}{m_2^{3/2}},\ "
            r"m_k = \frac{\sum (x_i - \bar{x})^k}{n}",
            "G₁ = [√(n(n−1)) / (n−2)] · m₃ / m₂^(3/2), mₖ = Σ(xᵢ − x̄)ᵏ / n",
        ),
        _f(
            "assimetria_pearson_1",
            "1º coeficiente de Pearson",
            r"As_1 = \frac{\bar{x} - Mo}{s}",
            "As₁ = (x̄ − Mo) / s",
        ),
        _f(
            "assimetria_pearson_2",
            "2º coeficiente de Pearson",
            r"As_2 = \frac{3(\bar{x} - Md)}{s}",
            "As₂ = 3(x̄ − Md) / s",
        ),
        _f(
            "curtose",
            "Curtose (excesso)",
            r"G_2 = \frac{(n+1)n(n-1)}{(n-2)(n-3)} \cdot \frac{\sum (x_i-\bar{x})^4}"
            r"{(\sum (x_i-\bar{x})^2)^2} - \frac{3(n-1)^2}{(n-2)(n-3)}",
            "G₂ = curtose amostral − 3 (Normal = 0)",
        ),
        _f(
            "curtose_percentilica",
            "Curtose percentílica",
            r"K = \frac{Q_3 - Q_1}{2(P_{90} - P_{10})}",
            "K = (Q3 − Q1) / [2(P90 − P10)] (Normal ≈ 0,263)",
        ),
        _f(
            "normal",
            "Distribuição Normal",
            r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
            "f(x) = (1 / (σ√(2π))) · e^(−(x−μ)² / (2σ²))",
        ),
        _f(
            "binomial",
            "Distribuição Binomial",
            r"P(X = k) = \binom{n}{k} p^k (1-p)^{n-k}",
            "P(X = k) = C(n,k) · pᵏ · (1−p)ⁿ⁻ᵏ",
        ),
        _f(
            "bernoulli",
            "Distribuição de Bernoulli",
            r"P(X = 1) = p,\ E[X] = p,\ Var = p(1-p)",
            "P(X = 1) = p · E[X] = p · Var = p(1 − p)",
        ),
        _f(
            "qui_quadrado",
            "Qui-quadrado de aderência",
            r"\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}",
            "χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ",
        ),
    )
}


def formulas_usadas(chaves: list[str | None]) -> tuple[Formula, ...]:
    """Fórmulas citadas pelas medidas aplicáveis, sem repetir, na ordem do catálogo."""
    pedidas = set(chaves)
    return tuple(f for chave, f in FORMULAS.items() if chave in pedidas)
