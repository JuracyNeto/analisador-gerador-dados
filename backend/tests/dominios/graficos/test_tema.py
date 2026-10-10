import re

from app.core.config import RAIZ_REPOSITORIO
from app.dominios.graficos.tema import (
    CORES_CLARAS,
    PAPEL_DIVERGENTE,
    TOKENS_CLARO,
    colorir,
    layout_claro,
    mesclar,
)

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


def test_colorir_pinta_pelo_papel_sem_mudar_a_entrada() -> None:
    dados = {
        "data": [
            {"type": "bar", "meta": "principal", "marker": {"opacity": 0.85}},
            {"type": "scatter", "mode": "lines+markers", "meta": "principal", "line": {"width": 2}},
            {"type": "box", "meta": "principal"},
            {"type": "scatter", "mode": "markers", "meta": "referencia"},
            {"type": "pie", "labels": ["a", "b"], "values": [1, 2]},
        ],
        "layout": {},
    }
    cores = {"principal": "#111111", "referencia": "#222222"}

    pintados = colorir(dados, cores)["data"]

    assert pintados[0]["marker"] == {"opacity": 0.85, "color": "#111111"}
    assert "line" not in pintados[0]
    assert pintados[1]["line"] == {"width": 2, "color": "#111111"}
    assert pintados[1]["marker"] == {"color": "#111111"}
    assert pintados[2]["line"] == {"color": "#111111"}
    assert pintados[3]["marker"] == {"color": "#222222"}
    assert "line" not in pintados[3]
    assert pintados[4] == dados["data"][4]
    assert dados["data"][0]["marker"] == {"opacity": 0.85}


def test_cores_claras_vem_da_paleta_do_tema_claro() -> None:
    assert {
        "principal": TOKENS_CLARO["--graf-1"],
        "referencia": TOKENS_CLARO["--graf-2"],
    } == CORES_CLARAS


def test_colorir_pinta_o_heatmap_com_a_escala_divergente() -> None:
    dados = {"data": [{"type": "heatmap", "z": [[1]], "meta": PAPEL_DIVERGENTE}]}

    traco = colorir(dados, CORES_CLARAS)["data"][0]

    assert traco["colorscale"] == [
        [0, TOKENS_CLARO["--graf-2"]],
        [0.5, TOKENS_CLARO["--graf-fundo"]],
        [1, TOKENS_CLARO["--graf-1"]],
    ]
    assert "marker" not in traco
    assert traco["textfont"] == {"color": TOKENS_CLARO["--cor-texto"]}
