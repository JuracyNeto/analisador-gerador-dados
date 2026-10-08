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
