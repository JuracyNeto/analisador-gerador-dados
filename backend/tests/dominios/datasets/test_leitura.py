import io
import math
from pathlib import Path

import pandas as pd
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.leitura import ler_arquivo, padronizar_nomes
from app.dominios.datasets.modelos import OpcoesLeitura, ResultadoLeitura

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
SEM_OPCOES = OpcoesLeitura()


def _ler(nome: str, opcoes: OpcoesLeitura = SEM_OPCOES) -> ResultadoLeitura:
    return ler_arquivo((FIXTURES / nome).read_bytes(), nome, opcoes)


def test_txt_com_ponto_e_virgula_e_virgula_decimal() -> None:
    resultado = _ler("ponto_e_virgula.txt")

    assert resultado.metadados.separador == ";"
    assert resultado.metadados.decimal == ","
    assert resultado.dados["altura"].tolist() == [1.62, 1.78, 1.58]
    assert resultado.dados["peso"].iloc[1] == 1079.6
    assert math.isnan(resultado.dados["peso"].iloc[2])


def test_csv_com_virgula_e_ponto_decimal() -> None:
    resultado = _ler("virgula.csv")

    assert resultado.metadados.formato == "csv"
    assert resultado.dados["valor"].tolist() == [1.5, 2.25, 3.0]


def test_tsv_usa_tabulacao() -> None:
    resultado = _ler("tabulacao.tsv")

    assert resultado.metadados.separador == "\t"
    assert list(resultado.dados.columns) == ["produto", "preco", "unidades"]


def test_sem_cabecalho_cria_nomes_col_n() -> None:
    resultado = _ler("sem_cabecalho.txt")

    assert resultado.metadados.linha_cabecalho == 0
    assert list(resultado.dados.columns) == ["col_1", "col_2", "col_3"]
    assert len(resultado.dados) == 3


def test_latin1_com_acentos_e_lido_pela_cp1252() -> None:
    # cp1252 vem antes de latin-1 na spec e decodifica os acentos do português igual.
    conteudo = "cidade;valor\nGoiânia;1,5\nAnápolis;2,5\n".encode("latin-1")

    resultado = ler_arquivo(conteudo, "dados.txt", SEM_OPCOES)

    assert resultado.metadados.codificacao == "cp1252"
    assert resultado.dados["cidade"].tolist() == ["Goiânia", "Anápolis"]


def test_json_aninhado_vira_colunas_com_ponto() -> None:
    resultado = _ler("aninhado.json")

    assert "endereco.cidade" in resultado.dados.columns
    assert resultado.dados["idade"].tolist() == [34, 27]


def test_json_de_colunas() -> None:
    assert _ler("colunas.json").dados.shape == (3, 2)


@pytest.mark.parametrize("conteudo", [b"{nao e json", b"[1, 2, 3]", b'{"a": 1}'])
def test_json_invalido(conteudo: bytes) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(conteudo, "dados.json", SEM_OPCOES)

    assert erro.value.codigo == "JSON_INVALIDO"


def test_xlsx_le_a_primeira_aba_e_lista_as_abas() -> None:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as planilha:
        pd.DataFrame({"x": [1, 2], "y": ["a", "b"]}).to_excel(
            planilha, sheet_name="dados", index=False
        )
        pd.DataFrame({"z": [3]}).to_excel(planilha, sheet_name="outra", index=False)

    resultado = ler_arquivo(buffer.getvalue(), "dados.xlsx", SEM_OPCOES)

    assert resultado.metadados.abas == ("dados", "outra")
    assert resultado.dados["x"].tolist() == [1, 2]


def test_xlsx_escolhe_a_aba() -> None:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as planilha:
        pd.DataFrame({"x": [1]}).to_excel(planilha, sheet_name="dados", index=False)
        pd.DataFrame({"z": [3, 4]}).to_excel(planilha, sheet_name="outra", index=False)

    resultado = ler_arquivo(buffer.getvalue(), "dados.xlsx", OpcoesLeitura(aba="outra"))

    assert list(resultado.dados.columns) == ["z"]


def _planilha(*linhas: list[object]) -> bytes:
    """XLSX com as linhas dadas a partir de A1 (None = célula vazia)."""
    buffer = io.BytesIO()
    pd.DataFrame(list(linhas)).to_excel(buffer, header=False, index=False, engine="openpyxl")
    return buffer.getvalue()


def test_xlsx_com_titulo_acha_o_cabecalho_e_tira_colunas_vazias() -> None:
    conteudo = _planilha(
        [None, "Pesquisa de satisfação", None],
        [None, None, None],
        [None, "nome", "idade"],
        [None, "Ana", 34],
        [None, "Beto", 41],
    )

    resultado = ler_arquivo(conteudo, "dados.xlsx", SEM_OPCOES)

    assert resultado.metadados.linha_cabecalho == 3
    assert list(resultado.dados.columns) == ["nome", "idade"]
    assert resultado.dados["idade"].tolist() == [34, 41]
    assert resultado.metadados.linhas_iniciais[0].celulas == ("Pesquisa de satisfação", "")
    assert resultado.metadados.linhas_iniciais[1].celulas == ()


def test_xlsx_com_linha_do_cabecalho_escolhida() -> None:
    conteudo = _planilha(["titulo", None], ["a", "b"], [1, 2])

    resultado = ler_arquivo(conteudo, "dados.xlsx", OpcoesLeitura(linha_cabecalho=0))

    assert list(resultado.dados.columns) == ["col_1", "col_2"]
    assert len(resultado.dados) == 3
    assert resultado.metadados.motivos["cabecalho"] == "Escolhido por você."


def test_xlsx_corrompido() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(b"isto nao e uma planilha", "dados.xlsx", SEM_OPCOES)

    assert erro.value.codigo == "ARQUIVO_ILEGIVEL"


def test_csv_com_titulo_pula_as_linhas_acima_do_cabecalho() -> None:
    resultado = _ler("com_titulo.csv")

    assert resultado.metadados.linha_cabecalho == 3
    assert resultado.metadados.motivos["cabecalho"] == (
        "A linha 3 é a primeira só com nomes; as linhas acima ficam de fora."
    )
    assert list(resultado.dados.columns) == ["nome", "idade", "nota"]
    assert resultado.dados["nota"].tolist() == [8.5, 7.0]


def test_linhas_iniciais_mostram_o_arquivo_como_esta() -> None:
    iniciais = _ler("com_titulo.csv").metadados.linhas_iniciais

    assert [linha.numero for linha in iniciais] == [1, 2, 3, 4, 5]
    assert iniciais[0].celulas == ("Pesquisa de satisfação 2026", "", "")
    assert iniciais[2].celulas == ("nome", "idade", "nota")


def test_linha_do_cabecalho_escolhida_vira_os_nomes() -> None:
    resultado = _ler("com_titulo.csv", OpcoesLeitura(linha_cabecalho=4))

    assert list(resultado.dados.columns) == ["Ana", "34", "8,5"]
    assert len(resultado.dados) == 1


def test_sem_cabecalho_com_titulo_le_tudo_como_dados() -> None:
    conteudo = b"Pesquisa\n\nsexo;peso\nF;58,2\nM;79,6\n"

    resultado = ler_arquivo(conteudo, "dados.txt", OpcoesLeitura(linha_cabecalho=0))

    assert list(resultado.dados.columns) == ["col_1", "col_2"]
    assert resultado.dados["col_1"].tolist() == ["Pesquisa", "sexo", "F", "M"]


@pytest.mark.parametrize("linha", [2, 9])
def test_linha_do_cabecalho_vazia_ou_fora_do_arquivo(linha: int) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(b"a;b\n\n1;2\n", "dados.txt", OpcoesLeitura(linha_cabecalho=linha))

    assert erro.value.codigo == "LINHA_CABECALHO_INVALIDA"


def test_json_nao_tem_linha_de_cabecalho() -> None:
    assert _ler("colunas.json").metadados.linha_cabecalho is None


def test_opcoes_do_usuario_sobrescrevem_a_deteccao() -> None:
    opcoes = OpcoesLeitura(separador=",", decimal=".", linha_cabecalho=1)

    resultado = ler_arquivo(b"a,b\n1.5,2\n", "dados.txt", opcoes)

    assert resultado.metadados.motivos["separador"] == "Escolhido por você."
    assert resultado.dados["a"].tolist() == [1.5]


@pytest.mark.parametrize("conteudo", [b"", b"   \n  "])
def test_arquivo_vazio(conteudo: bytes) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(conteudo, "dados.csv", SEM_OPCOES)

    assert erro.value.codigo == "ARQUIVO_VAZIO"


def test_so_cabecalho_tambem_e_vazio() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(b"a;b;c\n", "dados.txt", OpcoesLeitura(linha_cabecalho=1))

    assert erro.value.codigo == "ARQUIVO_VAZIO"


def test_uma_coluna_com_separador_suspeito_gera_aviso() -> None:
    opcoes = OpcoesLeitura(separador="|")

    resultado = ler_arquivo(b"a;b\n1;2\n3;4\n", "dados.txt", opcoes)

    assert [a.codigo for a in resultado.metadados.avisos] == ["UMA_COLUNA"]


@pytest.mark.parametrize("marcador", ["NA", "N/A", "NaN", "null", "None", "-", "?", "—", " "])
def test_marcadores_de_faltante(marcador: str) -> None:
    conteudo = f"cidade;n\nGoiânia;1\n{marcador};2\n".encode()

    resultado = ler_arquivo(conteudo, "dados.txt", SEM_OPCOES)

    assert resultado.dados["cidade"].isna().sum() == 1


def test_indice_e_o_numero_da_linha() -> None:
    assert _ler("virgula.csv").dados.index.tolist() == [1, 2, 3]


@pytest.mark.parametrize(
    ("nomes", "esperado"),
    [
        ([" idade ", "peso  kg"], ["idade", "peso kg"]),
        (["a", "a", "a"], ["a", "a_2", "a_3"]),
        (["", None], ["col_1", "col_2"]),
    ],
)
def test_padronizar_nomes(nomes: list[object], esperado: list[str]) -> None:
    assert padronizar_nomes(nomes) == esperado


def test_exemplo_pesquisa_saude() -> None:
    caminho = Path(__file__).resolve().parents[4] / "dados-exemplo" / "pesquisa_saude.txt"

    resultado = ler_arquivo(caminho.read_bytes(), caminho.name, SEM_OPCOES)

    assert (resultado.metadados.n_linhas, resultado.metadados.n_colunas) == (230, 8)
    assert resultado.metadados.motivos["separador"] == "Aparece 7 vezes em todas as linhas."
