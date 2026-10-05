import pytest

from app.compartilhado.tipos import TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets

CONTEUDO = b"id;sexo;peso;obs\n1;F;58,2;\n2;M;79,6;\n3;F;;\n4;M;63,0;\n"


@pytest.fixture
def servico(servico_datasets: ServicoDatasets) -> ServicoAnalise:
    return ServicoAnalise(servico_datasets)


@pytest.fixture
def dataset_id(servico_datasets: ServicoDatasets) -> str:
    return servico_datasets.importar(CONTEUDO, "dados.txt", OpcoesLeitura()).dataset_id


def test_analisar_coluna_numerica(servico: ServicoAnalise, dataset_id: str) -> None:
    analise = servico.analisar(dataset_id, "peso")

    assert (analise.tipo, analise.n, analise.n_faltantes) == (TipoVariavel.CONTINUA, 3, 1)


def test_analisar_com_classes(servico: ServicoAnalise, dataset_id: str) -> None:
    assert servico.analisar(dataset_id, "peso", classes=3).frequencias.k == 3


def test_identificador_fica_fora(servico: ServicoAnalise, dataset_id: str) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        servico.analisar(dataset_id, "id")

    assert erro.value.codigo == "COLUNA_IGNORADA"


def test_coluna_vazia(
    servico: ServicoAnalise, servico_datasets: ServicoDatasets, dataset_id: str
) -> None:
    servico_datasets.alterar_tipo(dataset_id, "obs", TipoVariavel.NOMINAL)

    with pytest.raises(EntradaInvalida) as erro:
        servico.analisar(dataset_id, "obs")

    assert erro.value.codigo == "COLUNA_VAZIA"


def test_posicao_so_para_numericas(servico: ServicoAnalise, dataset_id: str) -> None:
    posicao = servico.posicao(dataset_id, "peso", 70.0, "quartil")

    assert posicao.regiao == "3º quartil"
    with pytest.raises(EntradaInvalida) as erro:
        servico.posicao(dataset_id, "sexo", 1.0, "quartil")
    assert erro.value.codigo == "POSICAO_NAO_APLICAVEL"
