from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.dominios.datasets.servico import AcaoLimpeza, Limites, ServicoDatasets


def test_diagnostico_do_exemplo_tem_os_problemas_plantados(
    servico_datasets: ServicoDatasets,
) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    limites = {"altura_m": Limites(1.2, 2.2), "idade": Limites(1, 110), "peso_kg": Limites(30, 200)}

    diagnostico = servico_datasets.diagnosticar(dataset_id, limites)

    assert sum(f.n for f in diagnostico.faltantes) == 7
    assert [(d.linha_original, d.copias) for d in diagnostico.duplicados] == [(44, (45, 46, 47))]
    assert sum(len(f.ocorrencias) for f in diagnostico.fora_de_faixa) == 5
    assert [len(i.grupos) for i in diagnostico.inconsistencias] == [2]


def test_limpar_atualiza_atual_log_e_tipos(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id

    resultado = servico_datasets.limpar(
        dataset_id,
        [
            AcaoLimpeza("duplicados", "remover"),
            AcaoLimpeza("inconsistencia", "unificar", "cidade"),
        ],
    )

    assert (resultado.n_linhas, resultado.n_linhas_original) == (227, 230)
    assert [e.frase for e in resultado.log] == [
        "Unificamos 11 grafias de cidade.",
        "Removemos 3 linhas duplicadas.",
    ]
    cidade = next(c for c in resultado.colunas if c.coluna == "cidade")
    assert cidade.motivo == "São categorias sem ordem natural (7 categorias)."
    assert len(servico_datasets.obter(dataset_id).original) == 230


def test_log_acumula_entre_limpezas(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id

    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])
    resultado = servico_datasets.limpar(
        dataset_id, [AcaoLimpeza("faltantes", "preencher_moda", "cidade")]
    )

    assert len(resultado.log) == 2
    assert len(servico_datasets.resumo(dataset_id).log_limpeza) == 2


def test_tipo_manual_e_mantido_depois_da_limpeza(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.alterar_tipo(dataset_id, "idade", TipoVariavel.DISCRETA)

    resultado = servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])

    idade = next(c for c in resultado.colunas if c.coluna == "idade")
    assert (idade.tipo, idade.origem) == (TipoVariavel.DISCRETA, OrigemTipo.MANUAL)


def test_desfazer_tudo_volta_ao_original(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])

    resultado = servico_datasets.desfazer_limpeza(dataset_id)

    assert (resultado.n_linhas, resultado.log) == (230, ())
    dataset = servico_datasets.obter(dataset_id)
    assert dataset.atual is not dataset.original
