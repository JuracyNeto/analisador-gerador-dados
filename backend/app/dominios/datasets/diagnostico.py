"""Diagnóstico de problemas comuns, sem alterar os dados (spec 03)."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

import pandas as pd

from app.compartilhado.series import converter_para_numero
from app.compartilhado.textos import normalizar_texto
from app.compartilhado.tipos import TIPOS_CATEGORICOS, TIPOS_NUMERICOS, TipoVariavel
from app.dominios.datasets import erros
from app.dominios.datasets.modelos import Celula, TipoColuna
from app.dominios.datasets.tabela import celula

FATOR_IQR = 1.5
QUARTIS = (0.25, 0.75)


@dataclass(frozen=True, slots=True)
class Limites:
    """Faixa aceita para uma coluna numérica; None = sem limite daquele lado."""

    min: float | None = None
    max: float | None = None


@dataclass(frozen=True, slots=True)
class ValoresSugeridos:
    media: float | None
    mediana: float | None
    moda: Celula


@dataclass(frozen=True, slots=True)
class FaltantesColuna:
    coluna: str
    n: int
    linhas: tuple[int, ...]
    sugeridos: ValoresSugeridos


@dataclass(frozen=True, slots=True)
class GrupoDuplicado:
    linha_original: int
    copias: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Ocorrencia:
    linha: int
    valor: Celula


@dataclass(frozen=True, slots=True)
class ForaDeFaixaColuna:
    coluna: str
    limite_inferior: float
    limite_superior: float
    origem: Literal["iqr", "usuario"]
    ocorrencias: tuple[Ocorrencia, ...]


@dataclass(frozen=True, slots=True)
class Grafia:
    texto: str
    n: int


@dataclass(frozen=True, slots=True)
class GrupoGrafias:
    forma_preferida: str
    variacoes: tuple[Grafia, ...]


@dataclass(frozen=True, slots=True)
class InconsistenciaColuna:
    coluna: str
    grupos: tuple[GrupoGrafias, ...]


@dataclass(frozen=True, slots=True)
class TipoMistoColuna:
    coluna: str
    ocorrencias: tuple[Ocorrencia, ...]


@dataclass(frozen=True, slots=True)
class Diagnostico:
    n_linhas: int
    faltantes: tuple[FaltantesColuna, ...]
    duplicados: tuple[GrupoDuplicado, ...]
    fora_de_faixa: tuple[ForaDeFaixaColuna, ...]
    inconsistencias: tuple[InconsistenciaColuna, ...]
    tipo_misto: tuple[TipoMistoColuna, ...]


def _linhas(mascara: pd.Series) -> tuple[int, ...]:
    return tuple(int(i) for i in mascara[mascara].index.tolist())


def _ocorrencias(serie: pd.Series, mascara: pd.Series) -> tuple[Ocorrencia, ...]:
    marcados = serie[mascara]
    return tuple(
        Ocorrencia(int(linha), celula(valor))
        for linha, valor in zip(marcados.index.tolist(), marcados.tolist(), strict=True)
    )


def _sugeridos(serie: pd.Series, numeros: pd.Series | None) -> ValoresSugeridos:
    modas = serie.dropna().mode()
    moda = celula(modas.iloc[0]) if not modas.empty else None
    if numeros is None or numeros.dropna().empty:
        return ValoresSugeridos(None, None, moda)
    return ValoresSugeridos(float(numeros.mean()), float(numeros.median()), moda)


def faltantes(
    dados: pd.DataFrame, numericas: Mapping[str, pd.Series]
) -> tuple[FaltantesColuna, ...]:
    """Colunas com células vazias, as linhas afetadas e os valores sugeridos para preencher."""
    resultado = []
    for nome in dados.columns:
        vazias = dados[nome].isna()
        if vazias.any():
            sugeridos = _sugeridos(dados[nome], numericas.get(nome))
            resultado.append(FaltantesColuna(nome, int(vazias.sum()), _linhas(vazias), sugeridos))
    return tuple(resultado)


def colunas_comparaveis(tipos: Mapping[str, TipoColuna]) -> list[str]:
    """Colunas usadas para achar duplicados: todas menos identificadores (D50)."""
    return [nome for nome, tipo in tipos.items() if tipo.tipo != TipoVariavel.IDENTIFICADOR]


def duplicados(dados: pd.DataFrame, colunas: list[str]) -> tuple[GrupoDuplicado, ...]:
    """Linhas iguais à primeira ocorrência (keep="first") nas colunas comparáveis."""
    if not colunas:
        return ()
    grupos = dados.groupby(colunas, dropna=False, sort=False).indices
    repetidos = (sorted(dados.index[posicoes]) for posicoes in grupos.values() if len(posicoes) > 1)
    return tuple(
        GrupoDuplicado(int(linhas[0]), tuple(int(i) for i in linhas[1:]))
        for linhas in sorted(repetidos)
    )


def faixa_iqr(numeros: pd.Series) -> tuple[float, float]:
    """Cercas de Tukey: [Q1 − 1,5·IQR, Q3 + 1,5·IQR]."""
    q1, q3 = (float(q) for q in numeros.quantile(list(QUARTIS)))
    iqr = q3 - q1
    return q1 - FATOR_IQR * iqr, q3 + FATOR_IQR * iqr


def faixa_da_coluna(numeros: pd.Series, limites: Limites | None) -> tuple[float, float, bool]:
    """Faixa aceita: a do usuário onde houver limite, senão a do IQR."""
    inferior, superior = faixa_iqr(numeros)
    if limites is None:
        return inferior, superior, False
    if limites.min is not None and limites.max is not None and limites.min >= limites.max:
        raise erros.limites_invalidos(limites.max)
    inferior = limites.min if limites.min is not None else inferior
    superior = limites.max if limites.max is not None else superior
    return inferior, superior, True


def fora_de_faixa(
    dados: pd.DataFrame, numericas: Mapping[str, pd.Series], limites: Mapping[str, Limites]
) -> tuple[ForaDeFaixaColuna, ...]:
    """Valores numéricos fora da faixa aceita, por coluna."""
    resultado = []
    for nome, numeros in numericas.items():
        if numeros.dropna().empty:
            continue
        inferior, superior, do_usuario = faixa_da_coluna(numeros, limites.get(nome))
        fora = (numeros < inferior) | (numeros > superior)
        if fora.any():
            origem: Literal["iqr", "usuario"] = "usuario" if do_usuario else "iqr"
            ocorrencias = _ocorrencias(dados[nome], fora)
            resultado.append(ForaDeFaixaColuna(nome, inferior, superior, origem, ocorrencias))
    return tuple(resultado)


def grupos_de_grafias(serie: pd.Series) -> tuple[GrupoGrafias, ...]:
    """Grafias que viram o mesmo texto ao normalizar; a mais frequente é a preferida."""
    contagens = serie.dropna().astype(str).value_counts()
    por_forma: dict[str, list[Grafia]] = {}
    for texto, n in contagens.items():
        por_forma.setdefault(normalizar_texto(str(texto)), []).append(Grafia(str(texto), int(n)))
    return tuple(
        GrupoGrafias(grafias[0].texto, tuple(grafias[1:]))
        for grafias in por_forma.values()
        if len(grafias) > 1
    )


def inconsistencias(
    dados: pd.DataFrame, tipos: Mapping[str, TipoColuna], numericas: Mapping[str, pd.Series]
) -> tuple[InconsistenciaColuna, ...]:
    """Categorias de texto escritas de jeitos diferentes ("SP", "sp ", "Sp")."""
    resultado = []
    for nome, tipo in tipos.items():
        if tipo.tipo not in TIPOS_CATEGORICOS or nome in numericas:
            continue
        grupos = grupos_de_grafias(dados[nome])
        if grupos:
            resultado.append(InconsistenciaColuna(nome, grupos))
    return tuple(resultado)


def tipo_misto(
    dados: pd.DataFrame, numericas: Mapping[str, pd.Series]
) -> tuple[TipoMistoColuna, ...]:
    """Textos que não viram número em colunas numéricas (ex.: "doze")."""
    resultado = []
    for nome, numeros in numericas.items():
        textos = dados[nome].notna() & numeros.isna()
        if textos.any():
            resultado.append(TipoMistoColuna(nome, _ocorrencias(dados[nome], textos)))
    return tuple(resultado)


def series_numericas(
    dados: pd.DataFrame, tipos: Mapping[str, TipoColuna], decimal: str | None
) -> dict[str, pd.Series]:
    """Colunas discretas/contínuas convertidas para número (texto que não converte vira NaN)."""
    return {
        nome: converter_para_numero(dados[nome], decimal)
        for nome, tipo in tipos.items()
        if tipo.tipo in TIPOS_NUMERICOS
    }


def diagnosticar(
    dados: pd.DataFrame,
    tipos: Mapping[str, TipoColuna],
    decimal: str | None,
    limites: Mapping[str, Limites],
) -> Diagnostico:
    """Levanta faltantes, duplicados, fora de faixa, grafias diferentes e tipo misto."""
    numericas = series_numericas(dados, tipos, decimal)
    return Diagnostico(
        n_linhas=len(dados),
        faltantes=faltantes(dados, numericas),
        duplicados=duplicados(dados, colunas_comparaveis(tipos)),
        fora_de_faixa=fora_de_faixa(dados, numericas, limites),
        inconsistencias=inconsistencias(dados, tipos, numericas),
        tipo_misto=tipo_misto(dados, numericas),
    )
