import pytest

from app.compartilhado.textos import juntar_lista, normalizar_texto, pluralizar


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
