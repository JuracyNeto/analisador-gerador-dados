from datetime import date, datetime, time

import pandas as pd
import pytest

from app.compartilhado.datas import formatar_data, reconhecer_datas


@pytest.mark.parametrize(
    ("valores", "formato"),
    [
        (["07/10/2026", "8/10/2026", "31/12/2025"], "dd/mm/aaaa"),
        (["07-10-2026", "08.10.2026"], "dd/mm/aaaa"),
        (["10/27/2026", "10/28/2026", "1/2/2026"], "mm/dd/aaaa"),
        (["2026-10-07", "2026-10-08"], "aaaa-mm-dd"),
        (["07/10/2026 08:30", "2026-10-07T17:05:12"], "data_hora"),
        (["08:30", "17:05:12", "0:15"], "hora"),
    ],
)
def test_reconhece_o_formato(valores: list[str], formato: str) -> None:
    leitura = reconhecer_datas(pd.Series(valores))

    assert leitura is not None
    assert leitura.formato == formato
    assert leitura.proporcao == 1.0


def test_converte_os_valores_para_datas() -> None:
    leitura = reconhecer_datas(pd.Series(["07/10/2026", "2026-10-08"]))

    assert leitura is not None
    assert leitura.valores.iloc[0] == pd.Timestamp("2026-10-07")


def test_dia_vem_primeiro_quando_a_data_e_ambigua() -> None:
    leitura = reconhecer_datas(pd.Series(["01/02/2026", "03/04/2026"]))

    assert leitura is not None
    assert leitura.formato == "dd/mm/aaaa"
    assert leitura.valores.iloc[0] == pd.Timestamp("2026-02-01")


def test_mes_primeiro_quando_o_segundo_campo_passa_de_12() -> None:
    leitura = reconhecer_datas(pd.Series(["10/27/2026", "01/02/2026"]))

    assert leitura is not None
    assert leitura.valores.iloc[1] == pd.Timestamp("2026-01-02")


def test_datas_impossiveis_nao_contam() -> None:
    leitura = reconhecer_datas(pd.Series(["31/02/2026", "07/10/2026", "25:00"]))

    assert leitura is not None
    assert leitura.proporcao == pytest.approx(1 / 3)


def test_exemplo_e_o_primeiro_valor_reconhecido() -> None:
    leitura = reconhecer_datas(pd.Series(["sem data", "07/10/2026", "08/10/2026"]))

    assert leitura is not None
    assert leitura.exemplo == "07/10/2026"


def test_ignora_faltantes_na_proporcao() -> None:
    leitura = reconhecer_datas(pd.Series(["07/10/2026", None, "08/10/2026"]))

    assert leitura is not None
    assert leitura.proporcao == 1.0


@pytest.mark.parametrize(
    "valores",
    [
        ["1,62", "1,78"],
        ["20261007", "20261008"],
        ["Goiânia", "Anápolis"],
        ["13/14/2026", "07/10/2026"],
        ["12:3", "1:2:3"],
    ],
)
def test_nao_toma_outros_valores_por_data(valores: list[str]) -> None:
    leitura = reconhecer_datas(pd.Series(valores))

    assert leitura is None or leitura.proporcao < 0.9


def test_serie_vazia_nao_tem_datas() -> None:
    assert reconhecer_datas(pd.Series([None, None], dtype="object")) is None


def test_colunas_de_data_da_planilha() -> None:
    serie = pd.Series(pd.to_datetime(["2026-10-07", "2026-10-08", None]))

    leitura = reconhecer_datas(serie)

    assert leitura is not None
    assert (leitura.formato, leitura.proporcao, leitura.exemplo) == ("planilha", 1.0, "07/10/2026")


def test_horarios_da_planilha() -> None:
    leitura = reconhecer_datas(pd.Series([time(8, 30), time(17, 5), "?"]))

    assert leitura is not None
    assert leitura.formato == "hora"
    assert leitura.proporcao == pytest.approx(2 / 3)
    assert leitura.exemplo == "08:30"


@pytest.mark.parametrize(
    ("valor", "texto"),
    [
        (pd.Timestamp("2026-10-07"), "07/10/2026"),
        (pd.Timestamp("2026-10-07 08:30"), "07/10/2026 08:30"),
        (datetime(2026, 10, 7, 8, 30, 15), "07/10/2026 08:30:15"),
        (date(2026, 10, 7), "07/10/2026"),
        (time(8, 30), "08:30"),
        (time(8, 30, 5), "08:30:05"),
        (pd.Timestamp("1900-01-01 08:30"), "08:30"),
        ("07/10/2026", "07/10/2026"),
    ],
)
def test_formatar_data(valor: object, texto: str) -> None:
    assert formatar_data(valor) == texto


@pytest.mark.parametrize(
    ("valores", "formato"),
    [
        (["2026-10-07 08:30", "2026-10-08 17:05"], "data_hora"),
        (["2026-10-07", "2026-10-08 17:05"], "planilha"),
        (["1900-01-01 08:30", "1900-01-01 17:05"], "hora"),
    ],
)
def test_formato_das_datas_da_planilha(valores: list[str], formato: str) -> None:
    leitura = reconhecer_datas(pd.Series(pd.to_datetime(valores, format="ISO8601")))

    assert leitura is not None
    assert leitura.formato == formato


def test_datas_e_horarios_como_objetos_da_planilha() -> None:
    serie = pd.Series([date(2026, 10, 7), datetime(2026, 10, 8, 8, 30)], dtype="object")

    leitura = reconhecer_datas(serie)

    assert leitura is not None
    assert list(leitura.valores) == [pd.Timestamp("2026-10-07"), pd.Timestamp("2026-10-08 08:30")]
