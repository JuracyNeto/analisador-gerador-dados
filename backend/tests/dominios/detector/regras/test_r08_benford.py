import numpy as np
import pytest

from app.compartilhado.tipos import Severidade
from app.dominios.detector.regras.r08_benford import RegraBenford
from tests.dominios.detector.apoio import tabela_numerica


def _uniformes() -> np.ndarray:
    """Inteiros de 100 a 999 (1º dígito uniforme), com um 5 para cobrir duas ordens."""
    valores = np.arange(100.0, 1000.0)
    valores[0] = 5.0
    return valores


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
    assert aviso.resumo.startswith(
        "Os primeiros dígitos de valor_venda não seguem o padrão natural "
        "(Lei de Benford): o 9 abre "
    )
    assert "o esperado seria cerca de 5%" in aviso.resumo
    assert aviso.detalhes.teste == "Qui-quadrado (gl = 8)"
    assert aviso.detalhes.valor.startswith("MAD = 0,0")
    assert aviso.exemplo is not None
    assert all(valor.startswith("9") for valor in aviso.exemplo.valores[:1])


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
