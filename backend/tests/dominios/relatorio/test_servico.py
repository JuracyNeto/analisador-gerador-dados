from pathlib import Path

import pytest
from markupsafe import escape

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.tipos import TipoVariavel
from app.core.config import Configuracao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import AcaoLimpeza, OpcoesLeitura, ServicoDatasets
from app.dominios.detector.servico import ServicoDetector
from app.dominios.gerador.servico import (
    Gerado,
    Origem,
    OrigemPar,
    PedidoBivariado,
    PedidoUnivariado,
    RepositorioGerados,
    ServicoGerador,
)
from app.dominios.relatorio.servico import (
    SECOES_PADRAO,
    PedidoRelatorio,
    Secao,
    ServicoRelatorio,
    pares_mais_fortes,
)

SECOES_DA_ANALISE: tuple[Secao, ...] = (
    "leitura",
    "tipos",
    "limpeza",
    "analises",
    "distribuicoes",
    "bivariada",
)


@pytest.fixture
def servico_gerador(servico_datasets: ServicoDatasets) -> ServicoGerador:
    config = Configuracao()
    gerados = RepositorioGerados[Gerado](config.max_gerados)
    return ServicoGerador(servico_datasets, ServicoAnalise(servico_datasets), gerados, config)


@pytest.fixture
def servico(servico_datasets: ServicoDatasets, servico_gerador: ServicoGerador) -> ServicoRelatorio:
    analise = ServicoAnalise(servico_datasets)
    detector = ServicoDetector(servico_datasets, analise)
    return ServicoRelatorio(servico_datasets, analise, servico_gerador, detector)


@pytest.fixture
def dataset_id(servico_datasets: ServicoDatasets) -> str:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])
    return dataset_id


def test_pedido_padrao_tem_as_nove_secoes() -> None:
    assert PedidoRelatorio().secoes == SECOES_PADRAO
    assert PedidoRelatorio().gerado is None
    assert SECOES_PADRAO == (
        "leitura",
        "tipos",
        "limpeza",
        "analises",
        "distribuicoes",
        "bivariada",
        "gerador",
        "detector",
        "formulas",
    )


def test_mini_relatorio_completo(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=SECOES_DA_ANALISE))

    assert "Relatório estatístico" in html
    assert "pesquisa_saude.txt · 227 linhas após limpeza × 8 colunas" in html
    assert "1. Leitura do arquivo" in html
    assert "separado por ponto e vírgula, decimal com vírgula" in html
    assert "Removemos 3 linhas duplicadas." in html
    assert 'Análise de <span class="mono">peso_kg</span>' in html
    assert "Figura 1 · " in html
    # 7 colunas + forma de idade, altura_m e peso_kg + matriz (sem par com |r| ≥ 0,3)
    assert html.count("Plotly.newPlot(") == 11
    assert "cdn.plot.ly/plotly-" in html
    assert '<dd class="mono">-' not in html  # negativos com o sinal de menos (−)
    assert "inteligência artificial" not in html.lower()


def test_identificador_fica_fora(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("analises",)))

    assert 'Análise de <span class="mono">id</span>' not in html
    assert "Leitura do arquivo" not in html


def test_colunas_escolhidas_e_offline(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("analises",), colunas=("idade",), offline=True)
    )

    assert html.count("Plotly.newPlot(") == 1
    assert 'src="https://cdn.plot.ly' not in html
    assert "plotly.js v" in html


def test_sem_limpeza_avisa(servico: ServicoRelatorio, servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.alterar_tipo(dataset_id, "idade", TipoVariavel.DISCRETA)

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("limpeza", "tipos")))

    assert "Nenhuma ação de limpeza foi aplicada." in html
    assert "Tipo escolhido por você." in html


def test_coluna_de_datas_so_aparece_nos_tipos(
    servico: ServicoRelatorio, servico_datasets: ServicoDatasets
) -> None:
    conteudo = b"quando;peso\n07/10/2026;58,2\n08/10/2026;79,6\n09/10/2026;63,0\n"
    dataset_id = servico_datasets.importar(conteudo, "datas.txt", OpcoesLeitura()).dataset_id

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("tipos", "analises")))

    assert "Data ou hora (ignorada)" in html
    assert 'Análise de <span class="mono">quando</span>' not in html
    assert 'Análise de <span class="mono">peso</span>' in html


def test_distribuicoes_por_coluna(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("distribuicoes",), colunas=("peso_kg", "cidade"))
    )

    assert html.count("<h3>Forma e distribuição</h3>") == 2
    assert "Shapiro-Wilk: W = " in html
    assert "curva Normal" in html
    assert "Assimetria (G₁)" in html
    assert "Forma e distribuição não se aplica a qualitativas nominais" in html
    assert '<th scope="col">fᵢ</th>' not in html


def _apendice(html: str) -> str:
    """O trecho do apêndice (do título ao rodapé)."""
    return html[html.index("Fórmulas usadas</h2>") : html.index('<footer class="rodape">')]


def test_formulas_da_forma_so_com_distribuicoes(servico: ServicoRelatorio, dataset_id: str) -> None:
    so_analises = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("analises", "formulas"), colunas=("peso_kg",))
    )
    so_forma = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("distribuicoes", "formulas"), colunas=("peso_kg",))
    )

    assert "Forma e distribuição</h3>" not in _apendice(so_analises)
    assert "Assimetria (Fisher)" not in so_analises
    assert '<span class="nome-formula">Média</span>' in _apendice(so_analises)
    assert "<h3>Forma e distribuição</h3>" in _apendice(so_forma)
    assert '<span class="nome-formula">Distribuição Normal</span>' in _apendice(so_forma)
    assert '<span class="nome-formula">Média</span>' not in so_forma


def test_apendice_junta_as_formulas_das_colunas(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=(*SECOES_DA_ANALISE, "formulas")))

    apendice = _apendice(html)
    assert html.count('<span class="nome-formula">Média</span>') == 1
    assert html.count("<h3>Fórmulas usadas</h3>") == 0
    grupos = ["<h3>Análise por coluna</h3>", "<h3>Forma e distribuição</h3>"]
    assert [apendice.index(g) for g in grupos] == sorted(apendice.index(g) for g in grupos)
    proporcao = apendice[apendice.index("Proporção</span>") :]
    assert proporcao[: proporcao.index("</li>")].endswith('<span class="nota">· em sexo</span>')
    frequencia = apendice[apendice.index("Frequência relativa</span>") :]
    assert "· em todas as colunas</span>" in frequencia[: frequencia.index("</li>")]


@pytest.mark.parametrize("secoes", [("leitura", "formulas"), ("formulas",)])
def test_sem_formulas_nas_secoes_nao_ha_apendice(
    servico: ServicoRelatorio, dataset_id: str, secoes: tuple[Secao, ...]
) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=secoes))

    assert "Fórmulas usadas" not in html


def test_apendice_com_gerador_e_detector(
    servico: ServicoRelatorio, servico_gerador: ServicoGerador, servico_datasets: ServicoDatasets
) -> None:
    dataset_id = servico_datasets.importar_exemplo("alturas_plantadas.txt").dataset_id
    pedido = PedidoUnivariado(x=100, origem=Origem(dataset_id, "peso_kg"), semente=42)
    gerado = servico_gerador.univariado(pedido)
    secoes: tuple[Secao, ...] = ("gerador", "detector", "formulas")

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes, gerado=gerado.gerado_id))

    apendice = _apendice(html)
    assert apendice.index("<h3>Gerador</h3>") < apendice.index("<h3>Detector</h3>")
    assert '<span class="nome-formula">Reescala exata</span>' in apendice
    assert '<span class="nome-formula">R1 · Bloco alinhado</span>' in apendice
    assert "· em peso_kg</span>" in apendice
    assert '<span class="formula-texto">dᵤ = |x̄_bloco − x̄_resto|' in apendice


def test_analises_e_distribuicoes_numeram_as_figuras(
    servico: ServicoRelatorio, dataset_id: str
) -> None:
    html = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("analises", "distribuicoes"), colunas=("peso_kg",))
    )

    assert html.index("Figura 1 · ") < html.index("<h3>Forma e distribuição</h3>")
    assert html.index("<h3>Forma e distribuição</h3>") < html.index("Figura 2 · ")
    assert html.count("Plotly.newPlot(") == 2


def test_pares_mais_fortes_ordena_e_corta() -> None:
    colunas = ("a", "b", "c", "d")
    valores = (
        (1.0, 0.5, -0.9, 0.31),
        (0.5, 1.0, 0.1, 0.5),
        (-0.9, 0.1, 1.0, None),
        (0.31, 0.5, None, 1.0),
    )

    assert pares_mais_fortes(colunas, valores) == (("a", "c"), ("a", "b"), ("b", "d"))
    assert pares_mais_fortes(colunas, valores, limite=5) == (
        ("a", "c"),
        ("a", "b"),
        ("b", "d"),
        ("a", "d"),
    )


def test_bivariada_com_notas(servico: ServicoRelatorio, servico_datasets: ServicoDatasets) -> None:
    conteudo = (Path(Configuracao().pasta_exemplos) / "notas_turma.csv").read_bytes()
    dataset_id = servico_datasets.importar(conteudo, "notas_turma.csv", OpcoesLeitura()).dataset_id

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("bivariada",)))

    assert "<h2>1. Bivariada</h2>" in html
    assert "Matriz de correlação" in html
    titulo_par = '<span class="mono">nota_p2</span> em função de <span class="mono">nota_p1</span>'
    assert titulo_par in html
    assert "Ŷ = " in html
    assert "Fórmulas usadas" not in html  # as fórmulas ficam no apêndice (D151)
    assert html.count("Plotly.newPlot(") >= 2
    com_formulas = servico.gerar(dataset_id, PedidoRelatorio(secoes=("bivariada", "formulas")))
    assert '<span class="nome-formula">Correlação de Pearson</span>' in _apendice(com_formulas)


def test_bivariada_com_uma_coluna_numerica(
    servico: ServicoRelatorio, servico_datasets: ServicoDatasets
) -> None:
    conteudo = b"id;nome;idade\n1;Ana;20\n2;Bia;31\n3;Caio;45\n4;Davi;28\n"
    dataset_id = servico_datasets.importar(conteudo, "poucas.txt", OpcoesLeitura()).dataset_id

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("bivariada",)))

    assert "Precisa de pelo menos duas colunas numéricas" in html
    assert "Plotly.newPlot(" not in html


def test_bivariada_sem_par_forte(
    servico: ServicoRelatorio, servico_datasets: ServicoDatasets
) -> None:
    conteudo = b"x;y\n1;5\n2;1\n3;4\n4;2\n5;5\n6;1\n"
    dataset_id = servico_datasets.importar(conteudo, "fraca.txt", OpcoesLeitura()).dataset_id

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("bivariada",)))

    assert "Nenhum par de colunas numéricas tem correlação moderada ou forte" in html
    assert html.count("Plotly.newPlot(") == 1


def _gerar_peso(servico_gerador: ServicoGerador, dataset_id: str) -> Gerado:
    pedido = PedidoUnivariado(x=500, origem=Origem(dataset_id, "peso_kg"), semente=42)
    return servico_gerador.univariado(pedido)


def test_secao_gerador_com_a_ultima_geracao(
    servico: ServicoRelatorio, servico_gerador: ServicoGerador, dataset_id: str
) -> None:
    gerado = _gerar_peso(servico_gerador, dataset_id)

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("gerador",), gerado=gerado.gerado_id))

    assert "<h2>1. Gerador de dados</h2>" in html
    assert "Univariado · 500 valores · semente 42" in html
    assert "<dt>Origem</dt><dd>peso_kg (pesquisa_saude.txt)</dd>" in html
    assert f"<dt>Método</dt><dd>{gerado.metodo}</dd>" in html
    assert "<h3>Como geramos</h3>" in html
    assert f"<p>{gerado.explicacao}</p>" in html
    assert '<th scope="col">Gerado (500)</th>' in html
    media = next(linha for linha in gerado.comparacao if linha.estatistica == "Média")
    assert media.original is not None
    assert media.gerado is not None
    valor_original = formatar_numero(media.original)
    assert f'<td>Média</td><td class="numero">{valor_original}</td>' in html
    assert "Figura 1 · " in html
    assert html.count("Plotly.newPlot(") == 1


def test_secao_gerador_bivariada(
    servico: ServicoRelatorio, servico_gerador: ServicoGerador, dataset_id: str
) -> None:
    pedido = PedidoBivariado(n=300, origem=OrigemPar(dataset_id, "altura_m", "peso_kg"), semente=7)
    gerado = servico_gerador.bivariado(pedido)

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("gerador",), gerado=gerado.gerado_id))

    assert "Bivariado · 300 pares · semente 7" in html
    assert "<td>Correlação (r)</td>" in html
    assert html.count("Plotly.newPlot(") == 1


@pytest.mark.parametrize("gerado", [None, "nao-existe"])
def test_sem_geracao_a_secao_gerador_sai(
    servico: ServicoRelatorio, dataset_id: str, gerado: str | None
) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("leitura", "gerador"), gerado=gerado))

    assert "<h2>1. Leitura do arquivo</h2>" in html
    assert "Gerador de dados</h2>" not in html


def test_secao_detector_com_alturas_plantadas(
    servico: ServicoRelatorio, servico_datasets: ServicoDatasets
) -> None:
    dataset_id = servico_datasets.importar_exemplo("alturas_plantadas.txt").dataset_id
    detector = ServicoDetector(servico_datasets, ServicoAnalise(servico_datasets))
    resultado = detector.analisar(dataset_id)

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("detector",)))

    assert "<h2>1. Detector de dados artificiais</h2>" in html
    assert resultado.resumo.frase in html
    assert {"R1", "R3", "R4", "R5", "R10"} <= {aviso.regra for aviso in resultado.avisos}
    titulos = [f"<h3>{escape(f'{a.regra} · {a.titulo}')}</h3>" for a in resultado.avisos]
    posicoes = [html.index(titulo) for titulo in titulos]
    assert posicoes == sorted(posicoes)
    assert html.count("<h4>Detalhes técnicos</h4>") == len(resultado.avisos)
    assert "<dt>Teste</dt><dd>Binomial unilateral</dd>" in html
    assert "⛔ Suspeita alta" in html
    assert html.index("<h3>R1 · ") < html.index("Figura 1 · ")
    figuras = sum(aviso.figura is not None for aviso in resultado.avisos)
    assert html.count("Plotly.newPlot(") == figuras
    assert "<h3>Regras não verificadas</h3>" in html
    for nao_aplicada in resultado.nao_aplicadas:
        assert str(escape(nao_aplicada.frase)) in html


def test_secao_detector_com_alturas_reais(
    servico: ServicoRelatorio, servico_datasets: ServicoDatasets
) -> None:
    dataset_id = servico_datasets.importar_exemplo("alturas_reais.txt").dataset_id

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("detector",)))

    assert "⛔ Suspeita alta" not in html
    assert "⚠️ Atenção" not in html
    assert "<h3>Regras não verificadas</h3>" in html


def test_secao_detector_sem_alertas(
    servico: ServicoRelatorio, servico_datasets: ServicoDatasets
) -> None:
    conteudo = b"x;y\n1;5\n2;1\n3;4\n4;2\n5;5\n6;1\n"
    dataset_id = servico_datasets.importar(conteudo, "pequeno.txt", OpcoesLeitura()).dataset_id

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("detector",)))

    assert "Nenhuma das 11 regras encontrou suspeitas." in html
    assert "de atenção" not in html
    assert "<h4>Detalhes técnicos</h4>" not in html
