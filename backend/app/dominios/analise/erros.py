"""Erros do domínio analise (spec 14, formato da spec 16)."""

from app.compartilhado.tipos import TipoVariavel
from app.core.erros import EntradaInvalida

POR_QUE_IGNORADA = {
    TipoVariavel.IDENTIFICADOR: "é um identificador",
    TipoVariavel.DATA: "tem datas",
}


def coluna_ignorada(coluna: str, tipo: TipoVariavel) -> EntradaInvalida:
    """Tipos auxiliares (identificador e data) ficam fora das análises (D17, D90)."""
    return EntradaInvalida(
        "COLUNA_IGNORADA",
        f"A coluna {coluna} {POR_QUE_IGNORADA[tipo]} e fica fora das análises.",
        "Mude o tipo na etapa Variáveis se ela tiver valores para analisar.",
    )


def coluna_vazia(coluna: str) -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNA_VAZIA",
        f"A coluna {coluna} não tem valores para analisar.",
        "Escolha outra coluna ou confira a limpeza.",
    )


def posicao_nao_aplicavel() -> EntradaInvalida:
    return EntradaInvalida(
        "POSICAO_NAO_APLICAVEL",
        '"Onde está meu valor?" só funciona com colunas numéricas.',
        "Escolha uma coluna discreta ou contínua.",
    )


def tentativas_invalidas(maximo: int) -> EntradaInvalida:
    return EntradaInvalida(
        "TENTATIVAS_INVALIDAS",
        f"O número de tentativas precisa ser pelo menos o maior valor observado ({maximo}).",
        f"Use um número igual ou maior que {maximo}.",
    )


SUGESTAO_NUMERICAS = "Escolha colunas discretas ou contínuas."


def coluna_nao_numerica(coluna: str) -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNA_NAO_NUMERICA",
        f"Escolha duas colunas numéricas: {coluna} não é numérica.",
        SUGESTAO_NUMERICAS,
    )


def colunas_iguais() -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNAS_IGUAIS",
        "X e Y precisam ser colunas diferentes.",
        "Escolha outra coluna para Y.",
    )


def poucos_pares(n: int, x: str, y: str) -> EntradaInvalida:
    return EntradaInvalida(
        "POUCOS_PARES",
        f"Só há {n} linhas com {x} e {y} preenchidas; são precisas pelo menos 3.",
        "Confira os faltantes na etapa Limpeza.",
    )


def sem_variacao(coluna: str) -> EntradaInvalida:
    return EntradaInvalida(
        "SEM_VARIACAO",
        f"Todos os valores de {coluna} são iguais; não dá para medir a relação.",
        "Escolha outra coluna.",
    )
