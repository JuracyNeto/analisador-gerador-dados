import pytest

from app.compartilhado.textos import (
    juntar_lista,
    normalizar_texto,
    p_valor_em_palavras,
    pluralizar,
)


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [("  São   Paulo ", "sao paulo"), ("GOIÂNIA", "goiania"), ("Pós-graduação", "pos-graduacao")],
)
def test_normalizar_texto_tira_acento_caixa_e_espacos(texto: str, esperado: str) -> None:
    assert normalizar_texto(texto) == esperado


def test_pluralizar_escolhe_pela_quantidade() -> None:
    assert pluralizar(1, "linha", "linhas") == "linha"
    assert pluralizar(0, "linha", "linhas") == "linhas"
    assert pluralizar(3, "linha", "linhas") == "linhas"


@pytest.mark.parametrize(
    ("itens", "esperado"),
    [([], ""), (["a"], "a"), (["a", "b"], "a e b"), (["a", "b", "c"], "a, b e c")],
)
def test_juntar_lista_em_portugues(itens: list[str], esperado: str) -> None:
    assert juntar_lista(itens) == esperado


@pytest.mark.parametrize(
    ("p", "esperado"),
    [
        (0.0004, "menos de 1 em 1.000"),
        (0.02, "cerca de 1 em 50"),
        (0.21, "cerca de 1 em 5"),
        (0.7, "mais de 1 em 2"),
    ],
)
def test_p_valor_em_palavras(p: float, esperado: str) -> None:
    assert p_valor_em_palavras(p) == esperado
