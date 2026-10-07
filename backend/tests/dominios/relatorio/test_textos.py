import pytest

from app.dominios.relatorio.conteudo import DadosLeitura
from app.dominios.relatorio.textos import descrever_leitura, subtitulo


def test_descrever_leitura_de_txt() -> None:
    dados = DadosLeitura("txt", ";", ",", "utf-8", True, 230, 8)

    assert descrever_leitura(dados) == (
        "Arquivo de texto separado por ponto e vírgula, decimal com vírgula, codificação UTF-8 "
        "e cabeçalho na primeira linha. Foram lidas 230 linhas e 8 colunas."
    )


def test_descrever_leitura_de_planilha() -> None:
    dados = DadosLeitura("xlsx", None, None, None, True, 1, 1)

    assert descrever_leitura(dados) == (
        "Planilha do Excel com cabeçalho na primeira linha. Foram lidas 1 linha e 1 coluna."
    )


@pytest.mark.parametrize(
    ("n", "original", "esperado"),
    [
        (227, 230, "pesquisa.txt · 227 linhas após limpeza × 8 colunas"),
        (230, 230, "pesquisa.txt · 230 linhas × 8 colunas"),
    ],
)
def test_subtitulo(n: int, original: int, esperado: str) -> None:
    assert subtitulo("pesquisa.txt", n, original, 8) == esperado
