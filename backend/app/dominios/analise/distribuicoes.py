"""Ajuste de Normal, Binomial e Bernoulli com testes de aderência (spec 09, D95–D97)."""

import numpy as np
from scipy import stats

from app.compartilhado.estatistica import ALFA, agrupar_esperados_pequenos
from app.compartilhado.numeros import formatar_numero
from app.dominios.analise import erros, textos_forma
from app.dominios.analise.resultados import (
    Ajuste,
    Parametro,
    TabelaFrequencia,
    TesteAderencia,
    ajuste_nao_aplicavel,
)

LIMITE_SHAPIRO = 5000
MIN_NORMAL = 3
GL_MINIMO = 1
PARAMETROS_NORMAL = 2  # μ e σ estimados dos dados
PARAMETROS_BINOMIAL = 1  # p estimado dos dados
_TOLERANCIA_INTEIRO = 1e-9


def _decidir(nome: str, estatistica: float, gl: int | None, p: float) -> TesteAderencia:
    """Compatível quando p ≥ α = 0,05 (spec 09)."""
    return TesteAderencia(nome, float(estatistica), gl, float(p), compativel=p >= ALFA)


def _teste_normalidade(valores: np.ndarray) -> TesteAderencia:
    """Shapiro-Wilk até 5.000 valores; acima, D'Agostino-Pearson K² (D97)."""
    if len(valores) <= LIMITE_SHAPIRO:
        resultado = stats.shapiro(valores)
        return _decidir(textos_forma.TESTE_SHAPIRO, resultado.statistic, None, resultado.pvalue)
    k2, p = stats.normaltest(valores)
    return _decidir(textos_forma.TESTE_DAGOSTINO, k2, None, p)


def qui_quadrado(
    observados: np.ndarray, esperados: np.ndarray, estimados: int
) -> TesteAderencia | None:
    """χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ com grupos de esperado ≥ 5; gl = k − 1 − estimados."""
    obs, esp = agrupar_esperados_pequenos(observados.tolist(), esperados.tolist())
    gl = len(esp) - 1 - estimados
    if gl < GL_MINIMO:
        return None
    o, e = np.asarray(obs), np.asarray(esp)
    estatistica = float(np.sum((o - e) ** 2 / e))
    return _decidir(
        textos_forma.TESTE_QUI_QUADRADO, estatistica, gl, stats.chi2.sf(estatistica, gl)
    )


def _qui_quadrado_normal(
    valores: np.ndarray, tabela: TabelaFrequencia, media: float, desvio: float
) -> TesteAderencia | None:
    """Complementar: classes da spec 04, primeira e última abertas até ±∞."""
    limites = [linha.limite_superior for linha in tabela.linhas[:-1]]
    if None in limites:
        return None
    bordas = np.array([-np.inf, *[float(b or 0) for b in limites], np.inf])
    probabilidades = np.diff(stats.norm.cdf(bordas, loc=media, scale=desvio))
    observados = np.array([linha.fi for linha in tabela.linhas], dtype="float64")
    return qui_quadrado(observados, probabilidades * len(valores), PARAMETROS_NORMAL)


def _complementar(
    valores: np.ndarray, classes: TabelaFrequencia | None, media: float, desvio: float
) -> TesteAderencia | None:
    if classes is None or classes.k is None:
        return None
    return _qui_quadrado_normal(valores, classes, media, desvio)


def _motivo_normal(valores: np.ndarray) -> str | None:
    if len(valores) < MIN_NORMAL:
        return textos_forma.nao_calculavel("normal", "poucos_3")
    if float(np.ptp(valores)) == 0:
        return textos_forma.nao_calculavel("normal", "sem_variacao")
    return None


def ajuste_normal(valores: np.ndarray, classes: TabelaFrequencia | None) -> Ajuste:
    """Normal com μ̂ = x̄ e σ̂ = s, testada por Shapiro-Wilk ou D'Agostino-Pearson."""
    motivo = _motivo_normal(valores)
    if motivo:
        return ajuste_nao_aplicavel("normal", motivo)
    media, desvio = float(valores.mean()), float(valores.std(ddof=1))
    teste = _teste_normalidade(valores)
    complementar = _complementar(valores, classes, media, desvio)
    return Ajuste(
        "normal",
        parametros=(Parametro("μ̂", "média", media), Parametro("σ̂", "desvio padrão", desvio)),
        teste=teste,
        complementar=complementar,
        frase=textos_forma.frase_aderencia("Normal", teste),
        calculo=textos_forma.calculo_teste(teste),
        formula="normal",
    )


def eh_contagem(valores: np.ndarray) -> bool:
    """Inteiros a partir de 0 (número de sucessos)."""
    inteiros = bool(np.all(np.abs(valores - np.round(valores)) < _TOLERANCIA_INTEIRO))
    return inteiros and bool(np.all(valores >= 0))


def _motivo_binomial(valores: np.ndarray) -> str | None:
    if not eh_contagem(valores):
        return textos_forma.nao_calculavel("binomial", "binomial_nao_contagem")
    if float(valores.max()) == 0:
        return textos_forma.nao_calculavel("binomial", "binomial_zeros")
    return None


def _parametros_binomial(n: int, p: float) -> tuple[Parametro, ...]:
    return (
        Parametro("n", "número de tentativas", n),
        Parametro("p̂", "probabilidade de sucesso", p),
        Parametro("E[X]", "valor esperado", n * p),
        Parametro("Var", "variância", n * p * (1 - p)),
    )


def tentativas_da_binomial(valores: np.ndarray, tentativas: int | None) -> int:
    """n = máximo observado ou o informado, que não pode ser menor que o máximo (D96)."""
    maximo = round(float(valores.max()))
    if tentativas is None:
        return maximo
    if tentativas < maximo:
        raise erros.tentativas_invalidas(maximo)
    return tentativas


def ajuste_binomial(valores: np.ndarray, tentativas: int | None) -> Ajuste:
    """Binomial com p̂ = x̄ / n, testada por qui-quadrado com as caudas agrupadas."""
    motivo = _motivo_binomial(valores)
    if motivo:
        return ajuste_nao_aplicavel("binomial", motivo)
    n = tentativas_da_binomial(valores, tentativas)
    p = float(valores.mean()) / n
    observados = np.bincount(np.round(valores).astype(int), minlength=n + 1).astype("float64")
    esperados = len(valores) * stats.binom.pmf(np.arange(n + 1), n, p)
    teste = qui_quadrado(observados, esperados, PARAMETROS_BINOMIAL)
    if teste is None:
        frase, calculo = textos_forma.SEM_GRUPOS_PARA_TESTE, None
    else:
        frase = textos_forma.frase_aderencia("Binomial", teste)
        calculo = textos_forma.calculo_teste(teste)
    return Ajuste(
        "binomial",
        parametros=_parametros_binomial(n, p),
        teste=teste,
        frase=frase,
        calculo=calculo,
        formula="binomial",
    )


def ajuste_bernoulli(p: float) -> Ajuste:
    """Binária: p̂, E[X] = p e Var = p(1 − p); sem teste, pois gl = 0 (D95)."""
    parametros = (
        Parametro("p̂", "proporção de sucesso", p),
        Parametro("E[X]", "valor esperado", p),
        Parametro("Var", "variância", p * (1 - p)),
    )
    calculo = f"p̂ = {formatar_numero(p)} · Var = p(1 − p) = {formatar_numero(p * (1 - p))}"
    return Ajuste(
        "bernoulli",
        parametros=parametros,
        frase=textos_forma.FRASE_BERNOULLI,
        calculo=calculo,
        formula="bernoulli",
    )
