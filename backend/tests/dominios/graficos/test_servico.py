from app.dominios.graficos.servico import (
    codigo_plotlyjs,
    endereco_plotlyjs_cdn,
    figura_html,
)


def test_figura_html_aplica_o_tema_claro_e_escapa_o_script() -> None:
    dados = {"data": [{"type": "bar", "x": ["</script>"], "y": [1]}], "layout": {"bargap": 0}}

    html = figura_html("figura-1", dados)

    assert html.startswith('<div id="figura-1" class="grafico"></div>')
    assert "Plotly.newPlot(" in html
    assert '"separators": ",."' in html
    assert '"bargap": 0' in html
    assert '</script>"' not in html


def test_plotlyjs_embutido_e_cdn_da_mesma_versao() -> None:
    codigo = codigo_plotlyjs()
    endereco = endereco_plotlyjs_cdn()

    assert "plotly.js v" in codigo[:200]
    assert endereco.startswith("https://cdn.plot.ly/plotly-")
    versao = endereco.removeprefix("https://cdn.plot.ly/plotly-").removesuffix(".min.js")
    assert f"plotly.js v{versao}" in codigo[:200]


def test_figura_html_pinta_os_tracos_com_as_cores_claras() -> None:
    dados = {"data": [{"type": "bar", "meta": "principal", "x": ["a"], "y": [1]}], "layout": {}}

    html = figura_html("figura-1", dados)

    assert '"color": "#0b6aa8"' in html
