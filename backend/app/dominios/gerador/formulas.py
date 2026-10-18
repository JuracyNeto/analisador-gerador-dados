"""Catálogo de fórmulas (LaTeX + texto) dos métodos do gerador (spec 11, D152)."""

from app.compartilhado.tipos import Formula, catalogo_de_formulas
from app.dominios.gerador.estrategias.base import Metodo

METODOS_REESCALADOS: frozenset[Metodo] = frozenset({"normal", "kde", "normal_inteira"})
"""Métodos em que a spec 11 reescala os valores sorteados para a média e o desvio exatos."""


FORMULAS: dict[str, Formula] = catalogo_de_formulas(
    Formula(
        "normal",
        "Sorteio da Normal",
        r"g_i \sim \mathcal{N}(\mu, \sigma^2)",
        "gᵢ ~ Normal(μ, σ²)",
    ),
    Formula(
        "kde",
        "Densidade por núcleo (KDE, banda de Scott)",
        r"\hat{f}(x) = \frac{1}{nh} \sum_{i=1}^{n} K\left(\frac{x - x_i}{h}\right),\ "
        r"h = s \cdot n^{-1/5}",
        "f̂(x) = (1 / nh) · Σ K((x − xᵢ) / h), K = Normal(0, 1), h = s · n^(−1/5)",
    ),
    Formula(
        "normal_inteira",
        "Normal arredondada",
        r"x_i' = \operatorname{arred}(\mu + \sigma \cdot z_i)",
        "xᵢ' = arredondar(μ + σ·zᵢ), sem negativos se o original não tinha",
    ),
    Formula(
        "poisson",
        "Distribuição de Poisson",
        r"P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!},\ \lambda = \bar{x}",
        "P(X = k) = λᵏ · e^(−λ) / k!, λ = x̄",
    ),
    Formula(
        "empirica",
        "Sorteio pelos valores observados",
        r"P(X = v) = \frac{f_v}{n}",
        "P(X = v) = f_v / n (sorteio com reposição)",
    ),
    Formula(
        "bernoulli",
        "Distribuição de Bernoulli",
        r"P(\text{sucesso}) = p,\ P(\text{fracasso}) = 1 - p",
        "P(sucesso) = p · P(fracasso) = 1 − p",
    ),
    Formula(
        "frequencias",
        "Sorteio pelas frequências",
        r"P(X = c) = fr_c = \frac{f_c}{n}",
        "P(categoria c) = fr_c = f_c / n",
    ),
    Formula(
        "reescala",
        "Reescala exata",
        r"z_i = \frac{g_i - \bar{g}}{s_g},\ x_i' = \bar{x} + s \cdot z_i",
        "zᵢ = (gᵢ − ḡ) / s_g → xᵢ' = x̄ + s·zᵢ",
    ),
    Formula(
        "cholesky",
        "Pares com correlação (Cholesky)",
        r"X = \mu_x + \sigma_x Z_1,\ Y = \mu_y + \sigma_y \left(\rho Z_1 + \sqrt{1 - \rho^2}\,"
        r" Z_2\right)",
        "X = μx + σx·Z₁ · Y = μy + σy·(ρ·Z₁ + √(1 − ρ²)·Z₂)",
    ),
    Formula(
        "ajuste_exato",
        "Ajuste exato (Gram-Schmidt)",
        r"Z_2' = Z_2 - \frac{Z_2 \cdot Z_1}{Z_1 \cdot Z_1} Z_1",
        "Z₂' = Z₂ − (Z₂·Z₁ / Z₁·Z₁)·Z₁, com Z₁ e Z₂' centradas e com DP 1 (r amostral = ρ)",
    ),
)

FORMULAS_BIVARIADO: tuple[Formula, ...] = (FORMULAS["cholesky"],)
FORMULAS_BIVARIADO_EXATO: tuple[Formula, ...] = (FORMULAS["cholesky"], FORMULAS["ajuste_exato"])


def formulas_univariadas(metodo: Metodo) -> tuple[Formula, ...]:
    """A fórmula do sorteio e, quando a spec 11 reescala, a da reescala."""
    reescala = (FORMULAS["reescala"],) if metodo in METODOS_REESCALADOS else ()
    return (FORMULAS[metodo], *reescala)
