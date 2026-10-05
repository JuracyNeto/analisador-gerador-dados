import pandas as pd
import pytest

from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.dominios.datasets.classificacao import (
    Classificacao,
    Limiares,
    classificar,
    classificar_tabela,
    ler_coluna,
)

LIMIARES = Limiares()


def _classificar(nome: str, valores: list[object]) -> Classificacao:
    return classificar(ler_coluna(nome, pd.Series(valores), ",", LIMIARES))


def test_coluna_vazia_e_ignorada() -> None:
    resultado = _classificar("obs", [None, None])

    assert resultado.tipo == TipoVariavel.IDENTIFICADOR
    assert resultado.motivo == "A coluna está vazia; foi ignorada."


@pytest.mark.parametrize("nome", ["id", "ID_cliente", "Código", "cpf", "CEP", "matrícula"])
def test_nome_de_codigo_vira_identificador(nome: str) -> None:
    resultado = _classificar(nome, ["1", "1", "2"])

    assert resultado.tipo == TipoVariavel.IDENTIFICADOR
    assert resultado.motivo == f"O nome da coluna indica um código ({nome})."


def test_idade_nao_e_confundida_com_id() -> None:
    assert _classificar("idade", [20, 30, 30, 40]).tipo == TipoVariavel.DISCRETA


def test_cep_numerico_sem_nome_de_codigo_vira_identificador_pelos_unicos() -> None:
    valores = [74000000 + i for i in range(25)]

    resultado = _classificar("local", valores)

    assert resultado.tipo == TipoVariavel.IDENTIFICADOR
    assert resultado.motivo == "Parece um código: 100% dos valores são únicos."


def test_decimais_unicos_nao_viram_identificador() -> None:
    valores = [1.5 + i / 100 for i in range(25)]

    assert _classificar("peso", valores).tipo == TipoVariavel.CONTINUA


@pytest.mark.parametrize(
    ("valores", "motivo"),
    [(["M", "F", "F"], "Tem só dois valores: F e M."), ([0, 1, 1], "Tem só dois valores: 0 e 1.")],
)
def test_dois_valores_vira_binaria(valores: list[object], motivo: str) -> None:
    resultado = _classificar("x", valores)

    assert (resultado.tipo, resultado.motivo) == (TipoVariavel.BINARIA, motivo)


def test_likert_vira_ordinal_com_a_ordem_da_escala() -> None:
    resultado = _classificar("satisfacao", ["bom", "ruim", "ótimo", "regular", "bom"])

    assert resultado.tipo == TipoVariavel.ORDINAL
    assert resultado.categorias_ordem == ("ruim", "regular", "bom", "ótimo")
    assert (
        resultado.motivo == "Os valores seguem uma escala conhecida: ruim < regular < bom < ótimo."
    )


def test_texto_sem_escala_vira_nominal() -> None:
    resultado = _classificar("cidade", ["Goiânia", "Anápolis", "Trindade", "Goiânia"])

    assert resultado.tipo == TipoVariavel.NOMINAL
    assert resultado.motivo == "São categorias sem ordem natural (3 categorias)."


def test_inteiros_com_poucos_valores_viram_discreta() -> None:
    resultado = _classificar("filhos", [0, 1, 2, 2, 3])

    assert resultado.tipo == TipoVariavel.DISCRETA
    assert resultado.motivo == "Números inteiros com 4 valores diferentes (contagem)."


def test_inteiros_com_muitos_valores_viram_continua() -> None:
    valores = [i % 40 for i in range(41)] + [0] * 5

    resultado = _classificar("idade", valores)

    assert resultado.tipo == TipoVariavel.CONTINUA
    assert resultado.motivo == "Inteiros com muitos valores diferentes (40); tratada como contínua."


def test_texto_com_virgula_decimal_vira_continua() -> None:
    resultado = _classificar("altura", ["1,62", "1,78", "1,58"])

    assert (resultado.tipo, resultado.motivo) == (
        TipoVariavel.CONTINUA,
        "Números com casas decimais.",
    )


def test_um_texto_entre_numeros_nao_muda_o_tipo() -> None:
    # 19 de 20 valores (95%) viram número: acima do limiar de 90% (D48).
    valores = [str(i % 10) for i in range(19)] + ["doze"]

    assert _classificar("filhos", valores).tipo == TipoVariavel.DISCRETA


def test_muitos_textos_entre_numeros_viram_nominal() -> None:
    valores = ["1", "2", "3", "doze", "treze", "1"]

    assert _classificar("filhos", valores).tipo == TipoVariavel.NOMINAL


def test_limiar_de_discreta_vem_da_configuracao() -> None:
    coluna = ler_coluna("n", pd.Series([1, 2, 3, 4]), ".", Limiares(discreta=3))

    assert classificar(coluna).tipo == TipoVariavel.CONTINUA


def test_classificar_tabela_descreve_cada_coluna() -> None:
    dados = pd.DataFrame(
        {"sexo": ["F", "M", None, "F"], "peso": [58.2, 79.6, 63.0, None]},
        index=pd.RangeIndex(1, 5),
    )

    tipos = classificar_tabela(dados, ".", LIMIARES)

    sexo = tipos["sexo"]
    assert (sexo.n_validos, sexo.n_faltantes, sexo.n_distintos) == (3, 1, 2)
    assert sexo.origem == OrigemTipo.AUTO
    assert sexo.contagens == {"F": 2, "M": 1}
    assert tipos["peso"].exemplos == ("58,2", "79,6", "63")
    assert tipos["peso"].contagens == {}
