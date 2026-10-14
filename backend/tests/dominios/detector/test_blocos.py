import time
from itertools import pairwise

import numpy as np
import pytest

from app.dominios.detector import blocos


def _valores(n: int = 200, semente: int = 0) -> np.ndarray:
    return np.random.default_rng(semente).normal(70, 10, n)


def test_janelas_batem_com_um_laco_simples() -> None:
    valores = _valores()

    medias, desvios = blocos.janelas(valores, 15)

    esperadas = [valores[i : i + 15].mean() for i in range(len(valores) - 14)]
    desvios_esperados = [valores[i : i + 15].std(ddof=1) for i in range(len(valores) - 14)]
    np.testing.assert_allclose(medias, esperadas, rtol=1e-10)
    np.testing.assert_allclose(desvios, desvios_esperados, rtol=1e-8)


def test_janelas_de_valores_iguais_tem_desvio_zero() -> None:
    _, desvios = blocos.janelas(np.full(30, 1.7), 10)

    np.testing.assert_allclose(desvios, 0.0, atol=1e-12)


def test_afastamento_e_o_maior_entre_media_e_desvio() -> None:
    afastamento = blocos.afastamento(np.array([71.0, 70.0]), np.array([10.0, 12.0]), 70.0, 10.0)

    np.testing.assert_allclose(afastamento, [0.1, 0.2])


def test_melhor_janela_de_cada_linha_da_matriz() -> None:
    valores = _valores()
    media, desvio = valores.mean(), valores.std(ddof=1)
    medias, desvios = blocos.janelas(valores, 10)

    melhores = blocos.menor_afastamento(np.vstack([valores, valores[::-1]]), 10, media, desvio)

    esperado = blocos.afastamento(medias, desvios, media, desvio).min()
    np.testing.assert_allclose(melhores, [esperado, esperado])


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
    media, desvio = valores.mean(), valores.std(ddof=1)
    rng = np.random.default_rng(0)

    inicio = time.perf_counter()
    for lote in blocos.embaralhados(valores, 1_000, rng):
        blocos.menor_afastamento(lote, 500, media, desvio)

    assert time.perf_counter() - inicio < 3.0
