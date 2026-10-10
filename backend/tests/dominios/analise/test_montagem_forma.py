import numpy as np

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.univariada import analisar_amostra
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

NORMAL = np.random.default_rng(42).normal(70, 11, 227).round(1).tolist()
CONTAGENS = np.random.default_rng(5).binomial(10, 0.3, 40).astype("float64").tolist()


def test_continua_tem_normal_e_nao_tem_binomial(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, NORMAL))

    forma = analise.forma
    assert forma is not None
    assert forma.normal.aplicavel
    assert forma.normal.complementar is not None
    assert forma.binomial.motivo == (
        "Binomial não se aplica a quantitativas contínuas: "
        "precisa de contagens de sucessos em n tentativas."
    )
    assert forma.classificacao_assimetria == "simetrica"
    assert forma.assimetria_pearson_1.aplicavel  # moda de Czuber
    assert forma.curtose_percentilica.aplicavel
    assert (forma.interpretacao or "").startswith("Distribuição aproximadamente simétrica")
    assert "compatível com a Normal" in (forma.interpretacao or "")
    assert forma.tentativas is None


def test_continua_marca_aplicabilidade_e_formulas(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, NORMAL))

    assert {k: analise.aplicavel[k] for k in ("forma", "assimetria", "curtose", "normal")} == {
        "forma": True,
        "assimetria": True,
        "curtose": True,
        "normal": True,
    }
    assert analise.aplicavel["binomial"] is False
    assert "binomial" in [n.item for n in analise.nao_aplicavel]
    chaves = {f.chave for f in analise.formulas}
    assert {"assimetria", "curtose", "curtose_percentilica", "normal", "qui_quadrado"} <= chaves
    assert "binomial" not in chaves


def test_discreta_tem_binomial_e_normal(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.DISCRETA, CONTAGENS))

    forma = analise.forma
    assert forma is not None
    assert forma.binomial.aplicavel
    assert forma.normal.aplicavel
    assert forma.tentativas == int(max(CONTAGENS))
    assert analise.aplicavel["binomial"] is True


def test_discreta_com_tentativas_informadas(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.DISCRETA, CONTAGENS), tentativas=10)

    assert analise.forma is not None
    assert analise.forma.tentativas == 10


def test_discreta_com_poucos_valores_nao_aproxima_pela_normal(
    criar_amostra: CriarAmostra,
) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.DISCRETA, [0, 1, 1, 2, 2, 3, 1, 0, 2, 1]))

    forma = analise.forma
    assert forma is not None
    assert forma.normal.motivo == (
        "Normal não se aplica: a aproximação pela Normal precisa de pelo menos 30 valores."
    )
    assert forma.binomial.aplicavel


def test_binaria_usa_bernoulli(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.BINARIA, ["F", "M", "M", "F", "M"]))

    forma = analise.forma
    assert forma is not None
    assert forma.binomial.distribuicao == "bernoulli"
    assert not forma.assimetria.aplicavel
    assert (
        forma.assimetria.motivo == "Assimetria não se aplica a binárias: os valores são categorias."
    )
    assert not forma.normal.aplicavel
    assert analise.aplicavel["forma"] is True
    assert analise.aplicavel["assimetria"] is False
    assert "bernoulli" in {f.chave for f in analise.formulas}


def test_nominal_e_ordinal_nao_tem_forma(criar_amostra: CriarAmostra) -> None:
    nominal = analisar_amostra(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "b"]))
    ordinal = analisar_amostra(
        criar_amostra(TipoVariavel.ORDINAL, ["ruim", "bom", "bom"], ESCALA_SATISFACAO)
    )

    for analise in (nominal, ordinal):
        assert analise.forma is None
        assert analise.aplicavel["forma"] is False
    motivos = {n.item: n.motivo for n in nominal.nao_aplicavel}
    assert motivos["forma"] == (
        "Forma e distribuição não se aplica a qualitativas nominais: "
        "as distribuições Normal e Binomial exigem números."
    )
