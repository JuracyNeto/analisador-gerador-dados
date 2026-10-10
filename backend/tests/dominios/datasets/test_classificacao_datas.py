import io
from datetime import time

import pandas as pd
import pytest
from openpyxl import Workbook

from app.compartilhado.tipos import TipoVariavel
from app.dominios.datasets.classificacao import Classificacao, Limiares, classificar, ler_coluna
from app.dominios.datasets.modelos import OpcoesLeitura
from app.dominios.datasets.servico import ServicoDatasets


def _classificar(nome: str, valores: list[object]) -> Classificacao:
    return classificar(ler_coluna(nome, pd.Series(valores), ",", Limiares()))


def _csv_de_datas() -> bytes:
    """O CSV usado em 08/10/2026 para mostrar o problema (datas viravam nominal/identificador)."""
    linhas = ["id;data;hora;data_hora;dia"]
    for i in range(40):
        dia = (i % 28) + 1
        linhas.append(
            f"{i};{dia:02d}/10/2026;{8 + i % 10:02d}:{(i * 7) % 60:02d};"
            f"2026-10-{dia:02d} 08:{i % 60:02d};{['seg', 'ter', 'qua'][i % 3]}"
        )
    return "\n".join(linhas).encode()


@pytest.mark.parametrize(
    ("valores", "motivo"),
    [
        (["07/10/2026", "08/10/2026"], "Datas no formato DD/MM/AAAA (ex.: 07/10/2026)."),
        (["10/27/2026", "10/28/2026"], "Datas no formato MM/DD/AAAA (ex.: 10/27/2026)."),
        (["2026-10-07", "2026-10-08"], "Datas no formato AAAA-MM-DD (ex.: 2026-10-07)."),
        (["07/10/2026 08:30", "07/10/2026 09:00"], "Datas com horário (ex.: 07/10/2026 08:30)."),
        (["08:30", "17:05"], "Horários (ex.: 08:30)."),
        ([time(8, 30), time(9, 0)], "Horários (ex.: 08:30)."),
    ],
)
def test_datas_e_horarios_viram_tipo_data(valores: list[object], motivo: str) -> None:
    resultado = _classificar("quando", valores)

    assert (resultado.tipo, resultado.motivo) == (TipoVariavel.DATA, motivo)


def test_datas_unicas_nao_viram_identificador() -> None:
    valores = [f"{dia:02d}/10/2026" for dia in range(1, 29)]

    assert _classificar("quando", valores).tipo == TipoVariavel.DATA


def test_menos_de_90_por_cento_de_datas_nao_e_data() -> None:
    valores = [f"{dia % 5 + 1:02d}/10/2026" for dia in range(17)] + ["a", "b", "c"]

    assert _classificar("quando", valores).tipo == TipoVariavel.NOMINAL


def test_limiar_de_data_vem_da_configuracao() -> None:
    valores = pd.Series(["07/10/2026", "08/10/2026", "x"])

    coluna = ler_coluna("quando", valores, ",", Limiares(data=0.6))

    assert classificar(coluna).tipo == TipoVariavel.DATA


def test_numeros_nunca_viram_data() -> None:
    assert _classificar("codigo_dia", [20261007, 20261008]).tipo != TipoVariavel.DATA


def test_csv_com_datas(servico_datasets: ServicoDatasets) -> None:
    importacao = servico_datasets.importar(_csv_de_datas(), "datas.csv", OpcoesLeitura())

    tipos = {c.coluna: c for c in importacao.colunas}
    assert {nome: tipos[nome].tipo for nome in ("data", "hora", "data_hora", "dia")} == {
        "data": TipoVariavel.DATA,
        "hora": TipoVariavel.DATA,
        "data_hora": TipoVariavel.DATA,
        "dia": TipoVariavel.NOMINAL,
    }
    assert tipos["hora"].motivo == "Horários (ex.: 08:00)."
    assert tipos["data"].contagens == {}


def test_planilha_com_coluna_de_datas(servico_datasets: ServicoDatasets) -> None:
    buffer = io.BytesIO()
    tabela = pd.DataFrame(
        {
            "quando": [pd.Timestamp("2026-10-07"), pd.Timestamp("2026-10-08 08:30")],
            "valor": [1.5, 2.5],
        }
    )
    with pd.ExcelWriter(buffer, engine="openpyxl") as planilha:
        tabela.to_excel(planilha, index=False)

    importacao = servico_datasets.importar(buffer.getvalue(), "datas.xlsx", OpcoesLeitura())

    quando = next(c for c in importacao.colunas if c.coluna == "quando")
    assert quando.tipo == TipoVariavel.DATA
    assert quando.motivo == "Datas da planilha (ex.: 07/10/2026)."
    assert quando.exemplos == ("07/10/2026", "08/10/2026 08:30")
    assert importacao.previa[0].valores["quando"] == "07/10/2026"


def test_exemplos_tem_os_mesmos_tipos(servico_datasets: ServicoDatasets) -> None:
    importacao = servico_datasets.importar_exemplo()

    assert TipoVariavel.DATA not in {c.tipo for c in importacao.colunas}


def test_horario_da_planilha_corrigido_para_nominal_fica_em_pt_br(
    servico_datasets: ServicoDatasets,
) -> None:
    # O to_excel do pandas grava horários como texto; o openpyxl grava células de hora.
    livro = Workbook()
    for linha in (["hora", "valor"], [time(8, 0), 1], [time(8, 37), 2], [time(9, 14), 3]):
        livro.active.append(linha)
    buffer = io.BytesIO()
    livro.save(buffer)
    dataset_id = servico_datasets.importar(
        buffer.getvalue(), "horas.xlsx", OpcoesLeitura()
    ).dataset_id

    hora = servico_datasets.alterar_tipo(dataset_id, "hora", TipoVariavel.NOMINAL)

    assert hora.exemplos == ("08:00", "08:37", "09:14")
