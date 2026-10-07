from app.dominios.relatorio.conteudo import ConteudoRelatorio, LinhaTipo
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
