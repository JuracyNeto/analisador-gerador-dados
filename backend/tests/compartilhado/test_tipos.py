from app.compartilhado.tipos import (
    TIPOS_AUXILIARES,
    TIPOS_CATEGORICOS,
    TIPOS_NUMERICOS,
    TipoVariavel,
)


def test_data_e_identificador_sao_auxiliares() -> None:
    assert frozenset({TipoVariavel.IDENTIFICADOR, TipoVariavel.DATA}) == TIPOS_AUXILIARES


def test_auxiliares_nao_sao_numericos_nem_categoricos() -> None:
    assert not TIPOS_AUXILIARES & (TIPOS_NUMERICOS | TIPOS_CATEGORICOS)
