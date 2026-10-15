import numpy as np
import pytest

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r04_redondos import RegraRedondos
from tests.dominios.detector.apoio import tabela_numerica

NAO_REDONDOS = (1, 2, 3, 4, 6, 7, 8, 9)


def _com_finais(finais: list[int]) -> np.ndarray:
    """Inteiros de 40 a 129 com o último dígito pedido em cada posição."""
    dezenas = 40 + 10 * (np.arange(len(finais)) % 9)
    return (dezenas + np.array(finais)).astype(float)


def _finais(zeros: int, cincos: int, n: int) -> list[int]:
    outros = [NAO_REDONDOS[i % len(NAO_REDONDOS)] for i in range(n - zeros - cincos)]
    return [0] * zeros + [5] * cincos + outros


def test_muitos_terminados_em_0_ou_5_disparam_atencao() -> None:
    valores = _com_finais(_finais(23, 23, 100))

    resultado = RegraRedondos().executar(tabela_numerica(valores, TipoVariavel.DISCRETA, "peso"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R4"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Muitos valores redondos em peso"
    assert aviso.resumo == (
        "46% dos valores terminam em 0 ou 5; em medições reais o esperado seria "
        "cerca de 20% (2,3× mais)."
    )
    assert aviso.pode_ser_normal == "…o instrumento só mede de 5 em 5."
    assert aviso.detalhes.teste == "Binomial unilateral"
    assert aviso.detalhes.p_valor is not None
    assert aviso.detalhes.p_valor < 1e-8
    assert aviso.detalhes.p_em_palavras == "chance de acontecer por acaso: menos de 1 em 1.000"
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas[0] == 1


def test_muitos_terminados_em_0_avisam_os_multiplos_de_10() -> None:
    valores = _com_finais(_finais(30, 0, 100))

    (aviso,) = RegraRedondos().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith("30% dos valores terminam em 0; em medições reais")
    assert "cerca de 10% (3,0× mais)" in aviso.resumo
    assert aviso.pode_ser_normal == "…o instrumento só mede de 10 em 10."


def test_resolucao_decimal_fala_do_passo_decimal() -> None:
    valores = _com_finais(_finais(23, 23, 100)) / 10

    (aviso,) = RegraRedondos().executar(tabela_numerica(valores)).avisos

    assert aviso.pode_ser_normal == "…o instrumento só mede de 0,5 em 0,5."


def test_ultimo_digito_uniforme_nao_dispara() -> None:
    resultado = RegraRedondos().executar(tabela_numerica(np.arange(18.0, 118.0)))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_excesso_pequeno_com_p_baixo_nao_dispara() -> None:
    """Com n grande, 25% de redondos dá p < 0,01, mas fica abaixo de 1,5× o esperado."""
    valores = _com_finais(_finais(625, 625, 5000))

    assert RegraRedondos().executar(tabela_numerica(valores)).avisos == ()


@pytest.mark.parametrize(
    ("valores", "motivo"),
    [
        (np.arange(1.0, 31.0), "precisa de 50 valores ou mais; a coluna tem 30"),
        (np.arange(10.0, 1010.0, 10.0), "o último dígito é sempre o mesmo"),
        (
            np.tile(np.arange(1.0, 12.0), 10),
            "os valores variam pouco para o último dígito ser aleatório",
        ),
    ],
)
def test_nao_se_aplica(valores: np.ndarray, motivo: str) -> None:
    (nao_aplicada,) = RegraRedondos().executar(tabela_numerica(valores, nome="nota")).nao_aplicadas

    assert nao_aplicada.motivo == motivo
    assert nao_aplicada.frase == f"Valores redondos não verificada em nota: {motivo}."


def test_zeros_nao_contam_como_valores_redondos() -> None:
    # Vento calmo: muitos 0,0 entre velocidades com o último dígito uniforme (D134).
    medidas = np.round(np.arange(0.1, 20.1, 0.1), 1)
    valores = np.concatenate([np.zeros(60), medidas])

    resultado = RegraRedondos().executar(tabela_numerica(valores, nome="vento"))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_coluna_com_poucos_valores_diferentes_nao_se_aplica() -> None:
    descontos = np.tile([0.0, 5.0, 10.0, 12.5, 15.0], 60)

    (nao_aplicada,) = RegraRedondos().executar(tabela_numerica(descontos)).nao_aplicadas

    assert nao_aplicada.motivo == "a coluna tem só 4 valores diferentes, fora os zeros"
