"""Erros do domínio gerador (spec 14, formato da spec 16)."""

from app.compartilhado.textos import juntar_lista
from app.compartilhado.tipos import TipoVariavel
from app.core.erros import EntradaInvalida, NaoEncontrado

TIPOS_SO_PRESERVAR = {
    TipoVariavel.NOMINAL: "qualitativas nominais",
    TipoVariavel.ORDINAL: "qualitativas ordinais",
    TipoVariavel.IDENTIFICADOR: "identificadores",
    TipoVariavel.DATA: "datas",
}
POR_QUE_NAO_GERAVEL = {
    TipoVariavel.IDENTIFICADOR: "é um identificador",
    TipoVariavel.DATA: "tem datas",
}
PARAMETROS = "PARAMETROS_INCOMPLETOS"


def gerado_nao_encontrado() -> NaoEncontrado:
    return NaoEncontrado(
        "GERADO_NAO_ENCONTRADO",
        "Os dados gerados não estão mais disponíveis.",
        "Gere de novo na etapa Gerador.",
    )


def modo_nao_aplicavel(tipo: TipoVariavel) -> EntradaInvalida:
    return EntradaInvalida(
        "MODO_NAO_APLICAVEL",
        f"Novos parâmetros não se aplicam a {TIPOS_SO_PRESERVAR.get(tipo, tipo)}: "
        "só dá para preservar as frequências.",
        'Escolha "Preservar estatísticas".',
    )


def parametros_incompletos(campos: list[str]) -> EntradaInvalida:
    return EntradaInvalida(
        PARAMETROS,
        f"Informe {juntar_lista(campos)} para gerar com novos parâmetros.",
        "Preencha os campos e gere de novo.",
    )


def origem_obrigatoria() -> EntradaInvalida:
    return EntradaInvalida(
        PARAMETROS,
        "Escolha uma coluna de origem para preservar as estatísticas.",
        'Ou use "Parâmetros manuais".',
    )


def coluna_nao_geravel(coluna: str, tipo: TipoVariavel) -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNA_NAO_GERAVEL",
        f"A coluna {coluna} {POR_QUE_NAO_GERAVEL.get(tipo, 'não tem valores')} "
        "e não pode servir de origem.",
        "Escolha outra coluna.",
    )
