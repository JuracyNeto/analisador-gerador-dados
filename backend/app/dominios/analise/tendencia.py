"""Medidas de tendência central: média, mediana, moda, moda de Czuber e proporção (spec 05)."""

from typing import Literal

import pandas as pd

from app.compartilhado.numeros import formatar_inteiro, formatar_numero, formatar_percentual
from app.compartilhado.textos import juntar_lista, normalizar_texto
from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.frequencias import ordem_completa
from app.dominios.analise.resultados import (
    Amostra,
    Medida,
    Moda,
    TabelaFrequencia,
    Tendencia,
    nao_aplicavel,
)

SUCESSOS_PADRAO = frozenset({"1", "sim", "s", "true", "verdadeiro"})
VALORES_BIMODAL = 2


def media(amostra: Amostra) -> Medida:
    """x̄ = Σxᵢ / n."""
    if amostra.tipo == TipoVariavel.BINARIA:
        return nao_aplicavel(textos.nao_se_aplica("media", amostra.tipo, "media_binaria"))
    if amostra.tipo not in TIPOS_NUMERICOS:
        return nao_aplicavel(textos.nao_se_aplica("media", amostra.tipo, "media"))
    soma = float(amostra.valores.sum())
    valor = soma / amostra.n
    calculo = f"Σxᵢ / n = {formatar_numero(soma)} / {amostra.n} = {formatar_numero(valor)}"
    return Medida(valor, calculo=calculo, formula="media")


def _posicao_central(n: int) -> float:
    return (n + 1) / 2


def _mediana_ordinal(amostra: Amostra) -> Medida:
    """Categoria que contém a posição (n + 1)/2 na ordem da escala."""
    posicao = _posicao_central(amostra.n)
    contagens = amostra.valores.astype(str).value_counts()
    acumulada = 0
    for categoria in ordem_completa(amostra):
        acumulada += int(contagens.get(categoria, 0))
        if acumulada >= posicao:
            calculo = f"posição (n + 1) / 2 = {formatar_numero(posicao)} → {categoria}"
            return Medida(categoria, calculo=calculo, formula="mediana")
    return nao_aplicavel(textos.nao_se_aplica("mediana", amostra.tipo, "mediana"))


def mediana(amostra: Amostra) -> Medida:
    """Valor central dos dados ordenados; n par → média dos dois centrais."""
    if amostra.tipo == TipoVariavel.ORDINAL:
        return _mediana_ordinal(amostra)
    if amostra.tipo not in TIPOS_NUMERICOS:
        return nao_aplicavel(textos.nao_se_aplica("mediana", amostra.tipo, "mediana"))
    valor = float(amostra.valores.median())
    posicao = formatar_numero(_posicao_central(amostra.n))
    calculo = f"posição (n + 1) / 2 = {posicao} → {formatar_numero(valor)}"
    return Medida(valor, calculo=calculo, formula="mediana")


def _texto(valor: float | str) -> str:
    return formatar_numero(valor) if isinstance(valor, float) else valor


def _valor_da_moda(valor: object, numerica: bool) -> float | str:
    return float(str(valor)) if numerica else str(valor)


def moda(amostra: Amostra) -> Moda:
    """Valor(es) de maior frequência; amodal se todos aparecem igual."""
    contagens = amostra.valores.value_counts()
    maior = int(contagens.max())
    numerica = amostra.tipo in TIPOS_NUMERICOS
    modas = tuple(_valor_da_moda(v, numerica) for v in sorted(contagens[contagens == maior].index))
    vezes = f"{formatar_inteiro(maior)} {'vez' if maior == 1 else 'vezes'}"
    if len(contagens) > 1 and len(modas) == len(contagens):
        frase = "Não há moda: todos os valores aparecem o mesmo número de vezes."
        return Moda((), "amodal", frase)
    if len(modas) == 1:
        return Moda(modas, "unimodal", f"O valor mais frequente é {_texto(modas[0])} ({vezes}).")
    lista = juntar_lista([_texto(m) for m in modas])
    classificacao: Literal["bimodal", "multimodal"] = (
        "bimodal" if len(modas) == VALORES_BIMODAL else "multimodal"
    )
    return Moda(modas, classificacao, f"Há {len(modas)} modas: {lista} ({vezes} cada).")


def moda_czuber(amostra: Amostra, tabela: TabelaFrequencia) -> Medida:
    """Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h, na classe modal."""
    if amostra.tipo != TipoVariavel.CONTINUA or tabela.indice_modal is None or tabela.h is None:
        return nao_aplicavel(textos.nao_se_aplica("moda_czuber", amostra.tipo, "moda_czuber"))
    linhas, i = tabela.linhas, tabela.indice_modal
    modal = linhas[i]
    delta_1 = modal.fi - (linhas[i - 1].fi if i > 0 else 0)
    delta_2 = modal.fi - (linhas[i + 1].fi if i + 1 < len(linhas) else 0)
    inferior = modal.limite_inferior or 0.0
    if delta_1 + delta_2 == 0:
        return Medida(modal.ponto_medio, calculo="Δ₁ + Δ₂ = 0: usamos o ponto médio da classe.")
    valor = inferior + delta_1 / (delta_1 + delta_2) * tabela.h
    calculo = (
        f"Mo = {formatar_numero(inferior)} + [{delta_1} / ({delta_1} + {delta_2})] · "
        f"{formatar_numero(tabela.h)} = {formatar_numero(valor)}"
    )
    return Medida(valor, calculo=calculo, formula="moda_czuber")


def sucesso_padrao(valores: pd.Series) -> str:
    """1, sim, s, true ou verdadeiro; senão a categoria menos frequente (spec 05)."""
    categorias = sorted(str(v) for v in valores.unique())
    conhecida = next((c for c in categorias if normalizar_texto(c) in SUCESSOS_PADRAO), None)
    if conhecida is not None:
        return conhecida
    contagens = valores.astype(str).value_counts()
    return min(categorias, key=lambda c: (int(contagens[c]), c))


def proporcao(amostra: Amostra, sucesso: str | None) -> Medida:
    """p = nº de sucessos / n (só para binárias)."""
    if amostra.tipo != TipoVariavel.BINARIA:
        return nao_aplicavel(textos.nao_se_aplica("proporcao", amostra.tipo, "proporcao"))
    textos_validos = amostra.valores.astype(str)
    escolhida = sucesso if sucesso in set(textos_validos) else sucesso_padrao(textos_validos)
    sucessos = int((textos_validos == escolhida).sum())
    p = sucessos / amostra.n
    return Medida(
        p,
        calculo=f"p = {sucessos} / {amostra.n} = {formatar_numero(p)}",
        interpretacao=f'{formatar_percentual(p * 100)} dos valores são "{escolhida}".',
        formula="proporcao",
    )


def tendencia(amostra: Amostra, tabela: TabelaFrequencia, sucesso: str | None) -> Tendencia:
    return Tendencia(
        media=media(amostra),
        mediana=mediana(amostra),
        moda=moda(amostra),
        moda_czuber=moda_czuber(amostra, tabela),
        proporcao=proporcao(amostra, sucesso),
    )
