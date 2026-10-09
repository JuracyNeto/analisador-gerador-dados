from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.formulas import FORMULAS, formulas_usadas
from app.dominios.analise.univariada import analisar_amostra
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

LIVRO = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]


def test_continua_tem_tudo_menos_proporcao(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, LIVRO))

    assert analise.aplicavel == {
        "acumulada": True,
        "media": True,
        "mediana": True,
        "moda_czuber": True,
        "proporcao": False,
        "separatrizes": True,
        "posicao": True,
        "dispersao": True,
        "variancia": True,
        "cv": True,
        "forma": True,
        "assimetria": True,
        "curtose": True,
        "normal": True,
        "binomial": False,
    }
    assert [n.item for n in analise.nao_aplicavel] == ["proporcao", "binomial"]
    chaves = [f.chave for f in analise.formulas]
    assert {"sturges", "media", "moda_czuber", "variancia", "cv"} <= set(chaves)
    assert analise.figuras == ()


def test_nominal_explica_cada_item_que_nao_se_aplica(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "b"]))

    itens = {n.item: n.motivo for n in analise.nao_aplicavel}
    assert {"acumulada", "media", "mediana", "separatrizes", "posicao", "dispersao"} <= set(itens)
    assert itens["separatrizes"] == (
        "Separatrizes não se aplicam a qualitativas nominais: "
        "as categorias não têm ordem para dividir em partes."
    )
    assert analise.separatrizes is None
    assert analise.dispersao is None
    assert not any(analise.aplicavel.values())
    assert [f.chave for f in analise.formulas] == ["frequencia_relativa", "moda"]


def test_ordinal_tem_mediana_e_separatrizes_em_categorias(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(
        TipoVariavel.ORDINAL, ["ruim", "bom", "bom", "ótimo"], ESCALA_SATISFACAO
    )

    analise = analisar_amostra(amostra)

    assert analise.aplicavel["mediana"] is True
    assert analise.aplicavel["separatrizes"] is True
    assert analise.aplicavel["posicao"] is False
    assert analise.tendencia.mediana.valor == "bom"


def test_interpretacoes_automaticas(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, [1.0, 2.0, 3.0, 4.0, 5.0]))

    assert analise.interpretacoes == (
        "Média e mediana próximas (diferença de 0): a distribuição parece simétrica.",
        "Os dados são heterogêneos (muita variação em relação à média).",
    )


def test_assimetria_a_direita(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, [1.0, 1.5, 2.0, 2.5, 30.0]))

    assert analise.interpretacoes[0].startswith("Média maior que a mediana")


def test_formulas_usadas_seguem_o_catalogo_sem_repetir() -> None:
    usadas = formulas_usadas(["media", "moda", "media", None])

    assert [f.chave for f in usadas] == ["media", "moda"]
    assert FORMULAS["cv"].texto == "CV = (s / x̄) · 100%"
