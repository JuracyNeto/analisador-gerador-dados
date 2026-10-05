"""Dicionário de escalas ordinais conhecidas (spec 02) e ordenação de categorias."""

import re
from collections.abc import Iterable

from app.compartilhado.textos import normalizar_texto

# Cada escala é uma sequência de níveis; um nível pode ter sinônimos (ótimo = excelente).
type Escala = tuple[tuple[str, ...], ...]

ESCALAS: tuple[Escala, ...] = (
    (("muito baixo",), ("baixo",), ("medio",), ("alto",), ("muito alto",)),
    (("pessimo",), ("ruim",), ("regular",), ("bom",), ("otimo", "excelente")),
    (
        ("discordo totalmente",),
        ("discordo",),
        ("neutro",),
        ("concordo",),
        ("concordo totalmente",),
    ),
    (("nunca",), ("raramente",), ("as vezes",), ("frequentemente",), ("sempre",)),
    (("pp",), ("p",), ("m",), ("g",), ("gg",), ("xg",)),
    (
        ("fundamental incompleto",),
        ("fundamental",),
        ("medio incompleto",),
        ("medio",),
        ("superior incompleto",),
        ("superior",),
        ("pos-graduacao", "pos graduacao", "pos"),
    ),
    (("pequeno",), ("medio",), ("grande",)),
    (("leve",), ("moderado",), ("grave",)),
)

_ORDINAL_NUMERICO = re.compile(r"^(\d+)\s*[º°ª]$")


def _posicoes(escala: Escala) -> dict[str, int]:
    return {nome: nivel for nivel, sinonimos in enumerate(escala) for nome in sinonimos}


def _posicao_numerica(valor: str) -> int | None:
    casamento = _ORDINAL_NUMERICO.match(valor.strip())
    return int(casamento.group(1)) if casamento else None


def _ordenar_por(valores: Iterable[str], posicoes: dict[str, int]) -> tuple[str, ...] | None:
    lista = list(valores)
    if not all(normalizar_texto(v) in posicoes for v in lista):
        return None
    return tuple(sorted(lista, key=lambda v: (posicoes[normalizar_texto(v)], v)))


def _ordenar_numericos(valores: Iterable[str]) -> tuple[str, ...] | None:
    lista = list(valores)
    numeros = {v: _posicao_numerica(v) for v in lista}
    if any(n is None for n in numeros.values()):
        return None
    return tuple(sorted(lista, key=lambda v: (numeros[v] or 0, v)))


def ordenar_por_escala(valores: Iterable[str]) -> tuple[str, ...] | None:
    """Categorias na ordem da 1ª escala que contém todas elas; None se nenhuma servir."""
    lista = list(valores)
    for escala in ESCALAS:
        ordenados = _ordenar_por(lista, _posicoes(escala))
        if ordenados is not None:
            return ordenados
    return _ordenar_numericos(lista)
