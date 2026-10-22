import numpy as np

from app.dominios.detector.exemplos import (
    MAX_LINHAS_BLOCO,
    MAX_LINHAS_EXEMPLO,
    exemplo_de_valores,
    exemplo_do_bloco,
    exemplo_do_trecho,
    trecho_concentrado,
)


def test_trecho_aceita_ate_duas_linhas_sem_marca_no_meio() -> None:
    marcas = np.array([False, True, True, False, True, False, False, False, True])

    assert trecho_concentrado(marcas) == slice(1, 5)


def test_trecho_escolhe_o_grupo_com_mais_marcas() -> None:
    marcas = np.array([True] + [False] * 5 + [True, True, False, True])

    assert trecho_concentrado(marcas) == slice(6, 10)


def test_sem_marcas_o_trecho_e_vazio() -> None:
    assert trecho_concentrado(np.zeros(4, dtype=bool)) == slice(0, 0)


def test_exemplo_do_trecho_traz_linhas_e_valores_do_trecho() -> None:
    linhas = np.arange(118, 142)
    valores = np.where(np.isin(linhas, np.arange(120, 139)), 70.0, 71.3)
    marcas = valores == 70.0

    exemplo = exemplo_do_trecho(linhas, valores, marcas)

    assert exemplo.linhas == tuple(range(120, 139))
    assert exemplo.valores[:2] == ("70", "70")
    assert exemplo.texto == "Linhas 120 a 138: 70, 70, 70, 70, 70, 70, 70, 70…"


def test_exemplo_fica_em_20_linhas_no_maximo() -> None:
    exemplo = exemplo_de_valores(np.arange(1, 101), np.arange(100.0))

    assert len(exemplo.linhas) == len(exemplo.valores) == MAX_LINHAS_EXEMPLO
    assert exemplo.total_linhas == 100


def test_bloco_vai_inteiro_ate_caber_num_pedido_do_ver_na_tabela() -> None:
    """Com 3 linhas de contexto de cada lado, 194 linhas cabem nas 200 da API (D172)."""
    inteiro = exemplo_do_bloco(np.arange(231, 261), np.full(30, 70.0))
    cortado = exemplo_do_bloco(np.arange(1, 301), np.full(300, 70.0))

    assert inteiro.linhas == tuple(range(231, 261))
    assert inteiro.total_linhas == 30
    assert MAX_LINHAS_BLOCO + 2 * 3 == 200
    assert cortado.linhas == tuple(range(1, MAX_LINHAS_BLOCO + 1))
    assert cortado.total_linhas == 300
