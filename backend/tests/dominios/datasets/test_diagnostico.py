import pandas as pd
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.classificacao import Limiares, classificar_tabela
from app.dominios.datasets.diagnostico import (
    Grafia,
    GrupoDuplicado,
    Limites,
    diagnosticar,
    faixa_da_coluna,
    faixa_iqr,
    grupos_de_grafias,
)
from app.dominios.datasets.modelos import TipoColuna

DADOS = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "cidade": [
            "Goiânia",
            "Goiania",
            "goiânia",
            "Anápolis",
            "Anapolis",
            None,
            "Goiânia",
            "Goiânia",
        ],
        "idade": [30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 230.0, 30.0],
        "nota": ["7", "8", "doze", "6", "7", "8", "9", "7"],
    },
    index=pd.RangeIndex(1, 9),
)


def _tipos(dados: pd.DataFrame) -> dict[str, TipoColuna]:
    return classificar_tabela(dados, ".", Limiares(numerico=0.8))


def test_faltantes_com_linhas_e_valores_sugeridos() -> None:
    diagnostico = diagnosticar(DADOS, _tipos(DADOS), ".", {})

    [cidade] = diagnostico.faltantes
    assert (cidade.coluna, cidade.n, cidade.linhas) == ("cidade", 1, (6,))
    assert cidade.sugeridos.moda == "Goiânia"
    assert cidade.sugeridos.media is None


def test_sugeridos_de_coluna_numerica() -> None:
    dados = pd.DataFrame({"peso": [10.0, 20.0, None, 30.0, 20.0]}, index=pd.RangeIndex(1, 6))

    [peso] = diagnosticar(dados, _tipos(dados), ".", {}).faltantes

    assert (peso.sugeridos.media, peso.sugeridos.mediana, peso.sugeridos.moda) == (20.0, 20.0, 20.0)


def test_duplicados_ignoram_identificador() -> None:
    dados = pd.DataFrame(
        {"id": [1, 2, 3, 4], "sexo": ["F", "M", "F", "F"], "peso": [58.2, 79.6, 58.2, 58.2]},
        index=pd.RangeIndex(1, 5),
    )

    diagnostico = diagnosticar(dados, _tipos(dados), ".", {})

    assert diagnostico.duplicados == (GrupoDuplicado(1, (3, 4)),)


def test_fora_de_faixa_pelo_iqr() -> None:
    [idade] = diagnosticar(DADOS, _tipos(DADOS), ".", {}).fora_de_faixa

    assert idade.origem == "iqr"
    assert [o.linha for o in idade.ocorrencias] == [7]
    assert idade.ocorrencias[0].valor == 230.0


def test_fora_de_faixa_pelos_limites_do_usuario() -> None:
    limites = {"idade": Limites(min=31, max=None)}

    [idade] = diagnosticar(DADOS, _tipos(DADOS), ".", limites).fora_de_faixa

    assert idade.origem == "usuario"
    assert idade.limite_inferior == 31
    assert [o.linha for o in idade.ocorrencias] == [1, 7, 8]


def test_limites_invertidos_sao_recusados() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        faixa_da_coluna(pd.Series([1.0, 2.0]), Limites(min=110, max=1))

    assert erro.value.codigo == "LIMITES_INVALIDOS"
    assert erro.value.mensagem == "O mínimo precisa ser menor que o máximo (1)."


def test_faixa_iqr_usa_as_cercas_de_tukey() -> None:
    assert faixa_iqr(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])) == (-1.0, 7.0)


def test_grupos_de_grafias_preferem_a_mais_frequente() -> None:
    serie = pd.Series(["Goiânia", "Goiania", "Goiânia", "goiânia", "Rio Verde"])

    [grupo] = grupos_de_grafias(serie)

    assert grupo.forma_preferida == "Goiânia"
    assert grupo.variacoes == (Grafia("Goiania", 1), Grafia("goiânia", 1))


def test_inconsistencias_por_coluna() -> None:
    [cidade] = diagnosticar(DADOS, _tipos(DADOS), ".", {}).inconsistencias

    assert cidade.coluna == "cidade"
    assert [g.forma_preferida for g in cidade.grupos] == ["Goiânia", "Anápolis"]


def test_tipo_misto_aponta_os_textos() -> None:
    [nota] = diagnosticar(DADOS, _tipos(DADOS), ".", {}).tipo_misto

    assert nota.coluna == "nota"
    assert [(o.linha, o.valor) for o in nota.ocorrencias] == [(3, "doze")]
