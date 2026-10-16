import numpy as np
import pytest

from app.dominios.detector import digitos


def test_resolucao_e_o_maior_numero_de_casas() -> None:
    assert digitos.resolucao(np.array([1.25, 3.5, 7.0])) == 2


def test_resolucao_de_inteiros_e_zero() -> None:
    assert digitos.resolucao(np.array([18.0, 40.0, 93.0])) == 0


def test_digitos_finais_na_resolucao_da_coluna() -> None:
    valores = np.array([1.25, 3.5, 7.0])

    assert digitos.digitos_finais(valores, 2).tolist() == [5, 0, 0]


def test_digitos_finais_ignoram_o_sinal_e_o_ruido_do_float() -> None:
    valores = np.array([-58.2, 0.1 + 0.2, 63.0])

    assert digitos.digitos_finais(valores, 1).tolist() == [2, 3, 0]


def test_primeiros_digitos() -> None:
    assert digitos.primeiros_digitos(np.array([0.0123, 456.0, 7.8])).tolist() == [1, 4, 7]


@pytest.mark.parametrize(
    ("valor", "digito"), [(0.3, 3), (1000.0, 1), (0.001, 1), (9.999, 9), (2.0, 2)]
)
def test_primeiro_digito_nas_potencias_de_10_e_decimais(valor: float, digito: int) -> None:
    assert digitos.primeiros_digitos(np.array([valor])).tolist() == [digito]


def test_primeiros_digitos_ignoram_zeros_e_o_sinal() -> None:
    assert digitos.primeiros_digitos(np.array([0.0, -35.0, 25.0])).tolist() == [3, 2]


def test_digito_final_variavel_se_aplica() -> None:
    valores = np.arange(18.0, 98.0)

    assert digitos.motivo_digito_final(valores, 50) is None


def test_digito_final_com_poucos_valores() -> None:
    motivo = digitos.motivo_digito_final(np.arange(30.0), 50)

    assert motivo == "precisa de 50 valores ou mais; a coluna tem 30"


def test_digito_final_constante_nao_se_aplica() -> None:
    motivo = digitos.motivo_digito_final(np.arange(10.0, 1010.0, 10.0), 50)

    assert motivo == "o último dígito é sempre o mesmo"


def test_valores_com_pouca_variacao_nao_tem_ultimo_digito_aleatorio() -> None:
    notas = np.tile(np.arange(0.0, 11.0), 10)

    motivo = digitos.motivo_digito_final(notas, 50)

    assert motivo == "os valores variam pouco para o último dígito ser aleatório"


def test_coluna_com_poucos_valores_diferentes_nao_tem_digito_testavel() -> None:
    descontos = np.tile([5.0, 10.0, 12.5, 15.0], 30)

    motivo = digitos.motivo_digito_final(descontos, 50)

    assert motivo == "a coluna tem só 4 valores diferentes"


def _chuva(media: float) -> np.ndarray:
    """Quantis de uma Exponencial na grade do pluviômetro (de 0,2 em 0,2 mm, sem zeros)."""
    quantis = -media * np.log(1 - (np.arange(1, 301) - 0.5) / 300)
    return np.round(0.2 * (np.floor(quantis / 0.2) + 1), 1)


@pytest.mark.parametrize("media", [1.5, 4.0])
def test_valores_pequenos_perto_do_passo_nao_tem_ultimo_digito_aleatorio(media: float) -> None:
    # Por hora, o 1º quartil é 0,6 mm; por dia, 1,2 mm: 3 e 6 passos do pluviômetro (D134).
    motivo = digitos.motivo_digito_final(_chuva(media), 50)

    assert motivo == "os valores são pequenos demais para o último dígito ser aleatório"


def test_passo_da_medida() -> None:
    assert digitos.passo_da_medida(np.array([0.2, 1.4, 3.0]), 1) == 2
    assert digitos.passo_da_medida(np.array([1.62, 1.7]), 2) == 2
    assert digitos.passo_da_medida(np.array([70.1, 70.4]), 1) == 1
