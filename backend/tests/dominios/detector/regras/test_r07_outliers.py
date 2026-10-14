import numpy as np
import pandas as pd
from scipy import stats

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r07_outliers import RegraOutliers
from tests.dominios.detector.apoio import tabela_de, tabela_numerica


def _normal(n: int = 200) -> np.ndarray:
    """Quantis da Normal(70, 10): sem sorteio, só os 2 da ponta passam de 1,5·IQR."""
    return np.round(70 + 10 * stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n), 2)


def test_valores_muito_distantes_disparam_atencao() -> None:
    valores = np.concatenate([_normal(), [150.0, 155.0]])

    resultado = RegraOutliers().executar(tabela_numerica(valores, nome="peso"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R7"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.colunas == ("peso",)
    assert aviso.exemplo is not None
    assert {"150", "155"} <= set(aviso.exemplo.valores)
    assert aviso.exemplo.linhas[-2:] == (201, 202)
    assert aviso.titulo == "4 valores distantes dos demais em peso"
    assert "(ex.: 155)" in aviso.resumo
    assert aviso.detalhes.valor == "2 moderados e 2 extremos"


def test_so_moderados_disparam_informativo() -> None:
    resultado = RegraOutliers().executar(tabela_numerica(_normal(), nome="idade"))

    (aviso,) = resultado.avisos
    assert aviso.severidade == Severidade.INFO
    assert aviso.resumo.startswith("2 valores de idade estão muito longe dos demais (ex.: ")
    assert "; o limite usual seria " in aviso.resumo
    assert aviso.pode_ser_normal.startswith("…")


def test_um_valor_so_usa_o_singular() -> None:
    valores = np.concatenate([np.linspace(50, 90, 100), [150.0]])

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith("1 valor de x está muito longe dos demais (ex.: 150)")
    assert aviso.titulo == "1 valor distante dos demais em x"


def test_sem_valores_distantes_nao_dispara() -> None:
    resultado = RegraOutliers().executar(tabela_numerica(np.linspace(50, 90, 200)))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_coluna_constante_nao_se_aplica() -> None:
    resultado = RegraOutliers().executar(tabela_numerica([5.0] * 20))

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.motivo == "todos os valores são iguais"
    assert not resultado.verificada


def test_metade_central_igual_nao_se_aplica() -> None:
    valores = [0.0] * 30 + [1.0, 2.0, 3.0, 4.0, 50.0]

    (nao_aplicada,) = RegraOutliers().executar(tabela_numerica(valores)).nao_aplicadas

    assert nao_aplicada.motivo == "a metade central dos valores é toda igual"


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraOutliers().executar(tabela_numerica([1.0, 2.0, 90.0])).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 10 valores ou mais; a coluna tem 3"


def test_so_olha_colunas_numericas() -> None:
    tabela = tabela_de(
        pd.DataFrame({"cidade": ["a", "b"] * 10, "n": [1, 2] * 10}),
        {"cidade": TipoVariavel.NOMINAL, "n": TipoVariavel.DISCRETA},
    )

    resultado = RegraOutliers().executar(tabela)

    assert resultado.avisos == ()
    assert resultado.nao_aplicadas == ()


def test_sem_colunas_numericas_a_regra_nao_se_aplica_ao_arquivo() -> None:
    tabela = tabela_de(pd.DataFrame({"cidade": ["a", "b"]}), {"cidade": TipoVariavel.NOMINAL})

    (nao_aplicada,) = RegraOutliers().executar(tabela).nao_aplicadas

    assert nao_aplicada.frase == (
        "Valores distantes não verificada: o arquivo não tem colunas numéricas."
    )
