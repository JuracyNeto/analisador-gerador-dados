from app.dominios.detector.registro import REGRAS, regras_pedidas


def test_regras_em_ordem_de_codigo_e_sem_repeticao() -> None:
    numeros = [int(regra.codigo.removeprefix("R")) for regra in REGRAS]

    assert numeros == sorted(set(numeros))


def test_sem_codigos_roda_todas_as_regras() -> None:
    assert regras_pedidas(None) == REGRAS
    assert regras_pedidas(()) == REGRAS


def test_codigos_pedidos_filtram_na_ordem_do_registro() -> None:
    pedidas = regras_pedidas(("R9", "R7"))

    assert [regra.codigo for regra in pedidas] == [
        regra.codigo for regra in REGRAS if regra.codigo in {"R7", "R9"}
    ]


def test_codigo_sem_regra_implementada_nao_roda_nada() -> None:
    assert regras_pedidas(("R99",)) == ()
