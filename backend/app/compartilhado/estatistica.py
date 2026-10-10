"""Utilitários estatísticos sem regra de negócio, usados por mais de um domínio (padroes §2)."""

from collections.abc import Sequence

ALFA = 0.05  # nível de significância padrão (00-visao-geral.md)
MINIMO_ESPERADO = 5.0


def _juntar(observados: list[float], esperados: list[float], i: int, j: int) -> None:
    """Soma o grupo j no grupo i e apaga o j (i e j vizinhos)."""
    observados[i] += observados.pop(j)
    esperados[i] += esperados.pop(j)


def _indice_pequeno(esperados: list[float], minimo: float) -> int | None:
    return next((i for i, valor in enumerate(esperados) if valor < minimo), None)


def _vizinho_menor(esperados: list[float], i: int) -> int:
    if i == 0:
        return 1
    if i == len(esperados) - 1:
        return i - 1
    return i - 1 if esperados[i - 1] <= esperados[i + 1] else i + 1


def agrupar_esperados_pequenos(
    observados: Sequence[float], esperados: Sequence[float], minimo: float = MINIMO_ESPERADO
) -> tuple[list[float], list[float]]:
    """Junta grupos vizinhos até cada esperado ser ≥ mínimo (condição do qui-quadrado)."""
    obs, esp = list(observados), list(esperados)
    while len(esp) > 1:
        i = _indice_pequeno(esp, minimo)
        if i is None:
            break
        vizinho = _vizinho_menor(esp, i)
        _juntar(obs, esp, min(i, vizinho), max(i, vizinho))
    return obs, esp
