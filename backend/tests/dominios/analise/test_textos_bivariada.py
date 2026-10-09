import pytest

from app.dominios.analise import textos_bivariada as t
from app.dominios.analise.resultados_bivariada import Faixa


@pytest.mark.parametrize(
    ("a", "b", "equacao"),
    [
        (-98.4, 98.1, "Ŷ = −98,4 + 98,1·X"),
        (2.2, -0.6, "Ŷ = 2,2 − 0,6·X"),
        (2.2, 0.6, "Ŷ = 2,2 + 0,6·X"),
        (0.0, 1.0, "Ŷ = 0 + 1·X"),
    ],
)
def test_formatar_equacao(a: float, b: float, equacao: str) -> None:
    assert t.formatar_equacao(a, b) == equacao


@pytest.mark.parametrize(
    ("forca", "sentido", "frase"),
    [
        ("forte", "positiva", "Quando altura_m aumenta, peso_kg tende a aumentar."),
        ("moderada", "negativa", "Quando altura_m aumenta, peso_kg tende a diminuir."),
        ("fraca", "positiva", "altura_m e peso_kg quase não andam juntas."),
    ],
)
def test_frase_da_forca(forca: t.Forca, sentido: t.Sentido, frase: str) -> None:
    assert t.frase_forca(forca, sentido, "altura_m", "peso_kg") == frase


def test_frase_de_significancia() -> None:
    assert t.frase_significancia(0.0004) == (
        "A correlação é significativa (chance de acontecer por acaso: menos de 1 em 1.000)."
    )
    assert t.frase_significancia(0.124) == (
        "A correlação não é significativa: pode ter aparecido por acaso (cerca de 1 em 8)."
    )


def test_frases_da_regressao() -> None:
    assert t.frase_r2(61.0, "altura_m", "peso_kg") == (
        "61% da variação de peso_kg é explicada por altura_m."
    )
    assert t.frase_reta(98.1, "altura_m", "peso_kg") == (
        "A cada 1 a mais em altura_m, o valor previsto de peso_kg sobe cerca de 98,1."
    )
    assert t.frase_reta(-0.6, "x", "y") == (
        "A cada 1 a mais em x, o valor previsto de y cai cerca de 0,6."
    )
    assert t.frase_reta(0.0, "x", "y") == "O valor previsto de y não muda com x."
    assert t.frase_se(0.894427, "y") == (
        "Em média, as previsões de y erram cerca de 0,8944 para mais ou para menos."
    )


def test_frase_de_previsao_e_aviso() -> None:
    assert t.frase_previsao("x", 3.5, "y", 4.3) == "Para x = 3,5, o valor previsto de y é 4,3."
    assert t.aviso_extrapolacao("altura_m", Faixa(1.48, 1.96)) == (
        "Os valores de altura_m vão de 1,48 a 1,96. "
        "Prever fora disso (extrapolar) pode dar resultados pouco confiáveis."
    )


def test_resumo_da_matriz() -> None:
    valores = (
        (1.0, 0.12, 0.21),
        (0.12, 1.0, 0.78),
        (0.21, 0.78, 1.0),
    )

    assert t.resumo_matriz(("idade", "altura_m", "peso_kg"), valores) == (
        "O par mais forte é altura_m × peso_kg (0,78). idade quase não se relaciona com as outras."
    )


def test_resumo_da_matriz_com_varias_fracas_e_vazios() -> None:
    valores = (
        (1.0, None, 0.1),
        (None, 1.0, -0.2),
        (0.1, -0.2, 1.0),
    )

    assert t.resumo_matriz(("a", "b", "c"), valores) == (
        "O par mais forte é b × c (−0,2). a, b e c quase não se relacionam com as outras."
    )


def test_resumo_da_matriz_sem_pares() -> None:
    assert t.resumo_matriz(("a",), ((1.0,),)) == (
        "Precisa de pelo menos duas colunas numéricas para montar a matriz."
    )
