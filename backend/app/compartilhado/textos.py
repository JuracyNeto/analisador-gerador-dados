"""Utilitários de texto sem regra de negócio (spec 16)."""

import re
import unicodedata

_ESPACOS = re.compile(r"\s+")


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
