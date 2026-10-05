import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.dispersao import SEM_DISPERSAO, classificar_cv, dispersao
from app.dominios.analise.resultados import Dispersao, Medida
from app.dominios.analise.separatrizes import separatrizes
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

SEM_PROPORCAO = Medida(aplicavel=False)
LIVRO = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]


def _dispersao(criar_amostra: CriarAmostra, tipo: TipoVariavel, valores: list[float]) -> Dispersao:
    amostra = criar_amostra(tipo, valores)
    resultado = dispersao(amostra, separatrizes(amostra), SEM_PROPORCAO)
    assert resultado is not None
    return resultado


def test_exemplo_de_livro(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, LIVRO)

    assert resultado.amplitude.valor == 7
    assert resultado.variancia_populacional.valor == 4
    assert resultado.variancia.valor == pytest.approx(32 / 7)
    assert resultado.desvio_padrao.valor == pytest.approx(2.13809, abs=1e-5)
    assert resultado.iqr.valor == 1.5
    assert resultado.cv.valor == pytest.approx(42.76, abs=0.01)
    assert resultado.classificacao_cv == "alta"
    assert resultado.variancia.calculo == "Σ(xᵢ − x̄)² / (n − 1) = 32 / 7 = 4,571"


def test_variancia_amostral_usa_n_menos_1(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [1.0, 3.0])

    assert (resultado.variancia.valor, resultado.variancia_populacional.valor) == (2.0, 1.0)


def test_um_valor_so_nao_tem_variancia(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [5.0])

    assert resultado.variancia.motivo == "Variância não se aplica: precisa de pelo menos 2 valores."
    assert resultado.cv.aplicavel is False


def test_media_zero_nao_tem_cv(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [-1.0, 1.0])

    assert resultado.cv.motivo == "O CV não pode ser calculado porque a média é zero."


def test_cv_com_negativos_avisa(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [-2.0, 4.0, 6.0])

    assert resultado.cv.interpretacao is not None
    assert resultado.cv.interpretacao.endswith("CV pouco interpretável com valores negativos.")


def test_valores_iguais_nao_tem_dispersao(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.DISCRETA, [3.0, 3.0, 3.0])

    assert resultado.desvio_padrao.interpretacao == SEM_DISPERSAO
    assert resultado.classificacao_cv == "baixa"


@pytest.mark.parametrize(
    ("cv", "classe"), [(14.9, "baixa"), (15.0, "media"), (29.9, "media"), (30.1, "alta")]
)
def test_classificacao_do_cv(cv: float, classe: str) -> None:
    assert classificar_cv(cv) == classe


def test_binaria_usa_p_vezes_1_menos_p(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.BINARIA, ["a", "b"])

    resultado = dispersao(amostra, None, Medida(0.5))

    assert resultado is not None
    assert (resultado.variancia.valor, resultado.desvio_padrao.valor) == (0.25, 0.5)
    assert resultado.amplitude.aplicavel is False


def test_ordinal_em_categorias(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(
        TipoVariavel.ORDINAL, ["ruim", "regular", "bom", "bom", "ótimo"], ESCALA_SATISFACAO
    )

    resultado = dispersao(amostra, separatrizes(amostra), SEM_PROPORCAO)

    assert resultado is not None
    assert resultado.amplitude.valor == "de ruim a ótimo"
    assert resultado.iqr.valor == "de regular a bom"
    assert resultado.variancia.aplicavel is False


def test_nominal_nao_tem_dispersao(criar_amostra: CriarAmostra) -> None:
    assert dispersao(criar_amostra(TipoVariavel.NOMINAL, ["a", "b"]), None, SEM_PROPORCAO) is None
