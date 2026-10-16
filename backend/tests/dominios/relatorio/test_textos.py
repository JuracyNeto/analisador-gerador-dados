import pytest

from app.dominios.relatorio.conteudo import DadosLeitura
from app.dominios.relatorio.textos import (
    SELOS_SEVERIDADE,
    contadores_severidade,
    descrever_leitura,
    selo_assimetria,
    selo_correlacao,
    subtitulo,
    subtitulo_gerador,
    titulo_aviso,
)


def test_descrever_leitura_de_txt() -> None:
    dados = DadosLeitura("txt", ";", ",", "utf-8", 1, 230, 8)

    assert descrever_leitura(dados) == (
        "Arquivo de texto separado por ponto e vírgula, decimal com vírgula, codificação UTF-8 "
        "e cabeçalho na primeira linha. Foram lidas 230 linhas e 8 colunas."
    )


def test_descrever_leitura_de_planilha() -> None:
    dados = DadosLeitura("xlsx", None, None, None, 1, 1, 1)

    assert descrever_leitura(dados) == (
        "Planilha do Excel com cabeçalho na primeira linha. Foram lidas 1 linha e 1 coluna."
    )


@pytest.mark.parametrize(
    ("linha", "trecho"), [(0, "Planilha do Excel sem cabeçalho."), (3, "com cabeçalho na linha 3")]
)
def test_descrever_leitura_cita_a_linha_do_cabecalho(linha: int, trecho: str) -> None:
    assert trecho in descrever_leitura(DadosLeitura("xlsx", None, None, None, linha, 2, 2))


@pytest.mark.parametrize(
    ("n", "original", "esperado"),
    [
        (227, 230, "pesquisa.txt · 227 linhas após limpeza × 8 colunas"),
        (230, 230, "pesquisa.txt · 230 linhas × 8 colunas"),
    ],
)
def test_subtitulo(n: int, original: int, esperado: str) -> None:
    assert subtitulo("pesquisa.txt", n, original, 8) == esperado


@pytest.mark.parametrize(
    ("classe", "sentido", "esperado"),
    [
        ("simetrica", None, "Simétrica"),
        ("simetrica", "direita", "Aproximadamente simétrica"),
        ("moderada", None, "Moderada"),
        ("forte", "esquerda", "Forte à esquerda"),
    ],
)
def test_selo_assimetria(classe: str, sentido: str | None, esperado: str) -> None:
    assert selo_assimetria(classe, sentido) == esperado


@pytest.mark.parametrize(
    ("forca", "sentido", "esperado"),
    [
        ("forte", "positiva", "Positiva forte"),
        ("moderada", "nula", "Fraca"),
        ("fraca", "negativa", "Fraca"),
    ],
)
def test_selo_correlacao(forca: str, sentido: str, esperado: str) -> None:
    assert selo_correlacao(forca, sentido) == esperado


@pytest.mark.parametrize(
    ("tipo", "n", "esperado"),
    [
        ("univariado", 1, "Univariado · 1 valor · semente 42"),
        ("univariado", 1500, "Univariado · 1.500 valores · semente 42"),
        ("bivariado", 300, "Bivariado · 300 pares · semente 42"),
    ],
)
def test_subtitulo_gerador(tipo: str, n: int, esperado: str) -> None:
    assert subtitulo_gerador(tipo, n, 42) == esperado


@pytest.mark.parametrize(
    ("contagens", "esperado"),
    [
        ((2, 2, 1), "2 suspeitas altas · 2 de atenção · 1 informativo"),
        ((1, 0, 3), "1 suspeita alta · 0 de atenção · 3 informativos"),
    ],
)
def test_contadores_severidade(contagens: tuple[int, int, int], esperado: str) -> None:
    assert contadores_severidade(*contagens) == esperado


def test_selos_com_icone_e_palavra() -> None:
    assert SELOS_SEVERIDADE == {
        "alta": "⛔ Suspeita alta",
        "atencao": "⚠️ Atenção",
        "info": "ℹ️ Informativo",
    }
    assert titulo_aviso("R4", "Muitos valores redondos em peso_kg") == (
        "R4 · Muitos valores redondos em peso_kg"
    )
