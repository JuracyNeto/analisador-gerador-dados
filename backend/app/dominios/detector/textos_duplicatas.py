"""Textos da R5, Duplicatas (spec 16, ADR 0005), com os formatadores de `textos.py`.

Saíram de `textos.py`, que passaria de 500 linhas.
"""

from collections.abc import Sequence

from app.compartilhado.numeros import formatar_inteiro
from app.compartilhado.textos import pluralizar, quantidade
from app.dominios.detector.duplicatas import ContraOAcaso
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso
from app.dominios.detector.textos import faixa_de_linhas, numero, p_em_palavras

SO_IDENTIFICADORES = "o arquivo só tem identificadores"
POUCAS_COLUNAS = "precisa de 2 colunas ou mais (fora os identificadores)"


def r05_texto_exemplo(linhas: Sequence[int], primeira: str) -> str:
    """ "Linhas 44 a 47: F · 34 · …" (as linhas são iguais: mostra uma só)."""
    return f"{faixa_de_linhas(linhas)}: {primeira}"


def r05_texto_exemplo_quase(linhas: Sequence[int], primeira: str) -> str:
    return f"{faixa_de_linhas(linhas)} (quase iguais): {primeira}"


def _iguais(k: int, grupos_quase: int) -> str:
    """ "iguais" ou, se algum grupo só é quase igual, "iguais ou quase iguais"."""
    igual = pluralizar(k, "igual", "iguais")
    return f"{igual} ou quase {igual}" if grupos_quase else igual


def r05_textos(copias: int, grupos_quase: int, seguidas: tuple[int, int] | None) -> TextosAviso:
    """ "Encontramos {k} linhas iguais (ou quase), {em_sequencia}." (spec 16)."""
    linhas = quantidade(copias, "linha", "linhas")
    outras = pluralizar(copias, "outra", "outras")
    sequencia = (
        f"; as linhas {seguidas[0]} a {seguidas[1]} são {_iguais(2, grupos_quase)} e seguidas"
        if seguidas
        else ""
    )
    return TextosAviso(
        titulo="Linhas iguais em sequência" if seguidas else "Linhas repetidas no arquivo",
        resumo=(
            f"Encontramos {linhas} {_iguais(copias, grupos_quase)} a {outras} do arquivo"
            f"{sequencia}."
        ),
        por_que=(
            "Cópias seguidas costumam surgir de 'copiar e colar'."
            if seguidas
            else "Linhas repetidas podem ter sido copiadas de outras partes do arquivo."
        ),
        pode_ser_normal="…são registros legítimos repetidos (ex.: a mesma compra).",
        o_que_fazer=(
            "Confira se essas linhas são registros diferentes; "
            "se forem cópias, remova os duplicados na etapa Limpeza."
        ),
    )


def r05_formula_quase(numericas: int) -> str:
    return (
        "Quase iguais: distância entre as linhas padronizadas < 0,01·√p "
        f"(p = {numericas} colunas numéricas, fora as vazias nas duas linhas) e as demais "
        "colunas iguais; contam quando passam do acaso, estimado pelos pares vizinhos na "
        "precisão de cada coluna"
    )


R05_FORMULA_IDENTICAS = "Só linhas idênticas"


R05_TESTES = {
    "iguais": (
        "Poisson: pares de linhas iguais × acaso (densidade local)",
        "par igual",
        "pares iguais",
    ),
    "quase": (
        "Poisson: pares quase iguais × acaso (densidade local)",
        "par quase igual",
        "pares quase iguais",
    ),
    "seguidas": (
        "Poisson: linhas iguais seguidas × acaso (ordem aleatória)",
        "trinca seguida",
        "trincas seguidas",
    ),
}


def r05_detalhes(
    copias: int, grupos: int, formula: str, tipo: str, acaso: ContraOAcaso
) -> DetalhesAviso:
    """Detalhes com a comparação com o acaso que justificou o aviso (D120)."""
    teste, singular, plural = R05_TESTES[tipo]
    return DetalhesAviso(
        medida="Linhas iguais ou quase iguais em todas as colunas (fora os identificadores)",
        valor=(
            f"{quantidade(copias, 'cópia', 'cópias')} em {quantidade(grupos, 'grupo', 'grupos')}"
            f" · {quantidade(acaso.observados, singular, plural)} "
            f"(o acaso daria {numero(acaso.esperados)})"
        ),
        limiar=(
            "Repetições além do acaso, p < 0,01 (atenção); "
            "3 linhas iguais seguidas, improváveis ao acaso (suspeita alta)"
        ),
        teste=teste,
        formula=formula,
        p_valor=acaso.p_valor,
        p_em_palavras=p_em_palavras(acaso.p_valor),
    )


def r05_ressalva(n: int, limite: int) -> tuple[str, str]:
    """(motivo, frase) das quase duplicatas não verificadas em arquivos grandes (D120)."""
    motivo = f"o arquivo tem {formatar_inteiro(n)} linhas e o limite é {formatar_inteiro(limite)}"
    return motivo, f"Quase duplicatas não verificadas: {motivo}."
