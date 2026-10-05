import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.resultados import LinhaFrequencia, TabelaFrequencia
from app.dominios.analise.tendencia import (
    media,
    mediana,
    moda,
    moda_czuber,
    proporcao,
    sucesso_padrao,
)
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra


def test_media_com_calculo(criar_amostra: CriarAmostra) -> None:
    resultado = media(criar_amostra(TipoVariavel.DISCRETA, [2.0, 4.0, 6.0]))

    assert resultado.valor == 4
    assert resultado.calculo == "Σxᵢ / n = 12 / 3 = 4"
    assert resultado.formula == "media"


@pytest.mark.parametrize(
    ("tipo", "motivo"),
    [
        (
            TipoVariavel.NOMINAL,
            "Média não se aplica a qualitativas nominais: não dá para somar categorias.",
        ),
        (
            TipoVariavel.BINARIA,
            "Média não se aplica a binárias: use a proporção, que é a média de uma variável 0/1.",
        ),
    ],
)
def test_media_nao_se_aplica_a_categorias(
    criar_amostra: CriarAmostra, tipo: TipoVariavel, motivo: str
) -> None:
    resultado = media(criar_amostra(tipo, ["a", "b"]))

    assert (resultado.aplicavel, resultado.motivo, resultado.valor) == (False, motivo, None)


def test_mediana_par_e_media_dos_centrais(criar_amostra: CriarAmostra) -> None:
    assert mediana(criar_amostra(TipoVariavel.CONTINUA, [4.0, 1.0, 3.0, 2.0])).valor == 2.5


def test_mediana_ordinal_e_a_categoria_da_posicao_central(criar_amostra: CriarAmostra) -> None:
    valores = ["ruim", "bom", "bom", "ótimo", "regular"]

    resultado = mediana(criar_amostra(TipoVariavel.ORDINAL, valores, ESCALA_SATISFACAO))

    assert resultado.valor == "bom"
    assert resultado.calculo == "posição (n + 1) / 2 = 3 → bom"


def test_mediana_nao_se_aplica_a_nominal(criar_amostra: CriarAmostra) -> None:
    assert mediana(criar_amostra(TipoVariavel.NOMINAL, ["a", "b"])).aplicavel is False


@pytest.mark.parametrize(
    ("valores", "esperado", "classificacao"),
    [
        ([1.0, 2.0, 2.0, 3.0], (2.0,), "unimodal"),
        ([1.0, 1.0, 2.0, 2.0, 3.0], (1.0, 2.0), "bimodal"),
        ([1.0, 2.0, 3.0], (), "amodal"),
        ([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0], (1.0, 2.0, 3.0), "multimodal"),
    ],
)
def test_moda_e_classificacao(
    criar_amostra: CriarAmostra,
    valores: list[float],
    esperado: tuple[float, ...],
    classificacao: str,
) -> None:
    resultado = moda(criar_amostra(TipoVariavel.DISCRETA, valores))

    assert (resultado.valores, resultado.classificacao) == (esperado, classificacao)


def test_frases_da_moda(criar_amostra: CriarAmostra) -> None:
    uni = moda(criar_amostra(TipoVariavel.NOMINAL, ["Goiânia", "Goiânia", "Anápolis"]))
    bi = moda(criar_amostra(TipoVariavel.DISCRETA, [1.0, 1.0, 2.0, 2.0, 3.0]))

    assert uni.interpretacao == "O valor mais frequente é Goiânia (2 vezes)."
    assert bi.interpretacao == "Há 2 modas: 1 e 2 (2 vezes cada)."


def _tabela_do_design() -> TabelaFrequencia:
    """Classes do print 4b: h = 5,5 e classe modal 65,5 ⊢ 71,0 (fᵢ = 49)."""
    frequencias = [4, 9, 20, 36, 49, 47, 34, 18, 10]
    linhas = tuple(
        LinhaFrequencia(
            rotulo="",
            valor=None,
            fi=fi,
            fri=0.0,
            fr_pct=0.0,
            limite_inferior=43.5 + i * 5.5,
            limite_superior=49.0 + i * 5.5,
            ponto_medio=46.25 + i * 5.5,
        )
        for i, fi in enumerate(frequencias)
    )
    return TabelaFrequencia(
        TipoVariavel.CONTINUA, linhas, 227, True, indice_modal=4, k=9, k_sturges=9, h=5.5
    )


def test_moda_de_czuber(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.CONTINUA, [1.0, 2.0])

    resultado = moda_czuber(amostra, _tabela_do_design())

    # Mo = 65,5 + [13 / (13 + 2)] · 5,5 = 70,27
    assert resultado.valor == pytest.approx(70.2667, abs=1e-4)
    assert resultado.calculo == "Mo = 65,5 + [13 / (13 + 2)] · 5,5 = 70,27"


def test_moda_de_czuber_so_para_continua(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.DISCRETA, [1.0, 2.0])

    assert moda_czuber(amostra, _tabela_do_design()).aplicavel is False


@pytest.mark.parametrize(
    ("valores", "sucesso"),
    [(["sim", "não", "sim"], "sim"), (["0", "1", "0"], "1"), (["A", "B", "B"], "A")],
)
def test_sucesso_padrao(criar_amostra: CriarAmostra, valores: list[str], sucesso: str) -> None:
    assert sucesso_padrao(criar_amostra(TipoVariavel.BINARIA, valores).valores) == sucesso


def test_proporcao(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.BINARIA, ["sim", "não", "sim", "sim"])

    padrao = proporcao(amostra, None)
    escolhida = proporcao(amostra, "não")

    assert padrao.valor == 0.75
    assert padrao.calculo == "p = 3 / 4 = 0,75"
    assert padrao.interpretacao == '75,0% dos valores são "sim".'
    assert escolhida.valor == 0.25


def test_proporcao_so_para_binaria(criar_amostra: CriarAmostra) -> None:
    assert proporcao(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "c"]), None).aplicavel is False
