"""Ações de limpeza sobre a versão atual, na ordem da spec 03, com log em frases."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.series import converter_para_numero
from app.compartilhado.tipos import TIPOS_NUMERICOS
from app.dominios.datasets import erros
from app.dominios.datasets import frases_limpeza as frases
from app.dominios.datasets.diagnostico import (
    Limites,
    colunas_comparaveis,
    faixa_da_coluna,
    grupos_de_grafias,
)
from app.dominios.datasets.modelos import Celula, EntradaLog, TipoColuna
from app.dominios.datasets.tabela import celula

ORDEM_PROBLEMAS = ("inconsistencia", "tipo_misto", "duplicados", "fora_de_faixa", "faltantes")
MANTER = "manter"
VAZIO = "vazio"


@dataclass(frozen=True, slots=True)
class AcaoLimpeza:
    """O que fazer com um problema; `coluna`, `valor`, `limites` e `grupo` conforme a ação."""

    problema: str
    acao: str
    coluna: str | None = None
    valor: Celula = None
    limites: Limites | None = None
    grupo: str | None = None


@dataclass(frozen=True, slots=True, eq=False)
class _Contexto:
    dados: pd.DataFrame
    tipos: Mapping[str, TipoColuna]
    decimal: str | None


@dataclass(frozen=True, slots=True, eq=False)
class _Efeito:
    dados: pd.DataFrame
    linhas: tuple[int, ...]
    antes: str
    depois: str
    frase: str


@dataclass(frozen=True, slots=True, eq=False)
class ResultadoAcoes:
    dados: pd.DataFrame
    log: tuple[EntradaLog, ...]
    colunas_alteradas: frozenset[str]


type _Manipulador = Callable[[_Contexto, AcaoLimpeza], _Efeito]


def _linhas(mascara: pd.Series) -> tuple[int, ...]:
    return tuple(int(i) for i in mascara[mascara].index.tolist())


def _coluna(ctx: _Contexto, acao: AcaoLimpeza) -> str:
    if acao.coluna is None or acao.coluna not in ctx.dados.columns:
        raise erros.acao_incompativel(acao.coluna, "informe uma coluna que exista.")
    return acao.coluna


def _numeros(ctx: _Contexto, coluna: str) -> pd.Series:
    if ctx.tipos[coluna].tipo not in TIPOS_NUMERICOS:
        raise erros.acao_incompativel(coluna, "ela só vale para colunas numéricas.")
    return converter_para_numero(ctx.dados[coluna], ctx.decimal)


def _no_formato_do_arquivo(valor: Celula, decimal: str | None) -> Celula:
    """Número como texto no formato do arquivo, para colunas que ainda guardam texto."""
    if not isinstance(valor, float | int) or isinstance(valor, bool):
        return valor
    texto = str(int(valor)) if float(valor).is_integer() else repr(float(valor))
    return texto.replace(".", ",") if decimal == "," else texto


def _substituir(
    serie: pd.Series, mascara: pd.Series, novos: object, decimal: str | None
) -> pd.Series:
    """Troca os valores marcados mantendo o tipo da coluna (número ou texto)."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie.mask(mascara, novos)
    if isinstance(novos, pd.Series):
        return serie.mask(mascara, novos.map(lambda v: _no_formato_do_arquivo(v, decimal)))
    return serie.mask(mascara, _no_formato_do_arquivo(celula(novos), decimal))


def _com_coluna(ctx: _Contexto, coluna: str, serie: pd.Series) -> pd.DataFrame:
    dados = ctx.dados.copy()
    dados[coluna] = serie
    return dados


def _remocao(ctx: _Contexto, mascara: pd.Series, frase: str) -> _Efeito:
    restantes = ctx.dados[~mascara]
    antes, depois = f"{len(ctx.dados)} linhas", f"{len(restantes)} linhas"
    return _Efeito(restantes, _linhas(mascara), antes, depois, frase)


def _texto(valor: Celula) -> str:
    if isinstance(valor, float | int) and not isinstance(valor, bool):
        return formatar_numero(float(valor))
    return str(valor)


# Faltantes ---------------------------------------------------------------------------------


def _remover_vazias(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    vazias = ctx.dados[coluna].isna()
    return _remocao(ctx, vazias, frases.vazias_removidas(int(vazias.sum()), coluna))


def _preencher(ctx: _Contexto, coluna: str, valor: Celula, descricao: str) -> _Efeito:
    serie = ctx.dados[coluna]
    vazias = serie.isna()
    novo = _substituir(serie, vazias, valor, ctx.decimal)
    frase = frases.faltantes_preenchidos(int(vazias.sum()), coluna, descricao)
    return _Efeito(_com_coluna(ctx, coluna, novo), _linhas(vazias), VAZIO, _texto(valor), frase)


def _preencher_media(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    media = float(_numeros(ctx, coluna).mean())
    return _preencher(ctx, coluna, media, f"a média ({formatar_numero(media)})")


def _preencher_mediana(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    mediana = float(_numeros(ctx, coluna).median())
    return _preencher(ctx, coluna, mediana, f"a mediana ({formatar_numero(mediana)})")


def _preencher_moda(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    modas = ctx.dados[coluna].dropna().mode()
    if modas.empty:
        raise erros.acao_incompativel(coluna, "a coluna não tem valores para calcular a moda.")
    moda = celula(modas.iloc[0])
    return _preencher(ctx, coluna, moda, f"a moda ({_texto(moda)})")


def _valor_informado(ctx: _Contexto, coluna: str, valor: Celula) -> Celula:
    if valor is None or valor == "":
        raise erros.acao_incompativel(coluna, "informe o valor para preencher.")
    if ctx.tipos[coluna].tipo not in TIPOS_NUMERICOS:
        return valor
    numero = converter_para_numero(pd.Series([valor]), ctx.decimal).iloc[0]
    if pd.isna(numero):
        raise erros.acao_incompativel(coluna, "o valor precisa ser um número.")
    return float(numero)


def _preencher_valor(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    valor = _valor_informado(ctx, coluna, acao.valor)
    return _preencher(ctx, coluna, valor, f"o valor {_texto(valor)}")


# Duplicados --------------------------------------------------------------------------------


def _remover_duplicados(ctx: _Contexto, _acao: AcaoLimpeza) -> _Efeito:
    colunas = colunas_comparaveis(ctx.tipos)
    if colunas:
        copias = ctx.dados.duplicated(subset=colunas, keep="first")
    else:
        copias = pd.Series(False, index=ctx.dados.index)
    return _remocao(ctx, copias, frases.duplicadas_removidas(int(copias.sum())))


# Fora de faixa -----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class _Faixa:
    coluna: str
    numeros: pd.Series
    fora: pd.Series
    inferior: float
    superior: float


def _faixa(ctx: _Contexto, acao: AcaoLimpeza) -> _Faixa:
    coluna = _coluna(ctx, acao)
    numeros = _numeros(ctx, coluna)
    inferior, superior, _ = faixa_da_coluna(numeros.dropna(), acao.limites)
    fora = (numeros < inferior) | (numeros > superior)
    return _Faixa(coluna, numeros, fora, inferior, superior)


def _remover_fora(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    faixa = _faixa(ctx, acao)
    return _remocao(ctx, faixa.fora, frases.fora_removidas(int(faixa.fora.sum()), faixa.coluna))


def _limitar(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    faixa = _faixa(ctx, acao)
    limitados = faixa.numeros.clip(faixa.inferior, faixa.superior)
    serie = _substituir(ctx.dados[faixa.coluna], faixa.fora, limitados, ctx.decimal)
    linhas = _linhas(faixa.fora)
    antes = _texto(celula(faixa.numeros[faixa.fora].iloc[0])) if linhas else ""
    depois = _texto(celula(limitados[faixa.fora].iloc[0])) if linhas else ""
    inferior, superior = formatar_numero(faixa.inferior), formatar_numero(faixa.superior)
    frase = frases.fora_limitados(len(linhas), faixa.coluna, inferior, superior)
    return _Efeito(_com_coluna(ctx, faixa.coluna, serie), linhas, antes, depois, frase)


def _marcar_fora(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    faixa = _faixa(ctx, acao)
    serie = ctx.dados[faixa.coluna].mask(faixa.fora)
    linhas = _linhas(faixa.fora)
    antes = _texto(celula(faixa.numeros[faixa.fora].iloc[0])) if linhas else ""
    frase = frases.fora_marcados(len(linhas), faixa.coluna)
    return _Efeito(_com_coluna(ctx, faixa.coluna, serie), linhas, antes, VAZIO, frase)


# Grafias e tipo misto ----------------------------------------------------------------------


def _unificar(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    serie = ctx.dados[coluna]
    grupos = [g for g in grupos_de_grafias(serie) if acao.grupo in {None, g.forma_preferida}]
    mapa = {v.texto: g.forma_preferida for g in grupos for v in g.variacoes}
    alvo = serie.isin(list(mapa))
    novo = serie.mask(alvo, serie.map(mapa))
    antes, depois = ", ".join(mapa), ", ".join(dict.fromkeys(mapa.values()))
    frase = frases.grafias_unificadas(int(alvo.sum()), coluna)
    return _Efeito(_com_coluna(ctx, coluna, novo), _linhas(alvo), antes, depois, frase)


def _marcar_textos(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    numeros = _numeros(ctx, coluna)
    textos = ctx.dados[coluna].notna() & numeros.isna()
    linhas = _linhas(textos)
    antes = str(ctx.dados[coluna][textos].iloc[0]) if linhas else ""
    frase = frases.textos_marcados(len(linhas), coluna)
    return _Efeito(_com_coluna(ctx, coluna, numeros), linhas, antes, VAZIO, frase)


MANIPULADORES: dict[tuple[str, str], _Manipulador] = {
    ("faltantes", "remover_linhas"): _remover_vazias,
    ("faltantes", "preencher_media"): _preencher_media,
    ("faltantes", "preencher_mediana"): _preencher_mediana,
    ("faltantes", "preencher_moda"): _preencher_moda,
    ("faltantes", "preencher_valor"): _preencher_valor,
    ("duplicados", "remover"): _remover_duplicados,
    ("fora_de_faixa", "remover_linhas"): _remover_fora,
    ("fora_de_faixa", "limitar"): _limitar,
    ("fora_de_faixa", "marcar_faltante"): _marcar_fora,
    ("inconsistencia", "unificar"): _unificar,
    ("tipo_misto", "marcar_faltante"): _marcar_textos,
}


def _validar(acoes: list[AcaoLimpeza]) -> list[AcaoLimpeza]:
    """Descarta "manter", recusa combinações desconhecidas e ordena pela spec 03."""
    validas = [a for a in acoes if a.acao != MANTER]
    for acao in validas:
        if (acao.problema, acao.acao) not in MANIPULADORES:
            raise erros.acao_incompativel(acao.coluna, f"não existe a ação {acao.acao}.")
    return sorted(validas, key=lambda a: ORDEM_PROBLEMAS.index(a.problema))


def aplicar_acoes(
    dados: pd.DataFrame,
    tipos: Mapping[str, TipoColuna],
    decimal: str | None,
    acoes: list[AcaoLimpeza],
    quando: datetime,
) -> ResultadoAcoes:
    """Aplica as ações em ordem; cada uma que mexeu em alguma linha vira uma entrada no log."""
    log: list[EntradaLog] = []
    alteradas: set[str] = set()
    for acao in _validar(acoes):
        efeito = MANIPULADORES[(acao.problema, acao.acao)](_Contexto(dados, tipos, decimal), acao)
        if not efeito.linhas:
            continue
        removeu = len(efeito.dados) != len(dados)
        alteradas |= set(map(str, dados.columns)) if removeu else {str(acao.coluna)}
        dados = efeito.dados
        log.append(
            EntradaLog(
                acao.problema,
                acao.acao,
                acao.coluna,
                efeito.linhas,
                efeito.antes,
                efeito.depois,
                quando,
                efeito.frase,
            )
        )
    return ResultadoAcoes(dados, tuple(log), frozenset(alteradas))
