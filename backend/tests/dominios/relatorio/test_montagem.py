from app.dominios.relatorio.conteudo import (
    ConteudoRelatorio,
    FiguraRelatorio,
    ItemMedida,
    LinhaTipo,
    ParRelatorio,
    SecaoBivariada,
    SecaoColuna,
    SecaoForma,
)
from app.dominios.relatorio.montagem import renderizar


def test_renderizar_escapa_textos_e_numera_secoes() -> None:
    conteudo = ConteudoRelatorio(
        nome_arquivo="a.csv",
        gerado_em="03/10/2026 10:00",
        subtitulo="a.csv · 3 linhas × 1 coluna",
        script_plotly="<script>/* plotly */</script>",
        leitura="Arquivo CSV.",
        tipos=(LinhaTipo("<b>x</b>", "Binária", "Tem só dois valores."),),
    )

    html = renderizar(conteudo)

    assert "<h2>1. Leitura do arquivo</h2>" in html
    assert "<h2>2. Tipos de variável</h2>" in html
    assert "&lt;b&gt;x&lt;/b&gt;" in html
    assert "<script>/* plotly */</script>" in html
    assert "Limpeza" not in html


def _figura(titulo: str) -> FiguraRelatorio:
    return FiguraRelatorio(titulo, "Resumo.", f"<div>{titulo}</div>")


def test_renderizar_forma_e_bivariada_numera_figuras_em_ordem() -> None:
    forma = SecaoForma(
        medidas=(ItemMedida("Assimetria (G₁)", "0,32", "Moderada à direita"),),
        ajustes=("Shapiro-Wilk: W = 0,99 · p = 0,4 ≥ 0,05. Os dados são compatíveis.",),
        figura=_figura("Histograma"),
    )
    par = ParRelatorio("x", "y", (ItemMedida("r de Pearson", "0,7"),), "Ŷ = 1 + 2·X", (), None)
    conteudo = ConteudoRelatorio(
        nome_arquivo="a.csv",
        gerado_em="09/10/2026 10:00",
        subtitulo="a.csv",
        script_plotly="",
        colunas=(SecaoColuna("x", "Quantitativa contínua", 3, 0, None, forma, ()),),
        bivariada=SecaoBivariada(_figura("Matriz"), "Resumo da matriz.", (par,), None, ()),
    )

    html = renderizar(conteudo)

    assert "<h3>Forma e distribuição</h3>" in html
    assert '<dd class="selo">Moderada à direita</dd>' in html
    assert html.index("Figura 1 · Histograma") < html.index("<h2>2. Bivariada</h2>")
    assert html.index("<h2>2. Bivariada</h2>") < html.index("Figura 2 · Matriz")
    assert '<span class="mono">y</span> em função de <span class="mono">x</span>' in html
    assert "Resumo da matriz." not in html  # a legenda da figura já traz o resumo
    assert "fᵢ" not in html
    assert "{{" not in html
