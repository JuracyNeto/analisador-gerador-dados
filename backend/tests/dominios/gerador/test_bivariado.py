import numpy as np
import pytest

from app.dominios.gerador.bivariado import ParametrosBivariado, gerar_pares, gerar_pares_exatos


def _r(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(x, y)[0, 1])


def test_ajuste_exato_bate_r_medias_e_desvios() -> None:
    parametros = ParametrosBivariado(50, 1.7, 70.0, 0.09, 11.0, 0.7)

    x, y = gerar_pares_exatos(parametros, np.random.default_rng(1))

    assert abs(_r(x, y) - 0.7) < 1e-9
    assert float(x.mean()) == pytest.approx(1.7, abs=1e-12)
    assert float(y.mean()) == pytest.approx(70.0, abs=1e-9)
    assert float(x.std(ddof=1)) == pytest.approx(0.09, rel=1e-12)
    assert float(y.std(ddof=1)) == pytest.approx(11.0, rel=1e-12)


def test_sem_ajuste_r_perto_do_alvo_com_amostra_grande() -> None:
    parametros = ParametrosBivariado(10_000, 0.0, 0.0, 1.0, 1.0, 0.7)

    x, y = gerar_pares(parametros, np.random.default_rng(2))

    assert abs(_r(x, y) - 0.7) < 0.03


@pytest.mark.parametrize("rho", [1.0, -1.0])
def test_correlacao_perfeita_vira_reta(rho: float) -> None:
    x, y = gerar_pares_exatos(ParametrosBivariado(20, 0, 0, 1, 2, rho), np.random.default_rng(3))

    assert _r(x, y) == pytest.approx(rho, abs=1e-12)


def test_rho_zero_com_ajuste_exato() -> None:
    x, y = gerar_pares_exatos(ParametrosBivariado(30, 0, 0, 1, 1, 0.0), np.random.default_rng(4))

    assert abs(_r(x, y)) < 1e-9


def test_mesma_semente_mesmos_pares() -> None:
    parametros = ParametrosBivariado(10, 0, 0, 1, 1, 0.5)

    primeiro = gerar_pares(parametros, np.random.default_rng(5))
    segundo = gerar_pares(parametros, np.random.default_rng(5))

    assert np.array_equal(primeiro[0], segundo[0])
    assert np.array_equal(primeiro[1], segundo[1])
