"""Tabelas de frequência por tipo de variável (spec 04). Strategy: tipo → função."""

from collections.abc import Callable
from dataclasses import dataclass
from itertools import accumulate

import pandas as pd

from app.compartilhado.numeros import formatar_fixo, formatar_numero
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.classes import Agrupamento, Classe, agrupar
from app.dominios.analise.resultados import Amostra, LinhaFrequencia, TabelaFrequencia

SIMBOLO_CLASSE = "⊢"
PORCENTO = 100


@dataclass(frozen=True, slots=True)
class _Contagem:
    rotulo: str
    valor: float | str
    fi: int
    classe: Classe | None = None


def _linha(contagem: _Contagem, f_acum: int, n: int, acumular: bool) -> LinhaFrequencia:
    classe = contagem.classe
    return LinhaFrequencia(
        rotulo=contagem.rotulo,
        valor=contagem.valor,
        fi=contagem.fi,
        fri=contagem.fi / n,
        fr_pct=contagem.fi / n * PORCENTO,
        limite_inferior=classe.inferior if classe else None,
        limite_superior=classe.superior if classe else None,
        ponto_medio=classe.ponto_medio if classe else None,
        f_acum=f_acum if acumular else None,
        fr_acum=f_acum / n if acumular else None,
        fr_acum_pct=f_acum / n * PORCENTO if acumular else None,
    )


def _linhas(contagens: list[_Contagem], n: int, acumular: bool) -> tuple[LinhaFrequencia, ...]:
    acumuladas = accumulate(c.fi for c in contagens)
    return tuple(_linha(c, f, n, acumular) for c, f in zip(contagens, acumuladas, strict=True))


def _indice_modal(contagens: list[_Contagem]) -> int | None:
    if not contagens:
        return None
    maior = max(c.fi for c in contagens)
    return next(i for i, c in enumerate(contagens) if c.fi == maior)


def _tabela(amostra: Amostra, contagens: list[_Contagem], acumular: bool) -> TabelaFrequencia:
    motivo = None if acumular else textos.nao_se_aplica("acumulada", amostra.tipo, "acumulada")
    return TabelaFrequencia(
        tipo=amostra.tipo,
        linhas=_linhas(contagens, amostra.n, acumular),
        total=amostra.n,
        acumulada_aplicavel=acumular,
        motivo_acumulada=motivo,
        indice_modal=_indice_modal(contagens),
    )


def _por_frequencia(amostra: Amostra, _classes: int | None) -> TabelaFrequencia:
    """Nominal e binária: categorias da mais para a menos frequente, sem acumulada."""
    contagens = amostra.valores.value_counts()
    ordenadas = sorted(contagens.items(), key=lambda item: (-int(item[1]), str(item[0])))
    linhas = [_Contagem(str(c), str(c), int(fi)) for c, fi in ordenadas]
    return _tabela(amostra, linhas, acumular=False)


def ordem_completa(amostra: Amostra) -> list[str]:
    """Ordem da escala; categorias fora dela (não deveria haver) vão para o fim."""
    presentes = {str(v) for v in amostra.valores.unique()}
    extras = sorted(presentes - set(amostra.ordem))
    return [c for c in amostra.ordem if c in presentes] + extras


def _ordinal(amostra: Amostra, _classes: int | None) -> TabelaFrequencia:
    contagens = amostra.valores.astype(str).value_counts()
    linhas = [_Contagem(c, c, int(contagens[c])) for c in ordem_completa(amostra)]
    return _tabela(amostra, linhas, acumular=True)


def _discreta(amostra: Amostra, _classes: int | None) -> TabelaFrequencia:
    contagens = amostra.valores.value_counts().sort_index()
    pares = zip(contagens.index.tolist(), contagens.tolist(), strict=True)
    linhas = [_Contagem(formatar_numero(float(v)), float(v), int(fi)) for v, fi in pares]
    return _tabela(amostra, linhas, acumular=True)


def rotulo_classe(classe: Classe, casas: int) -> str:
    """Notação da spec 04: "10,0 ⊢ 20,0"."""
    inferior, superior = (
        formatar_fixo(classe.inferior, casas),
        formatar_fixo(classe.superior, casas),
    )
    return f"{inferior} {SIMBOLO_CLASSE} {superior}"


def _continua(amostra: Amostra, classes: int | None) -> TabelaFrequencia:
    agrupamento: Agrupamento = agrupar(amostra.valores, classes)
    linhas = [
        _Contagem(rotulo_classe(c, agrupamento.casas), c.ponto_medio, c.frequencia, c)
        for c in agrupamento.classes
    ]
    base = _tabela(amostra, linhas, acumular=True)
    return TabelaFrequencia(
        tipo=base.tipo,
        linhas=base.linhas,
        total=base.total,
        acumulada_aplicavel=True,
        indice_modal=base.indice_modal,
        k=agrupamento.k,
        k_sturges=agrupamento.k_sturges,
        h=agrupamento.h,
        metodo_classes="usuario" if agrupamento.metodo == "usuario" else "sturges",
    )


TABELAS: dict[TipoVariavel, Callable[[Amostra, int | None], TabelaFrequencia]] = {
    TipoVariavel.NOMINAL: _por_frequencia,
    TipoVariavel.BINARIA: _por_frequencia,
    TipoVariavel.ORDINAL: _ordinal,
    TipoVariavel.DISCRETA: _discreta,
    TipoVariavel.CONTINUA: _continua,
}


def tabela_frequencia(amostra: Amostra, classes: int | None = None) -> TabelaFrequencia:
    """fᵢ, frᵢ = fᵢ/n, fr% e, quando há ordem, Fᵢ = Σfⱼ e Frᵢ = Fᵢ/n."""
    return TABELAS[amostra.tipo](amostra, classes)


def contagens_por_categoria(amostra: Amostra) -> pd.Series:
    """Frequências na ordem em que a tabela mostra (usado por moda e separatrizes ordinais)."""
    tabela = tabela_frequencia(amostra)
    return pd.Series({linha.rotulo: linha.fi for linha in tabela.linhas})
