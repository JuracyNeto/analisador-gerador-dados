import pytest

from app.dominios.analise import erros


@pytest.mark.parametrize(
    ("n", "mensagem"),
    [
        (0, "Nenhuma linha tem x e y preenchidos; precisamos de pelo menos 3."),
        (1, "Só 1 linha tem x e y preenchidos; precisamos de pelo menos 3."),
        (2, "Só 2 linhas têm x e y preenchidos; precisamos de pelo menos 3."),
    ],
)
def test_poucos_pares_concorda_com_o_numero_de_linhas(n: int, mensagem: str) -> None:
    assert erros.poucos_pares(n, "x", "y").mensagem == mensagem


def test_coluna_nao_numerica_diz_o_que_aconteceu_e_a_sugestao_diz_o_que_fazer() -> None:
    erro = erros.coluna_nao_numerica("cidade")

    assert (erro.mensagem, erro.sugestao) == (
        "A coluna cidade não é numérica.",
        "Escolha colunas discretas ou contínuas.",
    )
