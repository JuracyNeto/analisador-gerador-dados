"""Apêndice de fórmulas (spec 13, item 10; D151): as fórmulas das seções incluídas, sem repetir.

Função pura sobre o conteúdo já montado: cada seção traz as suas fórmulas (análise e forma de
cada coluna, Bivariada, Gerador e a fórmula de cada alerta do detector) e o apêndice só junta.
"""

from collections.abc import Callable, Iterable
from dataclasses import replace

from app.compartilhado.tipos import Formula
from app.dominios.relatorio import textos
from app.dominios.relatorio.conteudo import (
    ApendiceFormulas,
    ConteudoRelatorio,
    FormulaApendice,
    GrupoFormulas,
    SecaoColuna,
    SecaoDetector,
)

type Seletor = Callable[[SecaoColuna], tuple[Formula, ...] | None]
"""As fórmulas de um bloco da coluna; None quando o bloco não está no relatório."""


def _da_analise(coluna: SecaoColuna) -> tuple[Formula, ...] | None:
    return None if coluna.analises is None else coluna.analises.formulas


def _da_forma(coluna: SecaoColuna) -> tuple[Formula, ...] | None:
    return None if coluna.forma is None else coluna.forma.formulas


def _agrupar[T](entradas: Iterable[tuple[str, T, Iterable[str]]]) -> list[tuple[T, list[str]]]:
    """Um item por chave, na ordem em que aparece, com os nomes (sem repetir) de onde aparece."""
    itens: dict[str, T] = {}
    onde: dict[str, dict[str, None]] = {}
    for chave, item, nomes in entradas:
        itens.setdefault(chave, item)
        onde.setdefault(chave, {}).update(dict.fromkeys(nomes))
    return [(itens[chave], list(onde[chave])) for chave in itens]


def _item(formula: Formula, onde: str | None = None) -> FormulaApendice:
    return FormulaApendice(formula.nome, formula.texto, formula.latex or None, onde)


def _onde(colunas: list[str], com_o_bloco: int) -> str | None:
    if com_o_bloco > 1 and len(colunas) == com_o_bloco:
        return textos.EM_TODAS_AS_COLUNAS
    return textos.onde_formula(colunas)


def _por_coluna(
    colunas: tuple[SecaoColuna, ...], seletor: Seletor, ordem: tuple[str, ...]
) -> tuple[FormulaApendice, ...]:
    """Na ordem do catálogo (chaves fora dele no fim), com as colunas em que cada uma aparece."""
    blocos = [(coluna.coluna, formulas) for coluna in colunas if (formulas := seletor(coluna))]
    com_o_bloco = sum(seletor(coluna) is not None for coluna in colunas)
    agrupadas = _agrupar((f.chave, f, (nome,)) for nome, formulas in blocos for f in formulas)
    posicoes = {chave: indice for indice, chave in enumerate(ordem)}
    agrupadas.sort(key=lambda par: posicoes.get(par[0].chave, len(ordem)))
    return tuple(_item(formula, _onde(nomes, com_o_bloco)) for formula, nomes in agrupadas)


def _sem_repetir(formulas: Iterable[Formula]) -> tuple[FormulaApendice, ...]:
    return tuple(_item(formula) for formula, _ in _agrupar((f.chave, f, ()) for f in formulas))


def _do_detector(detector: SecaoDetector | None) -> tuple[FormulaApendice, ...]:
    """Uma fórmula por regra com alerta, com as colunas de todos os alertas dela."""
    if detector is None:
        return ()
    entradas = [(a.formula.nome, a.formula, a.colunas) for a in detector.avisos if a.formula]
    agrupadas = _agrupar(entradas)
    return tuple(replace(formula, onde=textos.onde_formula(nomes)) for formula, nomes in agrupadas)


def montar_apendice(conteudo: ConteudoRelatorio, ordem: tuple[str, ...]) -> ApendiceFormulas | None:
    """Grupos na ordem do documento; grupo sem fórmula sai; sem nenhum, não há apêndice.

    `ordem` = as chaves do catálogo da análise, na ordem em que as fórmulas aparecem nele.
    """
    colunas = conteudo.colunas or ()
    bivariada = conteudo.bivariada.formulas if conteudo.bivariada else ()
    gerador = conteudo.gerador.formulas if conteudo.gerador else ()
    candidatos = {
        "analises": _por_coluna(colunas, _da_analise, ordem),
        "distribuicoes": _por_coluna(colunas, _da_forma, ordem),
        "bivariada": _sem_repetir(bivariada),
        "gerador": _sem_repetir(gerador),
        "detector": _do_detector(conteudo.detector),
    }
    grupos = tuple(
        GrupoFormulas(textos.GRUPOS_FORMULAS[secao], formulas)
        for secao, formulas in candidatos.items()
        if formulas
    )
    return ApendiceFormulas(grupos) if grupos else None
