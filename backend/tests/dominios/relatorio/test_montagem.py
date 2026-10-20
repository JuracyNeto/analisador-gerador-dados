from app.dominios.relatorio.conteudo import (
    ApendiceFormulas,
    AvisoRelatorio,
    ConteudoRelatorio,
    FiguraRelatorio,
    FormulaApendice,
    GrupoFormulas,
    ItemMedida,
    LinhaTipo,
    ParRelatorio,
    SecaoBivariada,
    SecaoColuna,
    SecaoDetector,
    SecaoForma,
    SecaoGerador,
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
        colunas=(SecaoColuna("x", "Quantitativa contínua", 3, 0, None, forma),),
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


def _aviso(
    severidade: str, selo: str, titulo: str, figura: FiguraRelatorio | None
) -> AvisoRelatorio:
    return AvisoRelatorio(
        severidade=severidade,
        selo=selo,
        titulo=titulo,
        resumo="46% dos valores terminam em 0 ou 5.",
        por_que="Pessoas tendem a arredondar.",
        exemplo="Linhas 120 a 138: 70, 75, 80",
        pode_ser_normal="…a balança só mede de 5 em 5 kg.",
        o_que_fazer="Confira a origem dessas linhas.",
        detalhes=(
            ItemMedida("Teste", "Binomial unilateral"),
            ItemMedida(
                "p-valor", "p < 0,001", "chance de acontecer por acaso: menos de 1 em 1.000"
            ),
        ),
        figura=figura,
    )


def test_renderizar_gerador_e_detector_numera_secoes_e_figuras() -> None:
    gerador = SecaoGerador(
        subtitulo="Univariado · 3 valores · semente 1",
        parametros=(ItemMedida("Origem", "<i>x</i> (a.csv)"),),
        metodo="Normal com reescala",
        explicacao="Sorteamos 3 valores.",
        cabecalho_comparacao=("Medida", "Original", "Gerado (3)", "Diferença"),
        linhas_comparacao=(("Média", "1", "1", "0"),),
        figura=_figura("Sobreposição"),
    )
    avisos = (
        _aviso("alta", "⛔ Suspeita alta", "R1 · Bloco alinhado em <b>x</b>", _figura("Blocos")),
        _aviso("atencao", "⚠️ Atenção", "R4 · Muitos valores redondos em x", None),
    )
    detector = SecaoDetector(
        frase="Encontramos 2 alertas em 1 coluna",
        detalhe="x · 9 regras verificadas, 2 não se aplicam a este arquivo",
        contadores="1 suspeita alta · 1 de atenção · 0 informativos",
        avisos=avisos,
        nao_verificadas=("Lei de Benford não verificada em x: precisa de 100 valores ou mais.",),
        vazio=None,
    )
    conteudo = ConteudoRelatorio(
        nome_arquivo="a.csv",
        gerado_em="16/10/2026 10:00",
        subtitulo="a.csv",
        script_plotly="",
        leitura="Arquivo CSV.",
        bivariada=SecaoBivariada(_figura("Matriz"), "Resumo.", (), None, ()),
        gerador=gerador,
        detector=detector,
    )

    html = renderizar(conteudo)

    marcos = [
        "<h2>1. Leitura do arquivo</h2>",
        "<h2>2. Bivariada</h2>",
        "Figura 1 · Matriz",
        "<h2>3. Gerador de dados</h2>",
        "<h3>Como geramos</h3>",
        "<h3>Original × Gerado</h3>",
        "Figura 2 · Sobreposição",
        "<h2>4. Detector de dados artificiais</h2>",
        "1 suspeita alta · 1 de atenção · 0 informativos",
        '<article class="aviso sev-alta">',
        "Figura 3 · Blocos",
        '<article class="aviso sev-atencao">',
        "<h3>Regras não verificadas</h3>",
    ]
    posicoes = [html.index(marco) for marco in marcos]
    assert posicoes == sorted(posicoes)
    assert html.count("<h4>Detalhes técnicos</h4>") == 2
    assert '<p class="selo-severidade">⚠️ Atenção</p>' in html
    assert "R1 · Bloco alinhado em &lt;b&gt;x&lt;/b&gt;" in html
    assert "<dd>&lt;i&gt;x&lt;/i&gt; (a.csv)</dd>" in html
    assert '<dd>p &lt; 0,001 <span class="nota">· chance de acontecer' in html
    assert "{{" not in html
    assert "{%" not in html


def test_detector_sem_alertas_mostra_o_texto_vazio() -> None:
    vazio = "Nenhuma das 11 regras encontrou suspeitas."
    detector = SecaoDetector("Nenhum alerta", "11 regras verificadas", "0", (), (), vazio)
    conteudo = ConteudoRelatorio("a.csv", "16/10/2026", "a.csv", "", detector=detector)

    html = renderizar(conteudo)

    assert f"<p>{vazio}</p>" in html
    assert '<p class="contadores">' not in html
    assert "Regras não verificadas" not in html


def test_estilos_de_severidade_e_impressao() -> None:
    html = renderizar(ConteudoRelatorio("a.csv", "16/10/2026", "a.csv", ""))

    for token in ("--sev-alta: #b42318", "--sev-atencao: #995700", "--sev-info: #1d5fd1"):
        assert token in html
    # O texto do alerta não se divide; a figura pode ir para a página seguinte.
    assert ".aviso-texto { break-inside: avoid; }" in html
    quebra = (
        "section.coluna, section.bivariada, section.gerador, section.detector, section.apendice"
    )
    assert ".formulas li { margin: 3px 0; break-inside: avoid; }" in html
    assert f"{quebra} {{ break-before: page; }}" in html


def test_apendice_e_a_ultima_secao_com_latex_so_onde_ha() -> None:
    media = FormulaApendice("Média", "x̄ = Σxᵢ / n", r"\bar{x} = \frac{\sum x_i}{n}", "em <b>x</b>")
    r4 = FormulaApendice("R4 · Valores redondos", "P(X ≥ k)")
    apendice = ApendiceFormulas(
        (GrupoFormulas("Análise por coluna", (media,)), GrupoFormulas("Detector", (r4,)))
    )
    detector = SecaoDetector("Nenhum alerta", "11 regras", "0", (), (), "Nada.")
    conteudo = ConteudoRelatorio(
        "a.csv", "18/10/2026", "a.csv", "", leitura="CSV.", detector=detector, formulas=apendice
    )

    html = renderizar(conteudo)

    marcos = [
        "<h2>2. Detector de dados artificiais</h2>",
        "<h2>3. Fórmulas usadas</h2>",
        "<h3>Análise por coluna</h3>",
        "<h3>Detector</h3>",
    ]
    posicoes = [html.index(marco) for marco in marcos]
    assert posicoes == sorted(posicoes)
    latex = r'data-latex="\bar{x} = \frac{\sum x_i}{n}">x̄ = Σxᵢ / n</span>'
    assert f'<span class="formula" {latex}' in html
    assert '<span class="nota">· em &lt;b&gt;x&lt;/b&gt;</span>' in html
    assert '<span class="formula-texto">P(X ≥ k)</span>' in html
    assert html.count("data-latex=") == 1


def test_colunas_sem_lista_de_formulas() -> None:
    forma = SecaoForma(medidas=(ItemMedida("Assimetria (G₁)", "0,32"),))
    coluna = SecaoColuna("x", "Quantitativa contínua", 3, 0, None, forma)
    conteudo = ConteudoRelatorio("a.csv", "18/10/2026", "a.csv", "", colunas=(coluna,))

    html = renderizar(conteudo)

    assert "Fórmulas usadas" not in html
