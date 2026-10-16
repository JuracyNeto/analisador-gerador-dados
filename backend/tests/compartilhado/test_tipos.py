from app.compartilhado.tipos import (
    ORDEM_SEVERIDADE,
    TIPOS_AUXILIARES,
    TIPOS_CATEGORICOS,
    TIPOS_NUMERICOS,
    Severidade,
    TipoVariavel,
)


def test_data_e_identificador_sao_auxiliares() -> None:
    assert frozenset({TipoVariavel.IDENTIFICADOR, TipoVariavel.DATA}) == TIPOS_AUXILIARES


def test_auxiliares_nao_sao_numericos_nem_categoricos() -> None:
    assert not TIPOS_AUXILIARES & (TIPOS_NUMERICOS | TIPOS_CATEGORICOS)


def test_ordem_de_severidade_vai_da_mais_alta_para_a_informativa() -> None:
    assert ORDEM_SEVERIDADE == (Severidade.ALTA, Severidade.ATENCAO, Severidade.INFO)


def test_severidade_usa_os_valores_da_api() -> None:
    assert [s.value for s in Severidade] == ["info", "atencao", "alta"]
