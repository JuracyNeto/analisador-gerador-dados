"""Textos do detector (spec 16, ADR 0005): tom neutro, número com contexto, p em palavras.

Nenhuma regra monta texto fora deste módulo (D118).
"""

from collections.abc import Sequence
from itertools import pairwise

from app.compartilhado.numeros import (
    formatar_com_sinal,
    formatar_fixo,
    formatar_inteiro,
    formatar_p_valor,
    formatar_percentual,
)
from app.compartilhado.textos import juntar_lista, p_valor_em_palavras, pluralizar
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso

MAX_ITENS_TEXTO = 8
MIN_LINHAS_FAIXA = 3
"""Com 3 linhas seguidas ou mais, o exemplo diz "Linhas 120 a 138"."""
CASAS_SIGNIFICATIVAS_VALOR = 7
RETICENCIAS = "…"


# Formatação ---------------------------------------------------------------------------------


def valor(numero: float) -> str:
    """Valor de uma célula como o usuário escreveria: 70 · 1,62 · −3,5."""
    return formatar_com_sinal(numero, CASAS_SIGNIFICATIVAS_VALOR)


def numero(medida: float) -> str:
    """Medida calculada com até 4 algarismos significativos: 80,5 · 0,0881."""
    return formatar_com_sinal(medida)


def percentual(fracao: float) -> str:
    """Fração (0–1) como percentual sem casas: 0,46 → 46%."""
    return formatar_percentual(fracao * 100, 0)


def razao(vezes: float) -> str:
    """Quantas vezes o esperado: 2,3×."""
    return f"{formatar_fixo(vezes, 1)}×"


def quantidade(n: int, singular: str, plural: str) -> str:
    return f"{formatar_inteiro(n)} {pluralizar(n, singular, plural)}"


def p_em_palavras(p: float) -> str:
    return f"chance de acontecer por acaso: {p_valor_em_palavras(p)}"


def p_formatado(p: float) -> str:
    return formatar_p_valor(p)


# Exemplo e regras não aplicadas -------------------------------------------------------------


def _seguidas(linhas: Sequence[int]) -> bool:
    return all(b == a + 1 for a, b in pairwise(linhas))


def faixa_de_linhas(linhas: Sequence[int]) -> str:
    """ "Linha 12" · "Linhas 120 a 138" · "Linhas 3, 9 e 14" · "Linhas 1, 3, …, 15…"."""
    if len(linhas) == 1:
        return f"Linha {linhas[0]}"
    if len(linhas) >= MIN_LINHAS_FAIXA and _seguidas(linhas):
        return f"Linhas {linhas[0]} a {linhas[-1]}"
    if len(linhas) > MAX_ITENS_TEXTO:
        primeiras = ", ".join(str(linha) for linha in linhas[:MAX_ITENS_TEXTO])
        return f"Linhas {primeiras}{RETICENCIAS}"
    return f"Linhas {juntar_lista([str(linha) for linha in linhas])}"


def lista_de_valores(valores: Sequence[str]) -> str:
    """Até 8 valores separados por vírgula, com "…" se houver mais."""
    texto = ", ".join(valores[:MAX_ITENS_TEXTO])
    return texto + RETICENCIAS if len(valores) > MAX_ITENS_TEXTO else texto


def texto_exemplo(linhas: Sequence[int], valores: Sequence[str]) -> str:
    """ "Linhas 120 a 138: 70, 75, 80, 75, 70…" (spec 16, parte 5)."""
    return f"{faixa_de_linhas(linhas)}: {lista_de_valores(valores)}"


def frase_nao_aplicada(nome_regra: str, coluna: str | None, motivo: str) -> str:
    """ "{regra} não verificada em {col}: {motivo}." (spec 16)."""
    onde = f" em {coluna}" if coluna is not None else ""
    return f"{nome_regra} não verificada{onde}: {motivo}."


def poucos_valores(minimo: int, n: int) -> str:
    return (
        f"precisa de {formatar_inteiro(minimo)} valores ou mais; a coluna tem {formatar_inteiro(n)}"
    )


SEM_NUMERICAS = "o arquivo não tem colunas numéricas"
SEM_CONTINUAS = "o arquivo não tem colunas contínuas"
VALORES_IGUAIS = "todos os valores são iguais"
DIGITO_CONSTANTE = "o último dígito é sempre o mesmo"
POUCA_VARIACAO = "os valores variam pouco para o último dígito ser aleatório"
METADE_CENTRAL_IGUAL = "a metade central dos valores é toda igual"


# R7 — Valores distantes ---------------------------------------------------------------------


def r07_textos(coluna: str, k: int, exemplo: float, limite: float) -> TextosAviso:
    """ "{k} valores de {col} estão muito longe dos demais (ex.: {v})" (spec 16)."""
    longe = f"{pluralizar(k, 'está', 'estão')} muito longe dos demais"
    return TextosAviso(
        titulo=f"{quantidade(k, 'valor distante', 'valores distantes')} dos demais em {coluna}",
        resumo=(
            f"{quantidade(k, 'valor', 'valores')} de {coluna} {longe} (ex.: {valor(exemplo)}); "
            f"o limite usual seria {numero(limite)}."
        ),
        por_que="Valores extremos podem ser erros de digitação ou casos especiais.",
        pode_ser_normal="…são casos raros, mas reais.",
        o_que_fazer=(
            "Confira esses valores na fonte; se forem erros de digitação, corrija na etapa Limpeza."
        ),
    )


def r07_detalhes(moderados: int, extremos: int, cercas: tuple[float, ...]) -> DetalhesAviso:
    """Cercas: (Q1 − 1,5·IQR, Q3 + 1,5·IQR, Q1 − 3·IQR, Q3 + 3·IQR)."""
    baixo, alto, baixo_extremo, alto_extremo = (numero(c) for c in cercas)
    return DetalhesAviso(
        medida="Valores fora das cercas de Tukey ou com |z| > 3",
        valor=(
            f"{quantidade(moderados, 'moderado', 'moderados')} e "
            f"{quantidade(extremos, 'extremo', 'extremos')}"
        ),
        limiar=(
            f"Moderado: fora de {baixo} a {alto} (1,5·IQR) · "
            f"extremo: fora de {baixo_extremo} a {alto_extremo} (3·IQR) ou |z| > 3"
        ),
        formula="IQR = Q3 − Q1 · z = (x − x̄) / s",
    )
