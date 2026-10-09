"""Monta a análise de um par de colunas: correlação, regressão, faixa de X e fórmulas (spec 10)."""

from dataclasses import replace

from app.dominios.analise import textos_bivariada
from app.dominios.analise.correlacao import classificar, pearson, spearman, teste_t
from app.dominios.analise.formulas import formulas_usadas
from app.dominios.analise.regressao import regressao
from app.dominios.analise.resultados_bivariada import Bivariada, Faixa, Par

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
