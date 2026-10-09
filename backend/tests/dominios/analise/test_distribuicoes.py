import numpy as np
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.analise.distribuicoes import ajuste_bernoulli, ajuste_binomial, ajuste_normal
from app.dominios.analise.frequencias import tabela_frequencia
from tests.dominios.analise.conftest import CriarAmostra


def _amostras() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Mesma sequência do script de referência (scipy 1.18, semente 42)."""
    rng = np.random.default_rng(42)
    normal, exponencial = rng.normal(70, 11, 227), rng.exponential(10, 227)
    return normal, exponencial, rng.binomial(10, 0.3, 300).astype("float64")


NORMAL, EXPONENCIAL, BINOMIAL = _amostras()  # BINOMIAL: média 2,99 e máximo 8


def test_amostra_normal_e_compativel() -> None:
    ajuste = ajuste_normal(NORMAL, classes=None)

    assert ajuste.aplicavel
    assert ajuste.teste is not None
    assert ajuste.teste.nome == "Shapiro-Wilk"
    assert ajuste.teste.p_valor == pytest.approx(0.39896, rel=1e-3)
    assert ajuste.teste.compativel
    assert ajuste.frase == "Os dados são compatíveis com a distribuição Normal."
    assert [p.simbolo for p in ajuste.parametros] == ["μ̂", "σ̂"]
    assert (ajuste.calculo or "").startswith("Shapiro-Wilk: W = 0,993")
    assert ajuste.formula == "normal"


def test_amostra_exponencial_se_afasta() -> None:
    ajuste = ajuste_normal(EXPONENCIAL, classes=None)

    assert ajuste.teste is not None
    assert not ajuste.teste.compativel
    assert ajuste.teste.p_valor < 1e-10
    assert ajuste.frase == "Os dados se afastam da distribuição Normal."


def test_mais_de_5000_valores_usa_dagostino() -> None:
    dados = np.random.default_rng(7).normal(0, 1, 6000)

    teste = ajuste_normal(dados, classes=None).teste

    assert teste is not None
    assert teste.nome == "D'Agostino-Pearson K²"


def test_qui_quadrado_complementar_nas_classes(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, NORMAL.tolist()), None)

    complementar = ajuste_normal(NORMAL, classes=tabela).complementar

    assert complementar is not None
    assert complementar.nome == "Qui-quadrado"
    assert complementar.gl is not None
    assert tabela.k is not None
    assert 1 <= complementar.gl <= tabela.k - 3
    assert 0 <= complementar.p_valor <= 1


def test_poucas_classes_ficam_sem_complementar(criar_amostra: CriarAmostra) -> None:
    dados = np.array([1.0, 2.0, 2.5, 3.0, 4.0])
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, dados.tolist()), 3)

    assert ajuste_normal(dados, classes=tabela).complementar is None


@pytest.mark.parametrize(
    ("dados", "motivo"),
    [
        ([1.0, 2.0], "Normal não se aplica: precisa de pelo menos 3 valores."),
        (
            [5.0, 5.0, 5.0, 5.0],
            "Normal não se aplica: todos os valores são iguais; "
            "não há variação para medir a forma.",
        ),
    ],
)
def test_normal_nao_se_aplica_em_borda(dados: list[float], motivo: str) -> None:
    ajuste = ajuste_normal(np.array(dados), classes=None)

    assert not ajuste.aplicavel
    assert ajuste.motivo == motivo


def test_binomial_com_tentativas_informadas_e_compativel() -> None:
    ajuste = ajuste_binomial(BINOMIAL, tentativas=10)

    assert ajuste.aplicavel
    assert ajuste.teste is not None
    assert ajuste.teste.nome == "Qui-quadrado"
    assert ajuste.teste.compativel
    assert ajuste.frase == "Os dados são compatíveis com a distribuição Binomial."
    p = next(p for p in ajuste.parametros if p.simbolo == "p̂")
    assert p.valor == pytest.approx(0.299)
    assert ajuste.formula == "binomial"


def test_binomial_sem_tentativas_usa_o_maximo() -> None:
    ajuste = ajuste_binomial(BINOMIAL, tentativas=None)

    n = next(p for p in ajuste.parametros if p.simbolo == "n")
    assert n.valor == 8


def test_tentativas_menor_que_o_maximo_e_erro() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajuste_binomial(BINOMIAL, tentativas=5)

    assert erro.value.codigo == "TENTATIVAS_INVALIDAS"
    assert erro.value.mensagem == (
        "O número de tentativas precisa ser pelo menos o maior valor observado (8)."
    )


@pytest.mark.parametrize(
    ("dados", "motivo"),
    [
        ([1.5, 2.0, 3.0], "Binomial não se aplica: precisa de contagens inteiras a partir de 0."),
        ([-1.0, 2.0, 3.0], "Binomial não se aplica: precisa de contagens inteiras a partir de 0."),
        ([0.0, 0.0, 0.0], "Binomial não se aplica: todos os valores são zero."),
    ],
)
def test_binomial_exige_contagens(dados: list[float], motivo: str) -> None:
    ajuste = ajuste_binomial(np.array(dados), tentativas=None)

    assert not ajuste.aplicavel
    assert ajuste.motivo == motivo


def test_binomial_com_poucos_grupos_fica_sem_teste() -> None:
    ajuste = ajuste_binomial(np.array([0.0, 1.0, 1.0, 0.0, 1.0]), tentativas=None)

    assert ajuste.aplicavel
    assert ajuste.teste is None
    assert (ajuste.frase or "").startswith("Há poucos grupos")


def test_bernoulli_tem_parametros_e_nao_tem_teste() -> None:
    ajuste = ajuste_bernoulli(0.3)

    assert (ajuste.distribuicao, ajuste.teste, ajuste.formula) == ("bernoulli", None, "bernoulli")
    assert [round(p.valor, 4) for p in ajuste.parametros] == [0.3, 0.3, 0.21]
    assert (ajuste.frase or "").startswith("Com p estimado dos próprios dados")
