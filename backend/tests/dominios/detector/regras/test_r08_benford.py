import numpy as np
import pytest
from scipy import stats

from app.compartilhado.tipos import Severidade
from app.dominios.detector.regras.r08_benford import RegraBenford
from tests.dominios.detector.apoio import tabela_numerica


def _uniformes() -> np.ndarray:
    """1º dígito uniforme (1 a 9) em quatro ordens de grandeza: 1,5 · 25 · 350 · 4.500…"""
    return np.array([(d + 0.5) * 10.0**k for k in range(4) for d in range(1, 10)] * 30)


def test_log_uniforme_segue_benford_e_nao_dispara() -> None:
    valores = np.round(10 ** np.random.default_rng(42).uniform(0, 4, 1000), 2)

    resultado = RegraBenford().executar(tabela_numerica(valores))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_primeiro_digito_uniforme_dispara_atencao() -> None:
    resultado = RegraBenford().executar(tabela_numerica(_uniformes(), nome="valor_venda"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R8"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Primeiros dígitos fora do padrão em valor_venda"
    assert aviso.grafico is not None
    assert aviso.grafico.posicao == "primeiro"
    assert aviso.grafico.digitos == tuple(range(1, 10))
    assert aviso.resumo.startswith(
        "Os primeiros dígitos de valor_venda não seguem o padrão natural "
        "(Lei de Benford): o 9 abre "
    )
    assert "o esperado seria cerca de 5%" in aviso.resumo
    assert aviso.detalhes.teste == "Qui-quadrado (gl = 8)"
    assert aviso.detalhes.valor.startswith("MAD = 0,0")
    assert aviso.exemplo is not None
    assert all(valor.startswith("9") for valor in aviso.exemplo.valores[:1])


def test_poucos_valores_muito_diferentes_nao_bastam_para_varias_ordens() -> None:
    """Pesos com dois erros de digitação (6,8 e 712): a faixa real é estreita."""
    valores = np.concatenate([np.linspace(45, 110, 225), [6.8, 712.0]])

    (nao_aplicada,) = RegraBenford().executar(tabela_numerica(valores)).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de valores que variem em várias ordens de grandeza"


def test_zeros_ficam_de_fora_e_nao_impedem_a_regra() -> None:
    valores = np.concatenate([_uniformes(), np.zeros(20)])

    assert len(RegraBenford().executar(tabela_numerica(valores)).avisos) == 1


@pytest.mark.parametrize(
    ("valores", "motivo"),
    [
        (
            np.arange(18.0, 91.0).repeat(3),
            "precisa de valores que variem em várias ordens de grandeza",
        ),
        (np.linspace(1, 1000, 48), "precisa de 100 valores maiores que zero; a coluna tem 48"),
        (np.linspace(-10, 1000, 200), "tem valores negativos"),
    ],
)
def test_nao_se_aplica(valores: np.ndarray, motivo: str) -> None:
    resultado = RegraBenford().executar(tabela_numerica(valores, nome="idade"))

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.motivo == motivo
    assert nao_aplicada.frase == f"Lei de Benford não verificada em idade: {motivo}."


def _chuva_por_hora(n: int = 500) -> np.ndarray:
    """Quantis da Gama(0,3; 9) no pluviômetro de 0,2 mm: metade das horas com 0,2 a 0,6 mm."""
    milimetros = stats.gamma.ppf((np.arange(1, n + 1) - 0.5) / n, 0.3, scale=9)
    return np.round(np.maximum(np.round(milimetros / 0.2) * 0.2, 0.2), 1)


def test_valores_perto_do_passo_do_instrumento_ficam_de_fora() -> None:
    # Abaixo de 2 mm, o pluviômetro de 0,2 mm decide o 1º dígito (0,2 · 0,4 · 0,6 · 0,8 · 1,2…):
    # com eles, o 2 abria 48% dos valores (D145).
    resultado = RegraBenford().executar(tabela_numerica(_chuva_por_hora(), nome="chuva"))

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.motivo == (
        "precisa de valores que variem em várias ordens de grandeza, fora os valores abaixo "
        "de 2 (10 vezes o passo de 0,2 do instrumento)"
    )


def test_poucos_valores_longe_do_passo_nao_se_aplica() -> None:
    milimetros = np.round(np.geomspace(2, 2000, 50) / 0.2) * 0.2
    valores = np.concatenate([np.full(80, 0.4), milimetros.round(1)])

    (nao_aplicada,) = RegraBenford().executar(tabela_numerica(valores)).nao_aplicadas

    assert nao_aplicada.motivo == (
        "precisa de 100 valores maiores que zero; a coluna tem 50, fora os valores abaixo "
        "de 2 (10 vezes o passo de 0,2 do instrumento)"
    )


def test_detalhes_dizem_quantos_valores_perto_do_passo_ficaram_de_fora() -> None:
    # Em _uniformes, o passo é 0,5: 1,5 · 2,5 · 3,5 · 4,5 (30 vezes cada) ficam de fora.
    (aviso,) = RegraBenford().executar(tabela_numerica(_uniformes())).avisos

    assert aviso.detalhes.medida == (
        "Frequência do primeiro dígito comparada à Lei de Benford, fora os 120 valores abaixo de 5"
    )
