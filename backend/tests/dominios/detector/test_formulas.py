"""Catálogo das fórmulas do detector (D169): cada regra tem as suas e os detalhes vêm dele."""

import re
from string import Formatter

import pytest
from fastapi.testclient import TestClient

from app.dominios.detector import formulas, servico
from app.dominios.detector.registro import REGRAS


def _padrao(codigo: str) -> re.Pattern[str]:
    """Uma ou mais fórmulas da regra, separadas por " · "; cada campo aceita qualquer valor."""
    opcoes = "|".join(
        "".join(
            re.escape(literal) + ("" if campo is None else ".+?")
            for literal, campo, _, _ in Formatter().parse(formula)
        )
        for formula in formulas.FORMULAS_REGRAS[codigo]
    )
    return re.compile(f"(?:{opcoes})(?:{re.escape(formulas.SEPARADOR)}(?:{opcoes}))*")


def test_cada_regra_do_registro_tem_formulas_no_catalogo() -> None:
    assert list(formulas.FORMULAS_REGRAS) == [regra.codigo for regra in REGRAS]
    assert all(formulas.FORMULAS_REGRAS.values())


@pytest.mark.parametrize("arquivo", ["alturas_plantadas.txt", "vendas_correlacao_puxada.txt"])
def test_formula_dos_detalhes_vem_do_catalogo_da_regra(cliente: TestClient, arquivo: str) -> None:
    criado = cliente.post("/api/datasets/exemplo", params={"arquivo": arquivo}).json()
    avisos = cliente.get(f"/api/datasets/{criado['dataset_id']}/detector").json()["avisos"]

    assert avisos
    for aviso in avisos:
        assert _padrao(aviso["regra"]).fullmatch(aviso["detalhes"]["formula"]), aviso["regra"]


def test_formulas_genericas_trocam_os_valores_pelos_simbolos() -> None:
    assert formulas.genericas("R4") == ("P(X ≥ k), X ~ Binomial(n; p₀)",)
    assert formulas.genericas("R7")[2].startswith("MC = medcouple da coluna; com MC > 0")
    genericas = [f for codigo in formulas.FORMULAS_REGRAS for f in formulas.genericas(codigo)]
    assert not any("{" in formula for formula in genericas)


def test_fachada_lista_as_formulas_de_cada_regra_na_ordem_do_registro() -> None:
    regras = servico.formulas_das_regras()

    assert [regra.codigo for regra in regras] == [regra.codigo for regra in REGRAS]
    assert (regras[0].nome, regras[0].formulas) == (
        "Bloco alinhado",
        (formulas.DISTANCIA_MEDIAS, formulas.DISTANCIA_DESVIOS),
    )
    assert regras[3].formulas == formulas.genericas("R4")
