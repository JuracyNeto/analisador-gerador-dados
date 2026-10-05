import numpy as np
import pytest

from app.dominios.analise.posicao import calcular_posicao, posicao_percentil

UM_A_DEZ = [float(i) for i in range(1, 11)]


def test_posicao_percentil_conta_metade_dos_iguais() -> None:
    assert posicao_percentil(np.array(UM_A_DEZ), 6.0) == 55.0


def test_valor_no_terceiro_quartil() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 6.0, "quartil")

    assert (posicao.regiao, posicao.indice) == ("3º quartil", 3)
    assert (posicao.limite_inferior, posicao.limite_superior) == (5.5, 7.75)
    assert posicao.frase == (
        "O valor 6 está no 3º quartil (entre Q2 = 5,5 e Q3 = 7,75). "
        "Cerca de 55% dos dados são menores que ele."
    )
    assert [m.rotulo for m in posicao.marcas] == ["Q1", "Q2", "Q3"]
    assert (posicao.minimo, posicao.maximo) == (1.0, 10.0)


def test_valor_igual_a_q1_fica_no_primeiro_quartil() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 3.25, "quartil")

    assert posicao.indice == 1
    assert "(até Q1 = 3,25)" in posicao.frase


def test_valor_abaixo_do_minimo_avisa() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 0.0, "quartil")

    assert posicao.fora_da_faixa == "abaixo"
    assert posicao.frase.endswith("O valor está abaixo do menor dado observado (1).")


def test_decil_acima_do_ultimo() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 10.0, "decil")

    assert posicao.regiao == "10º decil"
    assert "(acima de D9 = 9,1)" in posicao.frase
    assert posicao.fora_da_faixa is None


def test_percentil_usa_a_posicao_percentil_e_9_marcas() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 6.0, "percentil")

    assert (posicao.regiao, posicao.indice) == ("percentil 55", 55)
    assert len(posicao.marcas) == 9
    assert posicao.limite_inferior == pytest.approx(5.86)
