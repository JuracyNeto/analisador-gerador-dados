"""Monta a análise de um par de colunas: correlação, regressão, faixa de X e fórmulas (spec 10)."""

from dataclasses import replace

import pandas as pd

from app.dominios.analise import erros, textos_bivariada
from app.dominios.analise.correlacao import classificar, pearson, spearman, teste_t
from app.dominios.analise.formulas import formulas_usadas
from app.dominios.analise.regressao import prever, regressao
from app.dominios.analise.resultados_bivariada import Bivariada, Faixa, Par, Previsao

MIN_PARES = 3
MIN_DISTINTOS = 2  # com um valor só não há variação

CHAVES_FORMULAS: list[str | None] = [
    "pearson",
    "teste_t_correlacao",
    "spearman",
    "regressao",
    "r2",
    "erro_padrao_estimativa",
    "residuo",
]


def analisar_par(par: Par) -> Bivariada:
    """Pearson (com teste t e Spearman ao lado), reta Ŷ = a + bX e interpretações."""
    x, y = par.valores_x, par.valores_y
    r = pearson(x, y)
    valor_r = float(r.valor) if isinstance(r.valor, float) else 0.0
    forca, sentido = classificar(valor_r)
    r = replace(r, interpretacao=textos_bivariada.frase_forca(forca, sentido, par.x, par.y))
    significancia = teste_t(valor_r, len(x))
    reta = regressao(x, y, (par.x, par.y))
    interpretacoes = (r.interpretacao, significancia.interpretacao, reta.r2.interpretacao)
    return Bivariada(
        x=par.x,
        y=par.y,
        n=len(x),
        n_descartados=par.n_descartados,
        pearson=r,
        teste_t=significancia,
        spearman=spearman(x, y),
        forca=forca,
        sentido=sentido,
        regressao=reta,
        faixa_x=Faixa(float(x.min()), float(x.max())),
        interpretacoes=tuple(frase for frase in interpretacoes if frase),
        formulas=formulas_usadas(CHAVES_FORMULAS),
    )


def montar_par(x: str, y: str, serie_x: pd.Series, serie_y: pd.Series) -> Par:
    """Só as linhas com X e Y (pelo número da linha, D49); n ≥ 3 e as duas com variação."""
    if x == y:
        raise erros.colunas_iguais()
    juntos = pd.concat([serie_x, serie_y], axis="columns", keys=[x, y]).dropna()
    if len(juntos) < MIN_PARES:
        raise erros.poucos_pares(len(juntos), x, y)
    for nome in (x, y):
        if juntos[nome].nunique() < MIN_DISTINTOS:
            raise erros.sem_variacao(nome)
    return Par(
        x,
        y,
        juntos[x].to_numpy(dtype="float64"),
        juntos[y].to_numpy(dtype="float64"),
        n_descartados=len(serie_x) - len(juntos),
    )


def prever_no_par(par: Par, valor: float) -> Previsao:
    """ŷ = a + b·x com a reta do par; avisa quando x sai da faixa observada."""
    reta = regressao(par.valores_x, par.valores_y, (par.x, par.y))
    faixa = Faixa(float(par.valores_x.min()), float(par.valores_x.max()))
    return prever(reta.a, reta.b, valor, faixa, (par.x, par.y))
