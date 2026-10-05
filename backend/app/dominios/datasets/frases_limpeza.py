"""Frases do log de limpeza: 1ª pessoa do plural, verbo no passado + quantidade (spec 16)."""

from app.compartilhado.textos import pluralizar


def _linhas(n: int) -> str:
    return f"{n} {pluralizar(n, 'linha', 'linhas')}"


def _valores(n: int) -> str:
    return f"{n} {pluralizar(n, 'valor', 'valores')}"


def duplicadas_removidas(n: int) -> str:
    return f"Removemos {_linhas(n)} {pluralizar(n, 'duplicada', 'duplicadas')}."


def vazias_removidas(n: int, coluna: str) -> str:
    return f"Removemos {_linhas(n)} sem valor em {coluna}."


def faltantes_preenchidos(n: int, coluna: str, com: str) -> str:
    faltantes = pluralizar(n, "faltante", "faltantes")
    return f"Preenchemos {_valores(n)} {faltantes} de {coluna} com {com}."


def fora_removidas(n: int, coluna: str) -> str:
    return f"Removemos {_linhas(n)} com {coluna} fora da faixa."


def fora_limitados(n: int, coluna: str, inferior: str, superior: str) -> str:
    return f"Limitamos {_valores(n)} de {coluna} à faixa de {inferior} a {superior}."


def fora_marcados(n: int, coluna: str) -> str:
    return f"Marcamos {_valores(n)} de {coluna} como faltantes por estarem fora da faixa."


def grafias_unificadas(n: int, coluna: str) -> str:
    return f"Unificamos {n} {pluralizar(n, 'grafia', 'grafias')} de {coluna}."


def textos_marcados(n: int, coluna: str) -> str:
    return f"Marcamos {n} {pluralizar(n, 'texto', 'textos')} de {coluna} como faltantes."
