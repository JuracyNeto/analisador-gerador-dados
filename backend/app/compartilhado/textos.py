"""Utilitários de texto sem regra de negócio (spec 16)."""

import re
import unicodedata

from app.compartilhado.numeros import P_VALOR_MINIMO, formatar_inteiro

_ESPACOS = re.compile(r"\s+")
METADE = 0.5


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sem acento e com espaços colapsados: '  São  Paulo ' → 'sao paulo'."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return _ESPACOS.sub(" ", sem_acento).strip().lower()


def pluralizar(quantidade: int, singular: str, plural: str) -> str:
    """Escolhe singular ou plural pela quantidade (1 linha · 3 linhas)."""
    return singular if quantidade == 1 else plural


def juntar_lista(itens: list[str]) -> str:
    """Junta itens em português: 'a', 'a e b', 'a, b e c'."""
    if len(itens) <= 1:
        return "".join(itens)
    return f"{', '.join(itens[:-1])} e {itens[-1]}"


def p_valor_em_palavras(p: float) -> str:
    """Chance de acontecer por acaso em palavras (spec 16): "cerca de 1 em 50"."""
    if p < P_VALOR_MINIMO:
        return "menos de 1 em 1.000"
    if p >= METADE:
        return "mais de 1 em 2"
    return f"cerca de 1 em {formatar_inteiro(round(1 / p))}"
