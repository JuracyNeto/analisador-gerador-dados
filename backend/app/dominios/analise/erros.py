"""Erros do domínio analise (spec 14, formato da spec 16)."""

from app.core.erros import EntradaInvalida


def coluna_ignorada(coluna: str) -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNA_IGNORADA",
        f"A coluna {coluna} é um identificador e fica fora das análises.",
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
