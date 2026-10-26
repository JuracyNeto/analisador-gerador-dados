import numpy as np
import pandas as pd
from scipy import stats

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r07_outliers import RegraOutliers
from tests.dominios.detector.apoio import chuva, tabela_de, tabela_numerica


def _normal(n: int = 200) -> np.ndarray:
    """Quantis da Normal(70, 10): sem sorteio, só os 2 da ponta passam de 1,5·IQR."""
    return np.round(70 + 10 * stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n), 2)


def test_valores_muito_distantes_disparam_atencao() -> None:
    valores = np.concatenate([_normal(), [150.0, 155.0]])

    resultado = RegraOutliers().executar(tabela_numerica(valores, nome="peso"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R7"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.colunas == ("peso",)
    assert aviso.exemplo is not None
    assert {"150", "155"} <= set(aviso.exemplo.valores)
    assert aviso.exemplo.linhas[-2:] == (201, 202)
    assert aviso.titulo == "4 valores distantes dos demais em peso"
    assert "(ex.: 155)" in aviso.resumo
    assert aviso.detalhes.valor == "2 moderados e 2 extremos"


def test_so_moderados_disparam_informativo() -> None:
    resultado = RegraOutliers().executar(tabela_numerica(_normal(), nome="idade"))

    (aviso,) = resultado.avisos
    assert aviso.severidade == Severidade.INFO
    assert aviso.resumo.startswith("2 valores de idade estão muito longe dos demais (ex.: ")
    assert "; o limite usual seria " in aviso.resumo
    assert aviso.pode_ser_normal.startswith("…")


def test_z_acima_de_3_dentro_das_cercas_extremas_e_so_informativo() -> None:
    """Numa Normal de 1.000 valores, |z| > 3 é comum; extremo é só fora de 3·IQR (D128)."""
    valores = _normal(1000)

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores)).avisos

    assert np.abs((valores - valores.mean()) / valores.std(ddof=1)).max() > 3
    assert aviso.severidade == Severidade.INFO
    assert aviso.detalhes.valor.endswith("e 0 extremos")


def test_um_valor_so_usa_o_singular() -> None:
    valores = np.concatenate([np.linspace(50, 90, 100), [150.0]])

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith("1 valor de x está muito longe dos demais (ex.: 150)")
    assert aviso.titulo == "1 valor distante dos demais em x"


def test_sem_valores_distantes_nao_dispara() -> None:
    resultado = RegraOutliers().executar(tabela_numerica(np.linspace(50, 90, 200)))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_coluna_constante_nao_se_aplica() -> None:
    resultado = RegraOutliers().executar(tabela_numerica([5.0] * 20))

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.motivo == "todos os valores são iguais"
    assert not resultado.verificada


def test_metade_central_igual_nao_se_aplica() -> None:
    valores = [7.0] * 30 + [1.0, 2.0, 3.0, 4.0, 50.0]

    (nao_aplicada,) = RegraOutliers().executar(tabela_numerica(valores)).nao_aplicadas

    assert nao_aplicada.motivo == "a metade central dos valores é toda igual"


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraOutliers().executar(tabela_numerica([1.0, 2.0, 90.0])).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 10 valores ou mais; a coluna tem 3"


def test_so_olha_colunas_numericas() -> None:
    tabela = tabela_de(
        pd.DataFrame({"cidade": ["a", "b"] * 10, "n": [1, 2] * 10}),
        {"cidade": TipoVariavel.NOMINAL, "n": TipoVariavel.DISCRETA},
    )

    resultado = RegraOutliers().executar(tabela)

    assert resultado.avisos == ()
    assert resultado.nao_aplicadas == ()


def test_sem_colunas_numericas_a_regra_nao_se_aplica_ao_arquivo() -> None:
    tabela = tabela_de(pd.DataFrame({"cidade": ["a", "b"]}), {"cidade": TipoVariavel.NOMINAL})

    (nao_aplicada,) = RegraOutliers().executar(tabela).nao_aplicadas

    assert nao_aplicada.frase == (
        "Valores distantes não verificada: o arquivo não tem colunas numéricas."
    )


def _exponencial(n: int = 300) -> np.ndarray:
    """Quantis da Exponencial (média 10): cauda longa sem sorteio."""
    return np.round(-10 * np.log(1 - (np.arange(1, n + 1) - 0.5) / n), 2)


def test_cauda_longa_nao_vira_extremo() -> None:
    # Com Tukey, os 3 maiores (até 63,9) passavam de Q3 + 3·IQR (46,8); as cercas ajustadas à
    # assimetria alargam o lado da cauda (D136).
    resultado = RegraOutliers().executar(tabela_numerica(_exponencial(), nome="valor"))

    assert {aviso.severidade for aviso in resultado.avisos} <= {Severidade.INFO}


def test_erro_de_digitacao_numa_cauda_longa_continua_extremo() -> None:
    valores = _exponencial()
    valores[[50, 120]] = valores.max() * 10

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores, nome="valor")).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.detalhes.valor.endswith("2 extremos")


def test_detalhes_dizem_a_assimetria_usada_nas_cercas() -> None:
    valores = np.concatenate([_normal(), [150.0, 155.0]])

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores)).avisos

    assert aviso.detalhes.medida == (
        "Valores fora das cercas de Tukey ajustadas à assimetria ou com |z| > 3"
    )
    assert aviso.detalhes.formula is not None
    assert "MC" in aviso.detalhes.formula
    assert aviso.detalhes.formula.endswith("; a etapa Limpeza usa as cercas sem o ajuste")


def test_exemplo_marcado_so_pelo_z_cita_os_desvios_padrao() -> None:
    """Com a cauda longa, a cerca vai a 58,46; o 50 só passa de |z| > 3 (achado D-a do M4.3)."""
    valores = np.minimum(_exponencial(), 50.0)

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores, nome="valor")).avisos

    assert aviso.resumo == (
        "6 valores de valor estão muito longe dos demais "
        "(ex.: 50, a mais de 3 desvios padrão da média)."
    )


def test_exemplo_fora_da_cerca_alargada_diz_que_o_limite_foi_ajustado() -> None:
    """A etapa Limpeza mostra a cerca sem o ajuste (Q3 + 1,5·IQR); o resumo explica a diferença."""
    valores = _exponencial()
    valores[[50, 120]] = valores.max() * 10

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores, nome="valor")).avisos

    assert aviso.resumo == (
        "3 valores de valor estão muito longe dos demais (ex.: 639,7); "
        "o limite, ajustado à assimetria da coluna, seria 59,62."
    )


def test_o_que_fazer_aponta_acoes_que_existem() -> None:
    """A Limpeza não corrige valores (D76): corrige-se no arquivo, ou remove-se na Limpeza."""
    valores = np.concatenate([_normal(), [150.0]])

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores)).avisos

    assert aviso.o_que_fazer == (
        "Confira esses valores na fonte; se forem erros de digitação, corrija no arquivo e "
        "envie de novo, ou remova-os na etapa Limpeza."
    )


def test_com_muitos_zeros_as_cercas_saem_dos_valores_acima_de_zero() -> None:
    # Com 72% de zeros, Q1 = 0 e Q3 = 0,2: toda chuva acima de 0,8 mm virava extremo (D143).
    resultado = RegraOutliers().executar(tabela_numerica(chuva(360, 100), nome="chuva"))

    assert {aviso.severidade for aviso in resultado.avisos} <= {Severidade.INFO}


def test_erro_de_digitacao_com_muitos_zeros_continua_extremo() -> None:
    valores = chuva(360, 100)
    valores[np.argmax(valores)] *= 10

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores, nome="chuva")).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.detalhes.valor.endswith("e 1 extremo")
    assert aviso.detalhes.medida.endswith(", fora os 260 zeros")
    assert aviso.exemplo is not None
    assert "0" not in aviso.exemplo.valores


def test_um_zero_no_meio_de_valores_altos_continua_distante() -> None:
    valores = np.concatenate([_normal(), [0.0]])

    (aviso,) = RegraOutliers().executar(tabela_numerica(valores, nome="peso")).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.exemplo is not None
    assert "0" in aviso.exemplo.valores
    assert "zeros" not in aviso.detalhes.medida


def test_muitos_zeros_e_poucos_valores_acima_de_zero_nao_se_aplica() -> None:
    valores = [0.0] * 30 + [1.0, 2.0, 3.0, 4.0, 50.0]

    (nao_aplicada,) = RegraOutliers().executar(tabela_numerica(valores)).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 10 valores ou mais; a coluna tem 5, fora os zeros"
