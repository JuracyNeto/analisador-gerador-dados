import numpy as np
import pandas as pd
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.analise.bivariada import analisar_par, montar_par, prever_no_par
from app.dominios.analise.resultados_bivariada import Faixa, Par

PAR = Par("x", "y", np.array([1, 2, 3, 4, 5.0]), np.array([2, 4, 5, 4, 5.0]), n_descartados=2)


def test_monta_correlacao_e_regressao() -> None:
    bivariada = analisar_par(PAR)

    assert (bivariada.x, bivariada.y, bivariada.n, bivariada.n_descartados) == ("x", "y", 5, 2)
    assert (bivariada.forca, bivariada.sentido) == ("forte", "positiva")
    assert bivariada.regressao.b == pytest.approx(0.6)
    assert bivariada.faixa_x == Faixa(1.0, 5.0)
    assert bivariada.pearson.interpretacao == "Quando x aumenta, y tende a aumentar."


def test_interpretacoes_e_formulas() -> None:
    bivariada = analisar_par(PAR)

    assert bivariada.interpretacoes == (
        "Quando x aumenta, y tende a aumentar.",
        "A correlação não é significativa: pode ter aparecido por acaso (cerca de 1 em 8).",
        "60% da variação de y é explicada por x.",
    )
    assert [f.chave for f in bivariada.formulas] == [
        "pearson",
        "teste_t_correlacao",
        "spearman",
        "regressao",
        "r2",
        "erro_padrao_estimativa",
        "residuo",
    ]
    assert bivariada.figuras == ()


def _serie(valores: list[float | None]) -> pd.Series:
    return pd.Series(valores, index=pd.RangeIndex(1, len(valores) + 1), dtype="float64")


def test_montar_par_descarta_linhas_com_faltante() -> None:
    par = montar_par("x", "y", _serie([1, 2, None, 4, 5]), _serie([2, None, 3, 4, 5]))

    assert par.valores_x.tolist() == [1.0, 4.0, 5.0]
    assert par.valores_y.tolist() == [2.0, 4.0, 5.0]
    assert par.n_descartados == 2


@pytest.mark.parametrize(
    ("x", "y", "serie_y", "codigo"),
    [
        ("x", "x", [1, 2, 3], "COLUNAS_IGUAIS"),
        ("x", "y", [1, None, None], "POUCOS_PARES"),
        ("x", "y", [7, 7, 7], "SEM_VARIACAO"),
    ],
)
def test_montar_par_recusa(x: str, y: str, serie_y: list[float | None], codigo: str) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        montar_par(x, y, _serie([1, 2, 3]), _serie(serie_y))

    assert erro.value.codigo == codigo


def test_prever_no_par() -> None:
    previsao = prever_no_par(PAR, 8.0)

    assert previsao.y_previsto == pytest.approx(2.2 + 0.6 * 8)
    assert previsao.extrapolacao
