"""Helpers de pandas sem regra de negócio (conversão numérica, inteiros, casas decimais)."""

import re
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from app.compartilhado.numeros import MENOS

MAX_CASAS_DECIMAIS = 6
_TOLERANCIA = 1e-9
# "R$" antes do número (o sinal pode vir antes ou depois dele) e "%" depois; \s inclui o espaço
# não separável que o Excel e os navegadores põem depois do R$.
_UNIDADE = re.compile(r"^(-?)\s*R\$\s*|\s*%$")
_MARCA_DE_UNIDADE = re.compile(rf"[$%{MENOS}]")

type TipoUnidade = Literal["reais", "percentual"]
_PADROES_UNIDADE: dict[TipoUnidade, re.Pattern[str]] = {
    "reais": re.compile(rf"^[-{MENOS}]?\s*R\$"),
    "percentual": re.compile(r"%$"),
}


@dataclass(frozen=True, slots=True)
class Unidade:
    """Unidade escrita junto dos números de uma coluna e um valor de exemplo como no arquivo."""

    tipo: TipoUnidade
    exemplo: str


def sem_unidade(texto: str) -> str:
    """Tira "R$" e "%" e troca o sinal de menos (−) pelo hífen: "−R$ 1.234,56" → "-1.234,56"."""
    return _UNIDADE.sub(r"\1", texto.strip().replace(MENOS, "-"))


def _texto_para_numero(texto: pd.Series, decimal: str | None) -> pd.Series:
    if decimal == ",":
        texto = texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce").astype("float64")


def _com_marca_de_unidade(texto: pd.Series, numeros: pd.Series) -> np.ndarray:
    """Posições que não viraram número e têm R$, % ou − (só elas passam pela troca, mais lenta)."""
    falhou = numeros.isna().to_numpy() & texto.notna().to_numpy()
    marcadas = falhou.copy()
    marcadas[falhou] = texto[falhou].str.contains(_MARCA_DE_UNIDADE).to_numpy(dtype=bool)
    return marcadas


def converter_para_numero(serie: pd.Series, decimal: str | None = ".") -> pd.Series:
    """Converte para float; o que não for número vira NaN. Com decimal ',' o '.' é milhar.

    Aceita "R$" antes do número, "%" depois e o sinal de menos (−); o percentual mantém a
    escala do arquivo (12,5% → 12,5).
    """
    if pd.api.types.is_bool_dtype(serie):
        return pd.Series(np.nan, index=serie.index, dtype="float64")
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype("float64")
    texto = serie.astype("string").str.strip()
    numeros = _texto_para_numero(texto, decimal)
    marcadas = _com_marca_de_unidade(texto, numeros)
    if marcadas.any():
        sem_unidades = texto[marcadas].map(sem_unidade).astype("string")
        numeros[marcadas] = _texto_para_numero(sem_unidades, decimal).to_numpy()
    return numeros


def reconhecer_unidade(serie: pd.Series, limiar: float) -> Unidade | None:
    """Unidade ("R$" antes ou "%" depois do número) em ≥ limiar dos valores válidos."""
    if pd.api.types.is_numeric_dtype(serie):
        return None
    textos = serie.dropna().astype("string").str.strip()
    if textos.empty:
        return None
    for tipo, padrao in _PADROES_UNIDADE.items():
        com_unidade = textos[textos.str.contains(padrao)]
        if len(com_unidade) >= limiar * len(textos):
            return Unidade(tipo, str(com_unidade.iloc[0]))
    return None


def proporcao_numerica(serie: pd.Series, decimal: str | None = ".") -> float:
    """Fração dos valores não faltantes que viram número (0 se não houver valores)."""
    validos = serie.dropna()
    if validos.empty:
        return 0.0
    return float(converter_para_numero(validos, decimal).notna().mean())


def eh_inteira(numeros: pd.Series) -> bool:
    """Todos os valores válidos são inteiros (ex.: 3.0 conta como inteiro)."""
    valores = numeros.dropna().to_numpy(dtype="float64")
    return bool(np.all(np.abs(valores - np.round(valores)) < _TOLERANCIA))


def casas_decimais(numeros: pd.Series) -> int:
    """Menor número de casas decimais que representa todos os valores (máx. 6)."""
    valores = numeros.dropna().to_numpy(dtype="float64")
    for casas in range(MAX_CASAS_DECIMAIS):
        escalados = valores * 10**casas
        if np.all(np.abs(escalados - np.round(escalados)) < _TOLERANCIA * 10**casas):
            return casas
    return MAX_CASAS_DECIMAIS


def na_precisao(valor: float, numeros: pd.Series) -> float:
    """O valor nas casas decimais da coluna: a mediana 68,75 de pesos com 1 casa vira 68,8."""
    return float(np.round(valor, casas_decimais(numeros)))
