"""Helpers de pandas sem regra de negócio (conversão numérica, inteiros, casas decimais)."""

import numpy as np
import pandas as pd

MAX_CASAS_DECIMAIS = 6
_TOLERANCIA = 1e-9


def converter_para_numero(serie: pd.Series, decimal: str | None = ".") -> pd.Series:
    """Converte para float; o que não for número vira NaN. Com decimal ',' o '.' é milhar."""
    if pd.api.types.is_bool_dtype(serie):
        return pd.Series(np.nan, index=serie.index, dtype="float64")
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype("float64")
    texto = serie.astype("string").str.strip()
    if decimal == ",":
        texto = texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce").astype("float64")


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
