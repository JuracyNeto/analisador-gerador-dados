import pytest

from app.dominios.datasets.escalas_ordinais import ordenar_por_escala


@pytest.mark.parametrize(
    ("valores", "ordem"),
    [
        (["bom", "ruim", "ótimo", "regular"], ("ruim", "regular", "bom", "ótimo")),
        (["Alto", "baixo", "Médio"], ("baixo", "Médio", "Alto")),
        (["pós", "médio", "fundamental", "superior"], ("fundamental", "médio", "superior", "pós")),
        (["G", "P", "M"], ("P", "M", "G")),
        (["grave", "leve"], ("leve", "grave")),
        (["3º", "1º", "2º"], ("1º", "2º", "3º")),
        (["sempre", "nunca", "às vezes"], ("nunca", "às vezes", "sempre")),
    ],
)
def test_ordena_pela_escala_conhecida(valores: list[str], ordem: tuple[str, ...]) -> None:
    assert ordenar_por_escala(valores) == ordem


@pytest.mark.parametrize("valores", [["Goiânia", "Anápolis"], ["bom", "azul"], ["1º", "segundo"]])
def test_sem_escala_devolve_none(valores: list[str]) -> None:
    assert ordenar_por_escala(valores) is None
