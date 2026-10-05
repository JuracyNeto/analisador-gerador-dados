import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.core.config import Configuracao
from app.core.erros import ArquivoGrande, NaoEncontrado
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets

CONTEUDO = b"id;sexo;peso\n1;F;58,2\n2;M;79,6\n3;F;\n4;M;63,0\n"


def _importar(servico: ServicoDatasets) -> str:
    return servico.importar(CONTEUDO, "dados.txt", OpcoesLeitura()).dataset_id


def test_importar_guarda_original_e_atual_separados(servico_datasets: ServicoDatasets) -> None:
    dataset = servico_datasets.obter(_importar(servico_datasets))

    assert dataset.original is not dataset.atual
    assert dataset.tipos["sexo"].tipo == TipoVariavel.BINARIA


def test_importar_devolve_previa_e_colunas(servico_datasets: ServicoDatasets) -> None:
    importacao = servico_datasets.importar(CONTEUDO, "dados.txt", OpcoesLeitura())

    assert [linha.linha for linha in importacao.previa] == [1, 2, 3, 4]
    assert importacao.previa[2].valores["peso"] is None
    assert [c.coluna for c in importacao.colunas] == ["id", "sexo", "peso"]


def test_arquivo_acima_do_limite() -> None:
    config = Configuracao(limite_arquivo_mb=0)
    servico = ServicoDatasets(RepositorioDatasets(1), config)

    with pytest.raises(ArquivoGrande):
        servico.importar(b"a\n1\n", "a.csv", OpcoesLeitura())


def test_importar_exemplo(servico_datasets: ServicoDatasets) -> None:
    importacao = servico_datasets.importar_exemplo()

    assert importacao.nome_arquivo == "pesquisa_saude.txt"
    assert importacao.metadados.n_linhas == 230


def test_resumo_e_pagina(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    pagina = servico_datasets.pagina(dataset_id, pagina=1, tamanho=2, versao="original")

    assert pagina.resumo.n_linhas == 4
    assert pagina.total_paginas == 2
    assert len(pagina.linhas) == 2


def test_alterar_tipo_atualiza_o_dataset(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    servico_datasets.alterar_tipo(dataset_id, "sexo", TipoVariavel.NOMINAL)

    assert servico_datasets.colunas(dataset_id)[1].tipo == TipoVariavel.NOMINAL


def test_coluna_inexistente(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    with pytest.raises(NaoEncontrado) as erro:
        servico_datasets.coluna_para_analise(dataset_id, "altura")

    assert erro.value.codigo == "COLUNA_NAO_ENCONTRADA"


def test_coluna_para_analise_entrega_numeros_ou_textos(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    peso = servico_datasets.coluna_para_analise(dataset_id, "peso")
    sexo = servico_datasets.coluna_para_analise(dataset_id, "sexo")

    assert peso.numeros is not None
    assert peso.numeros.dropna().tolist() == [58.2, 79.6, 63.0]
    assert sexo.numeros is None
    assert sexo.textos.tolist() == ["F", "M", "F", "M"]
    assert isinstance(sexo.textos, pd.Series)
