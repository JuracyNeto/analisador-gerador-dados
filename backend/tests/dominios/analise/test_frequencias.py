import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.frequencias import tabela_frequencia
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra


def test_nominal_ordena_por_frequencia_e_nao_acumula(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "b", "c", "c", "c"]))

    assert [(linha.rotulo, linha.fi) for linha in tabela.linhas] == [("c", 3), ("b", 2), ("a", 1)]
    assert tabela.linhas[0].fri == 0.5
    assert tabela.linhas[0].fr_pct == 50
    assert tabela.linhas[0].f_acum is None
    assert tabela.acumulada_aplicavel is False
    assert tabela.motivo_acumulada == (
        "Frequência acumulada não se aplica a qualitativas nominais: "
        'as categorias não têm ordem para somar "até aqui".'
    )
    assert (tabela.total, tabela.indice_modal) == (6, 0)


def test_ordinal_segue_a_escala_e_acumula(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(
        TipoVariavel.ORDINAL, ["bom", "ruim", "bom", "ótimo"], ESCALA_SATISFACAO
    )

    tabela = tabela_frequencia(amostra)

    assert [(linha.rotulo, linha.fi, linha.f_acum) for linha in tabela.linhas] == [
        ("ruim", 1, 1),
        ("bom", 2, 3),
        ("ótimo", 1, 4),
    ]
    assert tabela.linhas[-1].fr_acum == 1
    assert tabela.indice_modal == 1


def test_discreta_em_ordem_crescente(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.DISCRETA, [3.0, 1.0, 2.0, 3.0, 2.0, 3.0]))

    assert [(linha.rotulo, linha.fi, linha.f_acum) for linha in tabela.linhas] == [
        ("1", 1, 1),
        ("2", 2, 3),
        ("3", 3, 6),
    ]
    assert tabela.linhas[1].fr_acum_pct == pytest.approx(50)


def test_continua_em_classes_com_notacao_da_spec(criar_amostra: CriarAmostra) -> None:
    valores = [2.0, 3.5, 4.0, 5.5, 6.0, 7.5, 8.0, 9.5, 10.0, 11.5]

    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, valores))

    primeira = tabela.linhas[0]
    assert primeira.rotulo == "2,0 ⊢ 3,9"
    assert (primeira.limite_inferior, primeira.limite_superior) == (2.0, 3.9)
    assert primeira.ponto_medio == pytest.approx(2.95)
    assert (tabela.k, tabela.k_sturges, tabela.h, tabela.metodo_classes) == (5, 5, 1.9, "sturges")
    assert tabela.linhas[-1].f_acum == 10


def test_continua_com_classes_do_usuario(criar_amostra: CriarAmostra) -> None:
    valores = [2.0, 3.5, 4.0, 5.5, 6.0, 7.5, 8.0, 9.5, 10.0, 11.5]

    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, valores), classes=3)

    assert (tabela.k, tabela.metodo_classes) == (3, "usuario")
    assert tabela.indice_modal == 1


def test_binaria_mostra_as_duas_categorias(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.BINARIA, ["F", "M", "M"]))

    assert [linha.rotulo for linha in tabela.linhas] == ["M", "F"]
    assert tabela.acumulada_aplicavel is False
