import re

from app.core.config import RAIZ_REPOSITORIO
from app.dominios.graficos.tema import TOKENS_CLARO, layout_claro, mesclar

TOKENS_CSS = RAIZ_REPOSITORIO / "frontend" / "src" / "shared" / "ui" / "tokens.css"
_DECLARACAO = re.compile(r"(--[\w-]+):\s*([^;]+);")


def _tokens_do_tema_claro() -> dict[str, str]:
    """Primeiro bloco do tokens.css (`:root, [data-tema='claro'] { … }`)."""
    css = TOKENS_CSS.read_text(encoding="utf-8")
    bloco = css[css.index("{") + 1 : css.index("}")]
    return {nome: valor.strip().lower() for nome, valor in _DECLARACAO.findall(bloco)}


def test_tema_do_relatorio_espelha_o_tokens_css() -> None:
    # ADR 0008: os valores claros ficam duplicados em Python; este teste impede que divirjam.
    tokens = _tokens_do_tema_claro()

    assert {nome: tokens[nome] for nome in TOKENS_CLARO} == TOKENS_CLARO


def test_layout_claro_usa_virgula_decimal_e_a_paleta() -> None:
    layout = layout_claro()

    assert layout["separators"] == ",."
    assert layout["colorway"][0] == TOKENS_CLARO["--graf-1"]
    assert layout["paper_bgcolor"] == "#ffffff"


def test_mesclar_preserva_dicionarios_internos() -> None:
    base = {"xaxis": {"gridcolor": "#eee", "title": {"font": {"size": 13}}}, "bargap": 0.04}
    extra = {"xaxis": {"title": {"text": "peso_kg"}}, "bargap": 0}

    resultado = mesclar(base, extra)

    assert resultado == {
        "xaxis": {"gridcolor": "#eee", "title": {"font": {"size": 13}, "text": "peso_kg"}},
        "bargap": 0,
    }
