"""Textos da bivariada: equação, correlação, regressão, previsão e matriz (spec 10, 16)."""

from itertools import combinations

from app.compartilhado.estatistica import ALFA
from app.compartilhado.numeros import MENOS, formatar_com_sinal, formatar_numero
from app.compartilhado.textos import juntar_lista, p_valor_em_palavras
from app.dominios.analise.resultados_bivariada import Faixa, Forca, Sentido

__all__ = ["Forca", "Sentido"]

LIMIAR_FRACA = 0.3
CASAS_MATRIZ = 2
SEM_PARES = "Precisa de pelo menos duas colunas numéricas para montar a matriz."


def numero(valor: float) -> str:
    return formatar_com_sinal(valor)


def formatar_equacao(a: float, b: float) -> str:
    """Ex.: "Ŷ = −98,4 + 98,1·X"."""
    sinal = MENOS if b < 0 else "+"
    return f"Ŷ = {numero(a)} {sinal} {formatar_numero(abs(b))}·X"


def frase_forca(forca: Forca, sentido: Sentido, x: str, y: str) -> str:
    """Spec 10: positiva = crescem juntas; negativa = uma cresce, a outra diminui."""
    if forca == "fraca" or sentido == "nula":
        return f"{x} e {y} quase não andam juntas."
    rumo = "aumentar" if sentido == "positiva" else "diminuir"
    return f"Quando {x} aumenta, {y} tende a {rumo}."


def frase_significancia(p: float) -> str:
    """Teste t de r com α = 0,05; p-valor traduzido (spec 16)."""
    acaso = p_valor_em_palavras(p)
    if p < ALFA:
        return f"A correlação é significativa (chance de acontecer por acaso: {acaso})."
    return f"A correlação não é significativa: pode ter aparecido por acaso ({acaso})."


def frase_r2(r2_pct: float, x: str, y: str) -> str:
    return f"{formatar_numero(r2_pct, 2)}% da variação de {y} é explicada por {x}."


def frase_reta(b: float, x: str, y: str) -> str:
    if b == 0:
        return f"O valor previsto de {y} não muda com {x}."
    rumo = "sobe" if b > 0 else "cai"
    return (
        f"A cada 1 a mais em {x}, o valor previsto de {y} {rumo} cerca de "
        f"{formatar_numero(abs(b))}."
    )


def frase_se(se: float, y: str) -> str:
    erro = formatar_numero(se)
    return f"Em média, as previsões de {y} erram cerca de {erro} para mais ou para menos."


def frase_previsao(x: str, valor: float, y: str, previsto: float) -> str:
    """Spec 10: "Para X = 50, o valor previsto de Y é 123,4."."""
    return f"Para {x} = {numero(valor)}, o valor previsto de {y} é {numero(previsto)}."


def aviso_extrapolacao(x: str, faixa: Faixa) -> str:
    """Texto de telas.md (tela 5); o título "Fora da faixa observada." fica no banner."""
    return (
        f"Os valores de {x} vão de {numero(faixa.minimo)} a {numero(faixa.maximo)}. "
        "Prever fora disso (extrapolar) pode dar resultados pouco confiáveis."
    )


type Valores = tuple[tuple[float | None, ...], ...]


def _par_mais_forte(colunas: tuple[str, ...], valores: Valores) -> tuple[str, str, float] | None:
    pares = [
        (colunas[i], colunas[j], r)
        for i, j in combinations(range(len(colunas)), 2)
        if (r := valores[i][j]) is not None
    ]
    return max(pares, key=lambda par: abs(par[2]), default=None)


def _fracas(colunas: tuple[str, ...], valores: Valores) -> list[str]:
    """Colunas cujos |r| com todas as outras ficam abaixo de 0,3."""

    def fraca(i: int) -> bool:
        outros = [r for j, r in enumerate(valores[i]) if j != i and r is not None]
        return bool(outros) and all(abs(r) < LIMIAR_FRACA for r in outros)

    return [coluna for i, coluna in enumerate(colunas) if fraca(i)]


def resumo_matriz(colunas: tuple[str, ...], valores: Valores) -> str:
    """Ex.: "O par mais forte é altura_m × peso_kg (0,78). idade quase não se relaciona …"."""
    mais_forte = _par_mais_forte(colunas, valores)
    if mais_forte is None:
        return SEM_PARES
    a, b, r = mais_forte
    frases = [f"O par mais forte é {a} × {b} ({numero(round(r, CASAS_MATRIZ))})."]
    fracas = _fracas(colunas, valores)
    if len(fracas) == 1:
        frases.append(f"{fracas[0]} quase não se relaciona com as outras.")
    elif fracas:
        frases.append(f"{juntar_lista(fracas)} quase não se relacionam com as outras.")
    return " ".join(frases)
