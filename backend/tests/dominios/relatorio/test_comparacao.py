import pytest

from app.dominios.relatorio.comparacao import linha_comparacao


@pytest.mark.parametrize(
    ("linha", "esperada"),
    [
        (("n", 227.0, 500.0, 273.0), ("n", "227", "500", "+273")),
        (("Média", 70.31, 70.31, 0.0), ("Média", "70,31", "70,31", "0,00")),
        (("Média", 70.3, 70.31, 0.000001), ("Média", "70,3", "70,31", "0,00")),
        (("Assimetria", 0.123, 0.0951, -0.0279), ("Assimetria", "0,123", "0,0951", "−0,0279")),
        (("Mínimo", -1.5, -1.2, 0.3), ("Mínimo", "−1,5", "−1,2", "+0,3")),
        (("fr% · F", 52.0, 50.4, -1.6), ("fr% · F", "52,0%", "50,4%", "−1,6 p.p.")),
        (("Média", None, 70.0, None), ("Média", "—", "70", "—")),
    ],
)
def test_linha_comparacao_como_na_tela_6(
    linha: tuple[str, float | None, float | None, float | None], esperada: tuple[str, ...]
) -> None:
    assert linha_comparacao(*linha) == esperada
