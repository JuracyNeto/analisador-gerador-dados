from pathlib import Path

import pytest

from app.compartilhado.tipos import TipoVariavel
from app.core.config import Configuracao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import AcaoLimpeza, OpcoesLeitura, ServicoDatasets
from app.dominios.relatorio.servico import (
    SECOES_PADRAO,
    PedidoRelatorio,
    ServicoRelatorio,
    pares_mais_fortes,
)


@pytest.fixture
def servico(servico_datasets: ServicoDatasets) -> ServicoRelatorio:
    return ServicoRelatorio(servico_datasets, ServicoAnalise(servico_datasets))


@pytest.fixture
def dataset_id(servico_datasets: ServicoDatasets) -> str:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])
    return dataset_id


def test_pedido_padrao_tem_as_seis_secoes() -> None:
    assert PedidoRelatorio().secoes == SECOES_PADRAO
    assert SECOES_PADRAO == (
        "leitura",
        "tipos",
        "limpeza",
        "analises",
        "distribuicoes",
        "bivariada",
    )


def test_mini_relatorio_completo(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio())

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


def test_formulas_da_forma_so_com_distribuicoes(servico: ServicoRelatorio, dataset_id: str) -> None:
    so_analises = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("analises",), colunas=("peso_kg",))
    )
    so_forma = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("distribuicoes",), colunas=("peso_kg",))
    )

    assert "Forma e distribuição" not in so_analises
    assert "Assimetria (Fisher)" not in so_analises
    assert "Média:" in so_analises
    assert "Assimetria (Fisher)" in so_forma
    assert "Distribuição Normal" in so_forma
    assert "Média:" not in so_forma


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
    assert "Correlação de Pearson:" in html
    assert html.count("Plotly.newPlot(") >= 2


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
