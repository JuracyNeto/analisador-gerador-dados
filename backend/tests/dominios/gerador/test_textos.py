import re

import pytest

from app.dominios.gerador.textos import (
    ContextoExplicacao,
    ContextoPares,
    estatisticas_par,
    explicacao_bivariada,
    explicacao_univariada,
    frase_casas,
)

MAX_PALAVRAS = 25  # spec 16, princípio 5


def _maior_frase(texto: str) -> int:
    return max(len(frase.split()) for frase in re.split(r"(?<=[.;])\s+", texto))


def test_explicacao_normal_preservando() -> None:
    contexto = ContextoExplicacao("normal", 500, 42, "peso_kg", 70.3, 11.2, casas=1, preservar=True)

    assert explicacao_univariada(contexto) == (
        "Sorteamos 500 valores de uma curva Normal com a mesma média (70,3) e desvio padrão "
        "(11,2) de peso_kg, usando a semente 42. Depois, ajustamos os valores para bater "
        "exatamente essas medidas. Arredondamos com 1 casa decimal, como no original."
    )


def test_explicacao_com_faixa() -> None:
    contexto = ContextoExplicacao(
        "normal", 500, 42, "peso_kg", 70.3, 11.2, casas=1, faixa=(43.8, 92.9), preservar=True
    )

    assert explicacao_univariada(contexto).endswith(
        "Sorteamos de novo os valores fora de 43,8 a 92,9."
    )


def test_explicacao_parametros_sem_origem() -> None:
    contexto = ContextoExplicacao("normal", 1, 7, media=-5.0, desvio=2.0, casas=2)

    assert explicacao_univariada(contexto) == (
        "Sorteamos 1 valor de uma curva Normal com média −5 e desvio padrão 2, usando a "
        "semente 7. Depois, ajustamos os valores para bater exatamente essas medidas. "
        "Arredondamos com 2 casas decimais."
    )


@pytest.mark.parametrize(
    ("metodo", "trecho"),
    [
        ("kde", "não seguem uma curva Normal"),
        ("poisson", "de uma Poisson com média 3"),
        ("empirica", "entre os que aparecem em faltas"),
        ("normal_inteira", "Depois, arredondamos para inteiros"),
        ("frequencias", "entre as categorias de faltas"),
    ],
)
def test_explicacao_por_metodo(metodo: str, trecho: str) -> None:
    contexto = ContextoExplicacao(metodo, 10, 1, "peso_por_dia_kg", 3.0, 1.5, preservar=True)
    contexto_faltas = ContextoExplicacao(metodo, 10, 1, "faltas", 3.0, 1.5, preservar=True)

    assert trecho in explicacao_univariada(contexto_faltas)
    assert _maior_frase(explicacao_univariada(contexto)) <= MAX_PALAVRAS


def test_explicacao_bernoulli() -> None:
    contexto = ContextoExplicacao(
        "bernoulli", 10, 1, "sexo", chance=0.49, sucesso="F", fracasso="M", preservar=True
    )

    assert "cada um é F com chance de 49,0% (a mesma proporção do original) ou M" in (
        explicacao_univariada(contexto)
    )


@pytest.mark.parametrize(
    ("casas", "frase"),
    [(0, "Arredondamos para inteiros."), (None, ""), (3, "Arredondamos com 3 casas decimais.")],
)
def test_frase_casas(casas: int | None, frase: str) -> None:
    assert frase_casas(casas, preservar=False) == frase


def test_explicacao_bivariada_com_ajuste_exato() -> None:
    contexto = ContextoPares(500, "altura_m", "peso_kg", 1.7, 70.0, 0.09, 11.0, 0.7, 42, True)

    texto = explicacao_bivariada(contexto)

    assert texto.startswith("Sorteamos 500 pares de duas curvas Normais")
    assert (
        "Assim, peso_kg acompanha altura_m com correlação 0,7; altura_m tem média 1,7 e "
        "desvio padrão 0,09, e peso_kg, média 70 e desvio padrão 11." in texto
    )
    assert "exatamente iguais aos pedidos" in texto
    assert _maior_frase(texto) <= MAX_PALAVRAS


def test_estatisticas_do_par_usam_desvio_padrao() -> None:
    assert estatisticas_par("x", "y")[3:5] == ("Desvio padrão de x", "Desvio padrão de y")
