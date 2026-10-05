from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from app.dominios.datasets.tabela import celula, linhas_dados, paginar


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (np.int64(3), 3),
        (np.float64(1.5), 1.5),
        (float("nan"), None),
        (None, None),
        (pd.NA, None),
        ("Goiânia", "Goiânia"),
        (np.True_, True),
        (datetime(2026, 10, 3, 9, 30), "2026-10-03T09:30:00"),
    ],
)
def test_celula_vira_tipo_simples(valor: object, esperado: object) -> None:
    assert celula(valor) == esperado


def test_linhas_guardam_o_numero_original() -> None:
    dados = pd.DataFrame({"a": [1, 2, 3]}, index=pd.Index([1, 5, 9]))

    assert [linha.linha for linha in linhas_dados(dados)] == [1, 5, 9]


def test_paginar() -> None:
    dados = pd.DataFrame({"a": range(45)}, index=pd.RangeIndex(1, 46))

    pagina = paginar(dados, pagina=3, tamanho=20)

    assert pagina.total_paginas == 3
    assert [linha.linha for linha in pagina.linhas] == [41, 42, 43, 44, 45]
