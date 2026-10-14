import numpy as np

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r09_ultimo_digito import RegraUltimoDigito
from tests.dominios.detector.apoio import tabela_numerica


def _idades(finais: list[int]) -> np.ndarray:
    dezenas = 20 + 10 * (np.arange(len(finais)) % 6)
    return (dezenas + np.array(finais)).astype(float)


def test_um_digito_repetido_demais_dispara_atencao() -> None:
    outros = [d for _ in range(19) for d in range(1, 10)][:152]
    valores = _idades([0] * 48 + outros)

    resultado = RegraUltimoDigito().executar(
        tabela_numerica(valores, TipoVariavel.DISCRETA, "idade")
    )

    (aviso,) = resultado.avisos
    assert aviso.regra == "R9"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Último dígito repetido em idade"
    assert aviso.resumo == (
        "O último dígito de idade não está bem distribuído: "
        "o 0 aparece 24% das vezes (esperado 10%)."
    )
    assert aviso.detalhes.teste == "Qui-quadrado de uniformidade (gl = 9)"
    assert aviso.detalhes.p_valor is not None
    assert aviso.detalhes.p_valor < 0.01
    assert aviso.exemplo is not None
    assert set(aviso.exemplo.valores[:3]) <= {"20", "30", "40", "50", "60", "70"}


def test_ultimo_digito_uniforme_nao_dispara() -> None:
    resultado = RegraUltimoDigito().executar(tabela_numerica(np.arange(18.0, 218.0)))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_coluna_com_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraUltimoDigito().executar(tabela_numerica(np.arange(40.0))).nao_aplicadas

    assert nao_aplicada.regra == "R9"
    assert nao_aplicada.motivo == "precisa de 50 valores ou mais; a coluna tem 40"


def test_coluna_que_termina_sempre_igual_nao_se_aplica() -> None:
    valores = np.arange(10.0, 1010.0, 10.0)

    (nao_aplicada,) = RegraUltimoDigito().executar(tabela_numerica(valores)).nao_aplicadas

    assert nao_aplicada.motivo == "o último dígito é sempre o mesmo"
