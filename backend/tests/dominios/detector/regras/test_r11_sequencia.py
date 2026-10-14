import numpy as np

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r11_sequencia import RegraSequencia
from tests.dominios.detector.apoio import tabela_numerica


def _normal(n: int = 200, semente: int = 0) -> np.ndarray:
    return np.round(np.random.default_rng(semente).normal(70, 10, n), 2)


def test_sequencia_1_2_3_dispara_progressao_aritmetica() -> None:
    (aviso,) = RegraSequencia().executar(tabela_numerica(np.arange(1.0, 51.0))).avisos

    assert aviso.regra == "R11"
    assert aviso.nome_regra == "Sequência"
    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Ordem dos valores segue um padrão em x"
    assert aviso.resumo == (
        "A ordem dos valores de x segue um padrão (progressão aritmética nas linhas 1–50)."
    )
    assert aviso.detalhes.teste == "Poisson: progressões × acaso"


def test_progressao_no_meio_de_dados_aleatorios_dispara() -> None:
    valores = _normal()
    valores[49:55] = [70.0, 72.5, 75.0, 77.5, 80.0, 82.5]

    resultado = RegraSequencia().executar(tabela_numerica(valores, nome="peso"))

    (aviso,) = resultado.avisos
    assert "(progressão aritmética nas linhas 50–55)" in aviso.resumo
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (50, 51, 52, 53, 54, 55)
    assert aviso.exemplo.texto == "Linhas 50 a 55: 70; 72,5; 75; 77,5; 80; 82,5"


def test_valores_que_alternam_disparam_pelo_runs() -> None:
    sinais = np.where(np.arange(100) % 2 == 0, 1.0, -1.0)
    ruido = np.random.default_rng(1).normal(0, 2, 100)
    valores = np.round(50 + sinais * (10 + ruido), 2)

    resultado = RegraSequencia().executar(tabela_numerica(valores))

    (aviso,) = resultado.avisos
    assert aviso.resumo == (
        "A ordem dos valores de x segue um padrão "
        "(valores alternam acima e abaixo do meio com regularidade)."
    )
    assert aviso.detalhes.teste == "Runs de Wald-Wolfowitz"
    assert aviso.detalhes.p_valor is not None
    assert aviso.detalhes.p_valor < 0.01


def test_valores_parecidos_com_o_anterior_disparam_pela_autocorrelacao() -> None:
    passeio = np.round(100 + np.cumsum(np.random.default_rng(2).normal(0, 1, 200)), 2)

    (aviso,) = RegraSequencia().executar(tabela_numerica(passeio)).avisos

    assert "(cada valor é muito parecido com o anterior)" in aviso.resumo
    assert "ρ₁ = 0,88" in aviso.detalhes.valor


def test_metades_separadas_disparam_por_sequencias_longas() -> None:
    rng = np.random.default_rng(3)
    valores = np.round(np.concatenate([rng.normal(40, 6, 50), rng.normal(60, 6, 50)]), 2)

    (aviso,) = RegraSequencia().executar(tabela_numerica(valores)).avisos

    assert "(valores acima e abaixo do meio aparecem em sequências longas)" in aviso.resumo


def test_ordem_aleatoria_nao_dispara() -> None:
    resultado = RegraSequencia().executar(tabela_numerica(_normal()))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_progressao_curta_com_poucos_valores_possiveis_pode_ser_acaso() -> None:
    """Com notas de 0 a 5, uma sequência 0, 1, 2, 3, 4, 5 aparece sozinha em 3.000 linhas."""
    valores = np.random.default_rng(4).integers(0, 6, 3000).astype(float)
    valores[1000:1006] = np.arange(6.0)

    resultado = RegraSequencia().executar(tabela_numerica(valores, TipoVariavel.DISCRETA))

    assert resultado.avisos == ()


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraSequencia().executar(tabela_numerica(_normal(20))).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 30 valores ou mais; a coluna tem 20"


def test_coluna_constante_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraSequencia().executar(tabela_numerica([2.0] * 40)).nao_aplicadas

    assert nao_aplicada.motivo == "todos os valores são iguais"
