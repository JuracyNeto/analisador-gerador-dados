from app.dominios.detector.registro import REGRAS, regras_pedidas


def test_regras_em_ordem_de_codigo_e_sem_repeticao() -> None:
    numeros = [int(regra.codigo.removeprefix("R")) for regra in REGRAS]

    assert numeros == sorted(set(numeros))


def test_sem_codigos_roda_todas_as_regras() -> None:
    assert regras_pedidas(None) == REGRAS
    assert regras_pedidas(()) == REGRAS
