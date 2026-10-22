import pytest

from app.dominios.datasets import frases_limpeza as frases


@pytest.mark.parametrize(
    ("frase", "esperado"),
    [
        (frases.duplicadas_removidas(1500), "Removemos 1.500 linhas duplicadas."),
        (frases.vazias_removidas(1200, "peso"), "Removemos 1.200 linhas sem valor em peso."),
        (frases.grafias_unificadas(1001, "cidade"), "Unificamos 1.001 grafias de cidade."),
        (frases.textos_marcados(2500, "nota"), "Marcamos 2.500 textos de nota como faltantes."),
    ],
)
def test_contagens_com_ponto_de_milhar(frase: str, esperado: str) -> None:
    assert frase == esperado
