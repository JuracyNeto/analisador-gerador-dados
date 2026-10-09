import pandas as pd
import pytest

from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.datasets.ajuste_tipo import (
    MOTIVO_MANUAL,
    MOTIVO_ORDEM_ALFABETICA,
    ajustar_tipo,
)
from app.dominios.datasets.classificacao import ColunaLida, Limiares, ler_coluna


def _coluna(valores: list[object]) -> ColunaLida:
    return ler_coluna("x", pd.Series(valores), ",", Limiares())


def test_tipo_manual_registra_origem_e_motivo() -> None:
    tipo = ajustar_tipo(_coluna([1, 2, 3]), TipoVariavel.DISCRETA, None)

    assert (tipo.tipo, tipo.origem, tipo.motivo) == (
        TipoVariavel.DISCRETA,
        OrigemTipo.MANUAL,
        MOTIVO_MANUAL,
    )


def test_texto_nao_pode_ser_numerico() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["a", "b"]), TipoVariavel.CONTINUA, None)

    assert erro.value.codigo == "TIPO_INCOMPATIVEL"
    assert erro.value.mensagem == "Esta coluna tem textos; não pode ser numérica."


def test_binaria_exige_dois_valores() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["a", "b", "c"]), TipoVariavel.BINARIA, None)

    assert "esta coluna tem 3" in erro.value.mensagem


def test_ordinal_com_ordem_informada() -> None:
    tipo = ajustar_tipo(_coluna(["b", "a", "c"]), TipoVariavel.ORDINAL, ["c", "a", "b", "z"])

    assert tipo.categorias_ordem == ("c", "a", "b")


def test_ordinal_com_ordem_incompleta_e_recusado() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["b", "a", "c"]), TipoVariavel.ORDINAL, ["a", "b"])

    assert erro.value.codigo == "CATEGORIAS_INCOMPLETAS"


def test_ordinal_sem_ordem_usa_a_escala_ou_a_ordem_alfabetica() -> None:
    escala = ajustar_tipo(_coluna(["bom", "ruim"]), TipoVariavel.ORDINAL, None)
    alfabetica = ajustar_tipo(_coluna(["c", "a", "b"]), TipoVariavel.ORDINAL, None)

    assert escala.categorias_ordem == ("ruim", "bom")
    assert alfabetica.categorias_ordem == ("a", "b", "c")
    assert alfabetica.motivo == MOTIVO_ORDEM_ALFABETICA


def test_numeros_podem_virar_ordinal_com_categorias_em_texto() -> None:
    tipo = ajustar_tipo(_coluna([3, 1, 2, 1]), TipoVariavel.ORDINAL, ["1", "2", "3"])

    assert tipo.categorias_ordem == ("1", "2", "3")
    assert tipo.contagens == {"1": 2, "3": 1, "2": 1}


DATAS = ["07/10/2026", "08/10/2026", "09/10/2026"]


def test_textos_sem_datas_nao_viram_data() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["Goiânia", "Anápolis"]), TipoVariavel.DATA, None)

    assert erro.value.codigo == "TIPO_INCOMPATIVEL"
    assert erro.value.mensagem == "Esta coluna não tem datas ou horários que dê para reconhecer."


def test_datas_podem_virar_nominal_e_voltar() -> None:
    nominal = ajustar_tipo(_coluna(DATAS), TipoVariavel.NOMINAL, None)
    data = ajustar_tipo(_coluna(DATAS), TipoVariavel.DATA, None)

    assert (nominal.tipo, data.tipo, data.origem) == (
        TipoVariavel.NOMINAL,
        TipoVariavel.DATA,
        OrigemTipo.MANUAL,
    )
    assert data.contagens == {}


def test_datas_nao_viram_numero() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(DATAS), TipoVariavel.CONTINUA, None)

    assert erro.value.mensagem == "Esta coluna tem textos; não pode ser numérica."
