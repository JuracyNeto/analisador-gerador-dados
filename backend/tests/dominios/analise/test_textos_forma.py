import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise import textos_forma
from app.dominios.analise.resultados import (
    ClasseAssimetria,
    ClasseCurtose,
    Sentido,
    TesteAderencia,
)

SHAPIRO = TesteAderencia("Shapiro-Wilk", 0.99329, None, 0.399, compativel=True)
QUI = TesteAderencia("Qui-quadrado", 3.2, 4, 0.525, compativel=True)
REPROVADO = TesteAderencia("Shapiro-Wilk", 0.83, None, 0.0000001, compativel=False)


@pytest.mark.parametrize(
    ("classe", "sentido", "frase"),
    [
        (
            "simetrica",
            "direita",
            "Aproximadamente simétrica: a cauda direita é só um pouco mais longa.",
        ),
        ("simetrica", None, "Simétrica: as duas caudas têm o mesmo tamanho."),
        (
            "moderada",
            "direita",
            "Assimetria moderada à direita: há valores altos mais afastados do centro.",
        ),
        (
            "moderada",
            "esquerda",
            "Assimetria moderada à esquerda: há valores baixos mais afastados do centro.",
        ),
        (
            "forte",
            "direita",
            "Assimetria forte à direita: poucos valores muito altos esticam a cauda.",
        ),
        (
            "forte",
            "esquerda",
            "Assimetria forte à esquerda: poucos valores muito baixos esticam a cauda.",
        ),
    ],
)
def test_frase_da_assimetria(classe: ClasseAssimetria, sentido: Sentido | None, frase: str) -> None:
    assert textos_forma.frase_assimetria(classe, sentido) == frase


@pytest.mark.parametrize(
    ("classe", "inicio"),
    [
        ("mesocurtica", "Mesocúrtica:"),
        ("leptocurtica", "Leptocúrtica:"),
        ("platicurtica", "Platicúrtica:"),
    ],
)
def test_frase_da_curtose(classe: ClasseCurtose, inicio: str) -> None:
    assert textos_forma.frase_curtose(classe).startswith(inicio)


def test_frase_de_aderencia() -> None:
    assert (
        textos_forma.frase_aderencia("Normal", SHAPIRO)
        == "Os dados são compatíveis com a distribuição Normal."
    )
    assert (
        textos_forma.frase_aderencia("Binomial", REPROVADO)
        == "Os dados se afastam da distribuição Binomial."
    )


@pytest.mark.parametrize(
    ("teste", "texto"),
    [
        (SHAPIRO, "Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05"),
        (QUI, "Qui-quadrado: χ² = 3,2 · gl = 4 · p = 0,525 ≥ 0,05"),
        (REPROVADO, "Shapiro-Wilk: W = 0,83 · p < 0,001 < 0,05"),
    ],
)
def test_calculo_do_teste(teste: TesteAderencia, texto: str) -> None:
    assert textos_forma.calculo_teste(teste) == texto


def test_nao_se_aplica_ao_tipo() -> None:
    assert textos_forma.nao_se_aplica_ao_tipo(
        "binomial", TipoVariavel.CONTINUA, "binomial_continua"
    ) == (
        "Binomial não se aplica a quantitativas contínuas: "
        "precisa de contagens de sucessos em n tentativas."
    )


def test_nao_calculavel() -> None:
    assert (
        textos_forma.nao_calculavel("curtose", "poucos_4")
        == "Curtose não se aplica: precisa de pelo menos 4 valores."
    )


def test_frase_conjunta_completa() -> None:
    frase = textos_forma.frase_conjunta(
        ("simetrica", "direita"), "mesocurtica", ("Normal", SHAPIRO)
    )

    assert frase == (
        "Distribuição aproximadamente simétrica e mesocúrtica; compatível com a Normal (p = 0,399)."
    )


def test_frase_conjunta_com_partes() -> None:
    assert (
        textos_forma.frase_conjunta(("forte", "esquerda"), None, ("Normal", REPROVADO))
        == "Distribuição fortemente assimétrica à esquerda; se afasta da Normal (p < 0,001)."
    )
    assert (
        textos_forma.frase_conjunta(("moderada", "direita"), "leptocurtica", None)
        == "Distribuição moderadamente assimétrica à direita e leptocúrtica."
    )
    assert textos_forma.frase_conjunta(None, None, None) is None
