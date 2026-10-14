import pytest

from app.dominios.detector import textos

VALORES = ("70", "75", "80", "75", "70", "75", "80", "70", "85", "90")


def test_exemplo_com_linhas_seguidas_usa_a_faixa_e_corta_em_8_valores() -> None:
    linhas = tuple(range(120, 139))

    texto = textos.texto_exemplo(linhas, VALORES)

    assert texto == "Linhas 120 a 138: 70, 75, 80, 75, 70, 75, 80, 70…"


def test_exemplo_com_linhas_soltas_lista_as_linhas() -> None:
    assert textos.texto_exemplo((3, 9, 14), ("70", "75", "80")) == "Linhas 3, 9 e 14: 70, 75, 80"


def test_valores_com_decimais_separados_por_ponto_e_virgula() -> None:
    texto = textos.texto_exemplo((99, 160), ("6,8", "712"))

    assert texto == "Linhas 99 e 160: 6,8; 712"


def test_exemplo_de_uma_linha_so() -> None:
    assert textos.texto_exemplo((12,), ("94",)) == "Linha 12: 94"


def test_muitas_linhas_soltas_mostram_as_8_primeiras() -> None:
    linhas = (1, 3, 5, 7, 9, 11, 13, 15, 17, 19)

    assert textos.faixa_de_linhas(linhas) == "Linhas 1, 3, 5, 7, 9, 11, 13, 15…"


def test_duas_linhas_seguidas_nao_viram_faixa() -> None:
    assert textos.faixa_de_linhas((44, 45)) == "Linhas 44 e 45"


@pytest.mark.parametrize(
    ("coluna", "esperado"),
    [
        ("idade", "Lei de Benford não verificada em idade: precisa de 100 valores ou mais."),
        (None, "Lei de Benford não verificada: precisa de 100 valores ou mais."),
    ],
)
def test_frase_da_regra_nao_aplicada(coluna: str | None, esperado: str) -> None:
    frase = textos.frase_nao_aplicada("Lei de Benford", coluna, "precisa de 100 valores ou mais")

    assert frase == esperado


def test_poucos_valores_diz_o_minimo_e_quantos_a_coluna_tem() -> None:
    assert textos.poucos_valores(100, 48) == "precisa de 100 valores ou mais; a coluna tem 48"


def test_p_em_palavras_traduz_o_p_valor() -> None:
    assert textos.p_em_palavras(0.0002) == "chance de acontecer por acaso: menos de 1 em 1.000"
    assert textos.p_em_palavras(0.02) == "chance de acontecer por acaso: cerca de 1 em 50"


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [(70.0, "70"), (1.62, "1,62"), (58.2, "58,2"), (0.0123, "0,0123"), (-3.5, "−3,5")],
)
def test_valor_do_exemplo_sem_zeros_a_direita(valor: float, esperado: str) -> None:
    assert textos.valor(valor) == esperado


def test_razao_com_uma_casa() -> None:
    assert textos.razao(2.3) == "2,3×"
