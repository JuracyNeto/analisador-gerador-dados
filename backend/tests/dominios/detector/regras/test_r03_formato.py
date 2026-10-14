import numpy as np
import pandas as pd

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r03_formato import RegraFormato
from tests.dominios.detector.apoio import tabela_de, tabela_numerica


def _decimais(n: int = 100) -> np.ndarray:
    """Valores sempre com casas decimais: 50,25 · 50,75 · 51,25…"""
    return 50 + np.arange(n) * 0.5 + 0.25


def _com_inteiros(posicoes: list[int] | np.ndarray) -> np.ndarray:
    valores = _decimais()
    valores[posicoes] = np.floor(valores[posicoes])
    return valores


def test_inteiros_juntos_no_meio_de_decimais_disparam_atencao() -> None:
    valores = _com_inteiros(np.arange(39, 49))

    resultado = RegraFormato().executar(tabela_numerica(valores, nome="altura"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R3"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Inteiros no meio de decimais em altura"
    assert aviso.resumo == (
        "Em altura, 90% dos valores têm casas decimais, "
        "mas 10 inteiros aparecem juntos (linhas 40–49)."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == tuple(range(40, 50))
    assert aviso.exemplo.texto.startswith("Linhas 40 a 49: 69, 70, 70")


def test_inteiros_em_posicoes_regulares_disparam() -> None:
    valores = _com_inteiros([5, 15, 25, 35, 45, 55])

    (aviso,) = RegraFormato().executar(tabela_numerica(valores, nome="altura")).avisos

    assert aviso.resumo == (
        "Em altura, 94% dos valores têm casas decimais, "
        "mas 6 inteiros aparecem a cada 10 linhas (linhas 6–56)."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (6, 16, 26, 36, 46, 56)


def test_inteiros_espalhados_ao_acaso_nao_disparam() -> None:
    valores = _com_inteiros([3, 17, 29, 52, 71, 88])

    resultado = RegraFormato().executar(tabela_numerica(valores))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_quatro_inteiros_seguidos_nao_bastam() -> None:
    assert RegraFormato().executar(tabela_numerica(_com_inteiros([40, 41, 42, 43]))).avisos == ()


def test_menos_de_80_porcento_de_decimais_nao_dispara() -> None:
    valores = _com_inteiros(np.arange(0, 30))

    assert RegraFormato().executar(tabela_numerica(valores)).avisos == ()


def test_sem_colunas_continuas_a_regra_nao_se_aplica() -> None:
    tabela = tabela_de(pd.DataFrame({"filhos": [0, 1, 2] * 20}), {"filhos": TipoVariavel.DISCRETA})

    resultado = RegraFormato().executar(tabela)

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.coluna is None
    assert nao_aplicada.motivo == "o arquivo não tem colunas contínuas"


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraFormato().executar(tabela_numerica(_decimais(20))).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 30 valores ou mais; a coluna tem 20"
