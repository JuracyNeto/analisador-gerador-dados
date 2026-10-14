"""Controle de falsos positivos (spec 12, spec 17): cada regra, exceto a R7, dispara em < 5%.

100 amostras Normal(50, 10) e 100 Exponenciais (média 10) por família, n = 500, arredondadas a
2 casas como medições reais (sem isso R4 e R9 nem se aplicam), geradas por `default_rng(1000 + i)`.
As regras de coluna rodam na amostra sozinha, como na spec. R2, R5 e R6 precisam de duas colunas
e de uma data: rodam numa tabela com datas diárias, a amostra e uma 2ª amostra da mesma família.
"""

from collections import Counter
from collections.abc import Callable
from functools import cache

import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.detector.registro import REGRAS
from app.dominios.detector.tabela import TabelaDetector
from tests.dominios.detector.apoio import tabela_de

AMOSTRAS = 100
N = 500
LIMITE = 0.05
SEMENTE_BASE = 1000
REGRAS_DE_TABELA = frozenset({"R2", "R5", "R6"})
FAMILIAS: dict[str, Callable[[np.random.Generator], np.ndarray]] = {
    "normal": lambda rng: rng.normal(50, 10, N),
    "exponencial": lambda rng: rng.exponential(10, N),
}
TIPOS = {"data": TipoVariavel.DATA, "x": TipoVariavel.CONTINUA, "y": TipoVariavel.CONTINUA}
INFORMATIVA = "R7"


def _tabelas(familia: str, i: int) -> tuple[TabelaDetector, TabelaDetector]:
    """(só a amostra, data + amostra + 2ª amostra)."""
    rng = np.random.default_rng(SEMENTE_BASE + i)
    x, y = (np.round(FAMILIAS[familia](rng), 2) for _ in range(2))
    datas = pd.date_range("2025-01-01", periods=N, freq="D")
    so_x = tabela_de(pd.DataFrame({"x": x}), {"x": TipoVariavel.CONTINUA})
    return so_x, tabela_de(pd.DataFrame({"data": datas, "x": x, "y": y}), TIPOS)


@cache
def taxas(familia: str) -> dict[str, float]:
    """Fração das amostras em que cada regra deu pelo menos um aviso."""
    disparos: Counter[str] = Counter()
    for i in range(AMOSTRAS):
        so_x, completa = _tabelas(familia, i)
        for regra in REGRAS:
            tabela = completa if regra.codigo in REGRAS_DE_TABELA else so_x
            disparos[regra.codigo] += bool(regra.executar(tabela).avisos)
    return {regra.codigo: disparos[regra.codigo] / AMOSTRAS for regra in REGRAS}


@pytest.mark.parametrize("familia", FAMILIAS)
@pytest.mark.parametrize("codigo", [r.codigo for r in REGRAS if r.codigo != INFORMATIVA])
def test_regra_dispara_em_menos_de_5_porcento(familia: str, codigo: str) -> None:
    taxa = taxas(familia)[codigo]

    assert taxa < LIMITE, f"{codigo} disparou em {taxa:.0%} das amostras {familia}"


@pytest.mark.parametrize("familia", FAMILIAS)
def test_as_regras_se_aplicam_as_amostras(familia: str) -> None:
    """O teste mede algo: as regras verificam as amostras (Benford só nas exponenciais)."""
    so_x, completa = _tabelas(familia, 0)

    verificadas = {
        regra.codigo
        for regra in REGRAS
        if regra.executar(completa if regra.codigo in REGRAS_DE_TABELA else so_x).verificada
    }

    esperadas = {f"R{i}" for i in range(1, 12)} - ({"R8"} if familia == "normal" else set())
    assert verificadas == esperadas
