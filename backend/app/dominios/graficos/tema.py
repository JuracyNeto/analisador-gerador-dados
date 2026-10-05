"""Tema claro do Plotly para o relatório (D45, D47, ADR 0008).

Espelha os tokens do tema claro de `frontend/src/shared/ui/tokens.css`; um teste compara os dois.
O frontend aplica o tema dele por cima da figura; o relatório usa sempre este.
"""

from typing import Any

TOKENS_CLARO = {
    "--cor-texto": "#161a20",
    "--cor-texto-2": "#4b5462",
    "--graf-1": "#0b6aa8",
    "--graf-2": "#c4520a",
    "--graf-3": "#0b7a5a",
    "--graf-4": "#b0548f",
    "--graf-5": "#8f6400",
    "--graf-6": "#5a4bb5",
    "--graf-7": "#3f8fc4",
    "--graf-8": "#4b5563",
    "--graf-grade": "#e6e9ee",
    "--graf-eixo": "#868f9c",
    "--graf-fundo": "#ffffff",
}
PALETA = tuple(TOKENS_CLARO[f"--graf-{i}"] for i in range(1, 9))
COR_PRINCIPAL = TOKENS_CLARO["--graf-1"]
COR_REFERENCIA = TOKENS_CLARO["--graf-2"]
FONTE = "Inter, system-ui, sans-serif"


def _eixo() -> dict[str, Any]:
    return {
        "gridcolor": TOKENS_CLARO["--graf-grade"],
        "linecolor": TOKENS_CLARO["--graf-eixo"],
        "zeroline": False,
        "ticks": "",
        "title": {"font": {"size": 13, "color": TOKENS_CLARO["--cor-texto"]}},
    }


def layout_claro() -> dict[str, Any]:
    """Mesmo layout do `layoutTema` de docs/design/graficos-plotly.md, com as cores claras."""
    return {
        "font": {"family": FONTE, "size": 12, "color": TOKENS_CLARO["--cor-texto-2"]},
        "paper_bgcolor": TOKENS_CLARO["--graf-fundo"],
        "plot_bgcolor": TOKENS_CLARO["--graf-fundo"],
        "colorway": list(PALETA),
        "separators": ",.",
        "margin": {"l": 60, "r": 16, "t": 32, "b": 48},
        "xaxis": _eixo(),
        "yaxis": _eixo(),
        "bargap": 0.04,
    }


def mesclar(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Junta dois layouts; dicionários internos são mesclados, o resto vem de `extra`."""
    resultado = dict(base)
    for chave, valor in extra.items():
        atual = resultado.get(chave)
        if isinstance(atual, dict) and isinstance(valor, dict):
            resultado[chave] = mesclar(atual, valor)
        else:
            resultado[chave] = valor
    return resultado
