"""Releitura do arquivo guardado com outras opções (D88)."""

import pytest
from fastapi.testclient import TestClient

from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.core.erros import NaoEncontrado
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets

CONTEUDO = b"Pesquisa\n\nid;sexo;peso\n1;F;58,2\n2;M;79,6\n3;F;\n4;M;63,0\n"
SEM_CABECALHO = OpcoesLeitura(linha_cabecalho=0)


def _importar(servico: ServicoDatasets) -> str:
    return servico.importar(CONTEUDO, "dados.txt", OpcoesLeitura()).dataset_id


def test_reler_usa_o_arquivo_guardado_e_mantem_o_id(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    importacao = servico_datasets.reler(dataset_id, SEM_CABECALHO)

    assert importacao.dataset_id == dataset_id
    assert importacao.nome_arquivo == "dados.txt"
    assert importacao.metadados.linha_cabecalho == 0
    assert [c.coluna for c in servico_datasets.colunas(dataset_id)][:2] == ["col_1", "col_2"]


def test_resumo_traz_as_opcoes_escolhidas(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    servico_datasets.reler(dataset_id, SEM_CABECALHO)

    assert servico_datasets.resumo(dataset_id).opcoes_leitura == SEM_CABECALHO


def test_reler_desfaz_tipos_corrigidos(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)
    servico_datasets.alterar_tipo(dataset_id, "sexo", TipoVariavel.NOMINAL)
    assert servico_datasets.resumo(dataset_id).tem_ajustes

    servico_datasets.reler(dataset_id, OpcoesLeitura())

    assert servico_datasets.obter(dataset_id).tipos["sexo"].origem == OrigemTipo.AUTO
    assert not servico_datasets.resumo(dataset_id).tem_ajustes


def test_reler_o_exemplo(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id

    importacao = servico_datasets.reler(dataset_id, OpcoesLeitura(separador=","))

    assert importacao.metadados.motivos["separador"] == "Escolhido por você."


def test_reler_dataset_que_nao_existe(servico_datasets: ServicoDatasets) -> None:
    with pytest.raises(NaoEncontrado):
        servico_datasets.reler("nao-existe", OpcoesLeitura())


def test_rota_de_releitura(cliente: TestClient, servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    resposta = cliente.post(f"/api/datasets/{dataset_id}/leitura", json={"linha_cabecalho": 0})

    assert resposta.status_code == 200
    assert resposta.json()["dataset_id"] == dataset_id
    assert resposta.json()["metadados"]["linha_cabecalho"] == 0
    resumo = cliente.get(f"/api/datasets/{dataset_id}").json()["resumo"]
    assert resumo["opcoes_leitura"]["linha_cabecalho"] == 0
    assert resumo["tem_ajustes"] is False


def test_rota_de_releitura_recusa_linha_negativa(
    cliente: TestClient, servico_datasets: ServicoDatasets
) -> None:
    dataset_id = _importar(servico_datasets)

    resposta = cliente.post(f"/api/datasets/{dataset_id}/leitura", json={"linha_cabecalho": -1})

    assert resposta.status_code == 422
