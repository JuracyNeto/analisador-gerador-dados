import numpy as np
import pytest

from app.dominios.analise.bivariada import analisar_par
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
