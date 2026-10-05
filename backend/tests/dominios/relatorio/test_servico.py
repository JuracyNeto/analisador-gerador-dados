import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import AcaoLimpeza, ServicoDatasets
from app.dominios.relatorio.servico import PedidoRelatorio, ServicoRelatorio


@pytest.fixture
def servico(servico_datasets: ServicoDatasets) -> ServicoRelatorio:
    return ServicoRelatorio(servico_datasets, ServicoAnalise(servico_datasets))


@pytest.fixture
def dataset_id(servico_datasets: ServicoDatasets) -> str:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])
    return dataset_id


def test_mini_relatorio_completo(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio())

    assert "Relatório estatístico" in html
    assert "pesquisa_saude.txt · 227 linhas após limpeza × 8 colunas" in html
    assert "1. Leitura do arquivo" in html
    assert "separado por ponto e vírgula, decimal com vírgula" in html
    assert "Removemos 3 linhas duplicadas." in html
    assert 'Análise de <span class="mono">peso_kg</span>' in html
    assert "Figura 1 · " in html
    assert html.count("Plotly.newPlot(") == 7
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
