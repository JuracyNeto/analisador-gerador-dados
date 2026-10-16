"""Tabela Original × Gerado em texto, como na tela 6 (D110, D115)."""

import re

from app.compartilhado.numeros import (
    MENOS,
    formatar_com_sinal,
    formatar_fixo,
    formatar_inteiro,
    formatar_numero,
    formatar_percentual,
)

VAZIO = "—"
PREFIXO_FREQUENCIA = "fr% · "
ESTATISTICA_N = "n"
SUFIXO_PONTOS = " p.p."
_DECIMAIS = re.compile(r",(\d+)")


def _eh_frequencia(estatistica: str) -> bool:
    return estatistica.startswith(PREFIXO_FREQUENCIA)


def _valor(estatistica: str, valor: float | None) -> str:
    if valor is None:
        return VAZIO
    if estatistica == ESTATISTICA_N:
        return formatar_inteiro(round(valor))
    return formatar_percentual(valor) if _eh_frequencia(estatistica) else formatar_com_sinal(valor)


def _casas(texto: str) -> int:
    casamento = _DECIMAIS.search(texto)
    return len(casamento.group(1)) if casamento else 0


def _sinal(valor: float) -> str:
    if valor > 0:
        return "+"
    return MENOS if valor < 0 else ""


def _diferenca(estatistica: str, diferenca: float | None, casas: int) -> str:
    """Na precisão dos valores mostrados: o resto de arredondamento da reescala não aparece."""
    if diferenca is None:
        return VAZIO
    arredondada = round(diferenca, casas)
    absoluta = formatar_fixo(0, casas) if arredondada == 0 else formatar_numero(abs(arredondada))
    texto = f"{_sinal(arredondada)}{absoluta}"
    return f"{texto}{SUFIXO_PONTOS}" if _eh_frequencia(estatistica) else texto


def linha_comparacao(
    estatistica: str, original: float | None, gerado: float | None, diferenca: float | None
) -> tuple[str, str, str, str]:
    """(medida, original, gerado, diferença com sinal); frequências em pontos percentuais."""
    textos = (_valor(estatistica, original), _valor(estatistica, gerado))
    casas = max(_casas(texto) for texto in textos)
    return (estatistica, *textos, _diferenca(estatistica, diferenca, casas))
