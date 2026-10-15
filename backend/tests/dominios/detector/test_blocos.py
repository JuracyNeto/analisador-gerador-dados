import time
from itertools import pairwise

import numpy as np
import pytest

from app.dominios.detector import blocos


def _valores(n: int = 200, semente: int = 0) -> np.ndarray:
    return np.random.default_rng(semente).normal(70, 10, n)


def _afastamento_por_laco(valores: np.ndarray, k: int) -> list[float]:
    """max(dᵤ, dₛ) de cada janela contra o restante, um por vez."""
    afastamentos = []
    for inicio in range(len(valores) - k + 1):
        janela = valores[inicio : inicio + k]
        resto = np.delete(valores, np.arange(inicio, inicio + k))
        desvio = resto.std(ddof=1)
        d_media = abs(janela.mean() - resto.mean()) / desvio
        afastamentos.append(max(d_media, abs(janela.std(ddof=1) - desvio) / desvio))
    return afastamentos


def test_afastamentos_do_resto_batem_com_um_laco_simples() -> None:
    valores = _valores()

    afastamentos = blocos.afastamentos_do_resto(np.vstack([valores, valores[::-1]]), 15)

    np.testing.assert_allclose(afastamentos[0], _afastamento_por_laco(valores, 15), rtol=1e-8)
    np.testing.assert_allclose(afastamentos[1], _afastamento_por_laco(valores[::-1], 15), rtol=1e-8)


def test_janela_com_a_media_e_o_desvio_do_resto_tem_afastamento_zero() -> None:
    resto = _valores(380)
    z = np.random.default_rng(5).normal(0, 1, 20)
    janela = resto.mean() + resto.std(ddof=1) * (z - z.mean()) / z.std(ddof=1)

    afastamentos = blocos.afastamentos_do_resto(np.concatenate([resto, janela])[np.newaxis], 20)

    assert afastamentos[0, -1] < 1e-9


def test_resto_sem_variacao_nao_vira_a_melhor_janela() -> None:
    """Com o resto constante, s_resto = 0: a janela fica infinitamente longe (sem NaN)."""
    valores = np.zeros(42)
    valores[20:22] = (1.0, 2.0)

    afastamentos = blocos.afastamentos_do_resto(valores[np.newaxis], 10)

    assert not np.isnan(afastamentos).any()
    assert np.isinf(afastamentos[0, 12:21]).all()
    assert np.isfinite(afastamentos[0, :12]).all()


def test_embaralhados_vem_em_lotes_com_os_mesmos_valores() -> None:
    valores = _valores(50)
    rng = np.random.default_rng(1)

    lotes = list(blocos.embaralhados(valores, 30, rng, limite_elementos=500))

    assert [len(lote) for lote in lotes] == [10, 10, 10]
    for lote in lotes:
        np.testing.assert_allclose(np.sort(lote, axis=1), np.tile(np.sort(valores), (10, 1)))


def test_mesma_semente_mesmos_embaralhamentos() -> None:
    valores = _valores(40)

    primeiro = next(blocos.embaralhados(valores, 5, np.random.default_rng(7)))
    segundo = next(blocos.embaralhados(valores, 5, np.random.default_rng(7)))

    np.testing.assert_array_equal(primeiro, segundo)


@pytest.mark.parametrize(
    ("n", "tamanhos"), [(120, [24] * 5), (62, [13, 13, 12, 12, 12]), (60, [12] * 5)]
)
def test_dividir_em_cinco_blocos_seguidos(n: int, tamanhos: list[int]) -> None:
    partes = blocos.dividir_em_blocos(n)

    assert [p.stop - p.start for p in partes] == tamanhos
    assert partes[0].start == 0
    assert partes[-1].stop == n
    assert all(a.stop == b.start for a, b in pairwise(partes))


def test_mil_embaralhamentos_de_dez_mil_valores_sao_rapidos() -> None:
    valores = _valores(10_000)
    rng = np.random.default_rng(0)

    inicio = time.perf_counter()
    for lote in blocos.embaralhados(valores, 1_000, rng):
        blocos.afastamentos_do_resto(lote, 500).min(axis=1)

    assert time.perf_counter() - inicio < 3.0
