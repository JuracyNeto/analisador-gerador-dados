import pytest

from app.dominios.gerador import formulas
from app.dominios.gerador.estrategias.base import Metodo
from app.dominios.gerador.textos import NOMES_METODOS


@pytest.mark.parametrize(
    ("metodo", "chaves"),
    [
        ("normal", ["normal", "reescala"]),
        ("kde", ["kde", "reescala"]),
        ("normal_inteira", ["normal_inteira", "reescala"]),
        ("poisson", ["poisson"]),
        ("empirica", ["empirica"]),
        ("bernoulli", ["bernoulli"]),
        ("frequencias", ["frequencias"]),
    ],
)
def test_formulas_do_metodo_univariado(metodo: Metodo, chaves: list[str]) -> None:
    """A reescala entra só onde a spec 11 a aplica (Normal, KDE e a discreta em parâmetros)."""
    assert [f.chave for f in formulas.formulas_univariadas(metodo)] == chaves


def test_todo_metodo_tem_formula_com_latex_e_texto() -> None:
    for metodo in NOMES_METODOS:
        formula = formulas.FORMULAS[metodo]
        assert formula.nome
        assert formula.latex
        assert formula.texto


def test_bivariado_com_e_sem_ajuste_exato() -> None:
    assert [f.chave for f in formulas.FORMULAS_BIVARIADO] == ["cholesky"]
    assert [f.chave for f in formulas.FORMULAS_BIVARIADO_EXATO] == ["cholesky", "ajuste_exato"]
