"""Exporta as fórmulas dos catálogos do app para o relatório final (D169: fonte única).

As mesmas fórmulas da tela, do apêndice do relatório HTML e dos detalhes do detector, em
Markdown com blocos ```math (o GitHub desenha a fórmula; com `$$…$$`, o Markdown dele tiraria
a barra de `\\#`, `\\,` e `\\%`) e o texto de reserva.

Uso (em backend/): python scripts/exportar_formulas.py [--saida ../docs/relatorio-final/formulas.md]
"""

import argparse
from collections.abc import Iterable
from pathlib import Path

from app.dominios.analise.servico import FORMULAS as FORMULAS_ANALISE
from app.dominios.analise.servico import Formula
from app.dominios.detector.servico import FormulasRegra, formulas_das_regras
from app.dominios.gerador.servico import FORMULAS as FORMULAS_GERADOR

SAIDA = Path(__file__).resolve().parents[2] / "docs" / "relatorio-final" / "formulas.md"

INICIO_DOS_GRUPOS = {
    "frequencia_relativa": "Frequências",
    "media": "Tendência central",
    "quantil": "Separatrizes",
    "amplitude": "Dispersão",
    "assimetria": "Forma e distribuições",
    "pearson": "Correlação e regressão",
}
"""Primeira fórmula de cada grupo no catálogo da análise, que segue a ordem das specs 04–10."""

CABECALHO = """# Fórmulas

> Gerado por `backend/scripts/exportar_formulas.py` a partir dos catálogos do app \
(`analise/formulas.py`, `gerador/formulas.py` e `detector/formulas.py`): são as mesmas \
fórmulas da tela, do apêndice do relatório HTML e dos detalhes do detector. Não edite à mão; \
para refazer, rode `python scripts/exportar_formulas.py` em `backend/`.

Cada fórmula aparece com o nome, a forma matemática e o texto que o app mostra quando a \
fórmula não pode ser desenhada (por exemplo, no relatório aberto sem internet).
"""

INTRODUCAO_DETECTOR = """\
As regras do detector mostram estas fórmulas em texto nos detalhes técnicos de cada alerta, \
com os valores do alerta no lugar de k, n, p₀ e do medcouple. Os limiares de cada regra estão \
na seção 9 do relatório final e na spec 12.
"""


def grupos_da_analise() -> list[tuple[str, list[Formula]]]:
    """O catálogo da análise em grupos, cada um a partir da sua primeira fórmula."""
    grupos: list[tuple[str, list[Formula]]] = []
    for chave, formula in FORMULAS_ANALISE.items():
        if chave in INICIO_DOS_GRUPOS:
            grupos.append((INICIO_DOS_GRUPOS[chave], []))
        grupos[-1][1].append(formula)
    return grupos


def _formula(formula: Formula) -> str:
    return f"### {formula.nome}\n\n```math\n{formula.latex}\n```\n\nEm texto: `{formula.texto}`\n"


def _grupo(titulo: str, formulas: Iterable[Formula]) -> str:
    return "\n".join([f"## {titulo}\n", *(_formula(formula) for formula in formulas)])


def _regra(regra: FormulasRegra) -> str:
    itens = "".join(f"- `{formula}`\n" for formula in regra.formulas)
    return f"### {regra.codigo} · {regra.nome}\n\n{itens}"


def texto_das_formulas() -> str:
    detector = "\n".join(
        ["## Detector\n", INTRODUCAO_DETECTOR, *(_regra(r) for r in formulas_das_regras())]
    )
    partes = [
        CABECALHO,
        *(_grupo(titulo, formulas) for titulo, formulas in grupos_da_analise()),
        _grupo("Gerador", FORMULAS_GERADOR.values()),
        detector,
    ]
    return "\n".join(partes)


def gravar(saida: Path) -> Path:
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto_das_formulas())
    return saida


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta as fórmulas para o relatório final.")
    parser.add_argument("--saida", type=Path, default=SAIDA)
    print(f"Gravado {gravar(parser.parse_args().saida)}")


if __name__ == "__main__":
    main()
