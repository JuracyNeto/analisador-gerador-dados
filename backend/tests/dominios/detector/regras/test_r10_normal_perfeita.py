from dataclasses import replace

import numpy as np
from scipy import stats

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r10_normal_perfeita import RegraNormalPerfeita
from app.dominios.detector.tabela import TabelaDetector
from tests.dominios.detector.apoio import tabela_numerica


def _quantis(n: int = 1000) -> np.ndarray:
    """Valores tirados direto da curva Normal(70, 10), embaralhados: perfeitos demais."""
    valores = 70 + 10 * stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    return np.random.default_rng(0).permutation(np.round(valores, 2))


def test_quantis_da_normal_disparam_informativo() -> None:
    resultado = RegraNormalPerfeita().executar(tabela_numerica(_quantis(), nome="cintura_cm"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R10"
    assert aviso.nome_regra == "Normal perfeita demais"
    assert aviso.severidade == Severidade.INFO
    assert aviso.colunas == ("cintura_cm",)
    assert aviso.titulo == "Curva Normal perfeita demais em cintura_cm"
    assert aviso.resumo.startswith(
        "cintura_cm parece uma curva Normal perfeita demais (assimetria "
    )
    assert aviso.exemplo is None
    assert aviso.resumo.endswith("(assimetria 0,000, curtose −0,022).")
    assert aviso.detalhes.teste == "Shapiro-Wilk"
    assert aviso.detalhes.p_valor is not None
    assert aviso.detalhes.p_valor > 0.99
    assert aviso.detalhes.p_em_palavras == (
        "chance de dados Normais de verdade ficarem tão perto da curva: menos de 1 em 1.000"
    )


def test_normal_sorteada_nao_dispara() -> None:
    valores = np.round(np.random.default_rng(3).normal(70, 10, 1000), 2)

    resultado = RegraNormalPerfeita().executar(tabela_numerica(valores))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_so_continuas_sao_examinadas() -> None:
    resultado = RegraNormalPerfeita().executar(
        tabela_numerica(np.round(_quantis()), TipoVariavel.DISCRETA)
    )

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.motivo == "o arquivo não tem colunas contínuas"


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraNormalPerfeita().executar(tabela_numerica(_quantis(150))).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 200 valores ou mais; a coluna tem 150"


def test_coluna_constante_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraNormalPerfeita().executar(tabela_numerica([1.5] * 250)).nao_aplicadas

    assert nao_aplicada.motivo == "todos os valores são iguais"


def test_coluna_sem_forma_calculada_nao_dispara() -> None:
    tabela = tabela_numerica(_quantis())
    coluna = tabela.colunas["x"]
    sem_forma = TabelaDetector(tabela.n_linhas, tabela.linhas, {"x": replace(coluna, forma=None)})

    resultado = RegraNormalPerfeita().executar(sem_forma)

    assert resultado.avisos == ()
    assert resultado.verificada
