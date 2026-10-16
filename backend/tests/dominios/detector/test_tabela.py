import numpy as np
import pandas as pd

from app.compartilhado.tipos import TipoVariavel
from app.dominios.detector.tabela import coluna_detector, montar_tabela
from tests.dominios.detector.apoio import tabela_de

TIPOS = {
    "sexo": TipoVariavel.BINARIA,
    "idade": TipoVariavel.DISCRETA,
    "peso": TipoVariavel.CONTINUA,
}


def _dados() -> pd.DataFrame:
    return pd.DataFrame(
        {"sexo": ["F", "M", None, "F"], "idade": [30, 41, 25, None], "peso": [58.2, None, 70, 64.5]}
    )


def test_tabela_guarda_linhas_e_colunas_na_ordem() -> None:
    tabela = tabela_de(_dados(), TIPOS)

    assert tabela.n_linhas == 4
    assert tabela.linhas.tolist() == [1, 2, 3, 4]
    assert list(tabela.colunas) == ["sexo", "idade", "peso"]


def test_faltantes_viram_nan_e_none() -> None:
    tabela = tabela_de(_dados(), TIPOS)

    peso = tabela.colunas["peso"]
    assert peso.numeros is not None
    assert np.isnan(peso.numeros[1])
    assert tabela.colunas["sexo"].textos == ("F", "M", None, "F")
    assert tabela.colunas["sexo"].numeros is None


def test_numericas_sao_discretas_e_continuas() -> None:
    tabela = tabela_de(_dados(), TIPOS)

    assert [c.nome for c in tabela.numericas()] == ["idade", "peso"]
    assert [c.nome for c in tabela.do_tipo({TipoVariavel.CONTINUA})] == ["peso"]


def test_valores_validos_trazem_o_numero_da_linha() -> None:
    tabela = tabela_de(_dados(), TIPOS)

    linhas, valores = tabela.valores_validos(tabela.colunas["peso"])

    assert linhas.tolist() == [1, 3, 4]
    assert valores.tolist() == [58.2, 70.0, 64.5]


def test_valores_validos_de_coluna_qualitativa_sao_vazios() -> None:
    tabela = tabela_de(_dados(), TIPOS)

    linhas, valores = tabela.valores_validos(tabela.colunas["sexo"])

    assert len(linhas) == len(valores) == 0


def test_linhas_seguem_o_indice_do_dataset_depois_da_limpeza() -> None:
    indice = pd.Index([2, 5, 9])
    numeros = pd.Series([1.0, 2.0, 3.0], index=indice)
    coluna = coluna_detector("x", TipoVariavel.CONTINUA, numeros, numeros.astype(str))

    tabela = montar_tabela(indice, [coluna])

    assert tabela.valores_validos(coluna)[0].tolist() == [2, 5, 9]


def test_coluna_de_datas_guarda_as_datas_na_ordem_das_linhas() -> None:
    textos = pd.Series(["01/02/2026", None, "03/02/2026"], index=pd.RangeIndex(1, 4))
    datas = pd.Series(pd.to_datetime(["2026-02-01", "2026-02-03"]), index=[1, 3])

    coluna = coluna_detector("quando", TipoVariavel.DATA, None, textos, datas)

    assert coluna.datas is not None
    assert len(coluna.datas) == 3
    assert np.isnat(coluna.datas[1])
