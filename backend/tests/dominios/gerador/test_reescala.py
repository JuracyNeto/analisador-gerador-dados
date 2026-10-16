import numpy as np
import pytest

from app.dominios.gerador.reescala import arredondar, casas_decimais, limitar_faixa, reescalar


def test_reescalar_da_media_e_desvio_exatos() -> None:
    sorteados = np.random.default_rng(1).normal(0, 1, 300)

    valores = reescalar(sorteados, 70.3, 11.2)

    assert float(np.mean(valores)) == pytest.approx(70.3, rel=1e-12)
    assert float(np.std(valores, ddof=1)) == pytest.approx(11.2, rel=1e-12)


def test_reescalar_sem_variacao_repete_a_media() -> None:
    assert reescalar(np.array([3.0, 3.0, 3.0]), 10.0, 2.0).tolist() == [10.0, 10.0, 10.0]


@pytest.mark.parametrize(
    ("valores", "casas"),
    [([1.5, 2.25, 3.0], 2), ([1.0, 2.0], 0), ([58.2, 79.6], 1), ([0.123456789], 6)],
)
def test_casas_decimais(valores: list[float], casas: int) -> None:
    assert casas_decimais(np.array(valores)) == casas


def test_arredondar() -> None:
    assert arredondar(np.array([1.234, 5.678]), 1).tolist() == [1.2, 5.7]


def test_limitar_faixa_sorteia_de_novo_e_mantem_as_medidas_proximas() -> None:
    rng = np.random.default_rng(7)

    def sortear(quantidade: int) -> np.ndarray:
        return rng.normal(70, 11, quantidade)

    inicial = reescalar(sortear(500), 70.0, 11.0)
    valores, recortou = limitar_faixa(sortear, inicial, 40.0, 100.0, (70.0, 11.0))

    assert float(valores.min()) >= 40.0
    assert float(valores.max()) <= 100.0
    assert abs(float(np.mean(valores)) - 70.0) / 70.0 < 0.01
    assert abs(float(np.std(valores, ddof=1)) - 11.0) / 11.0 < 0.01
    assert recortou is False
