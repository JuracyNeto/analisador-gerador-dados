import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.deteccao import (
    SEPARADOR_ESPACOS,
    decodificar,
    detectar_cabecalho,
    detectar_decimal,
    detectar_formato,
    detectar_separador,
    linhas_amostra,
)


@pytest.mark.parametrize(
    ("nome", "formato"),
    [
        ("dados.TXT", "txt"),
        ("a.csv", "csv"),
        ("a.tsv", "tsv"),
        ("a.xlsx", "xlsx"),
        ("a.json", "json"),
    ],
)
def test_formato_vem_da_extensao(nome: str, formato: str) -> None:
    assert detectar_formato(nome).valor == formato


def test_extensao_desconhecida_e_recusada() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        detectar_formato("relatorio_final.pdf")

    assert erro.value.codigo == "FORMATO_NAO_SUPORTADO"
    assert "relatorio_final.pdf" in erro.value.mensagem


@pytest.mark.parametrize(
    ("conteudo", "codificacao"),
    [
        ("Goiânia".encode("utf-8-sig"), "utf-8-sig"),
        ("Goiânia".encode(), "utf-8"),
        ("Goiânia – ok".encode("cp1252"), "cp1252"),
        (b"Goi\x81nia", "latin-1"),
    ],
)
def test_codificacao_segue_a_ordem_da_spec(conteudo: bytes, codificacao: str) -> None:
    _, detectada = decodificar(conteudo, None)

    assert detectada.valor == codificacao


def test_codificacao_escolhida_pelo_usuario_vence() -> None:
    texto, detectada = decodificar("Goiânia".encode("latin-1"), "latin-1")

    assert texto == "Goiânia"
    assert detectada.motivo == "Escolhida por você."


def test_motivo_da_codificacao_cita_uma_palavra_acentuada() -> None:
    _, detectada = decodificar("cidade\nGoiânia\n".encode(), None)

    assert detectada.motivo == "Acentos lidos sem erro (Goiânia)."


@pytest.mark.parametrize(
    ("texto", "separador"),
    [
        ("a;b;c\n1,5;2;3\n4;5,5;6\n", ";"),
        ("a,b\n1.5,2\n3,4\n", ","),
        ("a\tb\n1\t2\n", "\t"),
        ("a|b\n1|2\n", "|"),
        ("nome    idade\nAna     34\nBruno   27\n", SEPARADOR_ESPACOS),
    ],
)
def test_separador_e_o_que_se_repete_em_todas_as_linhas(texto: str, separador: str) -> None:
    detectado = detectar_separador(linhas_amostra(texto))

    assert detectado.valor == separador


def test_ponto_e_virgula_vence_a_virgula_decimal() -> None:
    texto = "id;altura;peso\n1;1,62;58,2\n2;1,78;\n3;1,58;63,0\n"

    detectado = detectar_separador(linhas_amostra(texto))

    assert detectado.valor == ";"
    assert detectado.motivo == "Aparece 2 vezes em todas as linhas."


def test_sem_separador_le_uma_coluna() -> None:
    assert detectar_separador(["valor", "1", "2"]).valor is None


@pytest.mark.parametrize(
    ("linhas", "separador", "decimal"),
    [
        (["a;b", "1,62;58,2", "1.234,5;7"], ";", ","),
        (["a,b", "1.62,58.2"], ",", "."),
        (["a;b", "1;2"], ";", ","),
        (["a,b", "1,2"], ",", "."),
    ],
)
def test_decimal_detectado(linhas: list[str], separador: str, decimal: str) -> None:
    assert detectar_decimal(linhas, separador).valor == decimal


def test_motivo_do_decimal_mostra_exemplos() -> None:
    detectado = detectar_decimal(["a;b", "1,72;68,4"], ";")

    assert detectado.motivo == "Valores como 1,72 e 68,4."


@pytest.mark.parametrize(
    ("linhas", "tem_cabecalho"),
    [
        (["nome;idade", "Ana;34", "Bruno;27"], True),
        (["10;1,5", "20;2,5"], False),
        (["F;bom", "M;ruim", "F;bom"], False),
        (["sexo;satisfacao", "F;bom", "M;ruim"], True),
        (["só uma linha"], True),
    ],
)
def test_cabecalho_detectado(linhas: list[str], tem_cabecalho: bool) -> None:
    assert detectar_cabecalho(linhas, ";").valor is tem_cabecalho
