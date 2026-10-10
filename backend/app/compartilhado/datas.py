"""Reconhecimento de datas e horários por formato explícito (spec 02, D90, D91).

Só formatos conhecidos: deixar o pandas "adivinhar" tomaria códigos e números por datas.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Literal

import pandas as pd

type FormatoData = Literal[
    "dd/mm/aaaa", "mm/dd/aaaa", "aaaa-mm-dd", "data_hora", "hora", "planilha"
]

LIMITE_DIA_MES = 12
DATA_DOS_HORARIOS = {"year": 1900, "month": 1, "day": 1}
_DMY = r"(?P<a>\d{1,2})[/.-](?P<b>\d{1,2})[/.-](?P<ano>\d{4})"
_ISO = r"(?P<ano>\d{4})-(?P<mes>\d{1,2})-(?P<dia>\d{1,2})"
_HORA = r"(?P<hora>\d{1,2}):(?P<minuto>\d{2})(?::(?P<segundo>\d{2}))?"
_SEPARADOR_HORA = r"[ T]"


@dataclass(frozen=True, slots=True, eq=False)
class LeituraDatas:
    """Formato que mais reconheceu valores, as datas convertidas e um exemplo do arquivo."""

    formato: FormatoData
    valores: pd.Series
    proporcao: float
    exemplo: str


def _numeros(extraido: pd.DataFrame, coluna: str) -> pd.Series:
    return pd.to_numeric(extraido[coluna], errors="coerce")


def _dia_primeiro(extraido: pd.DataFrame) -> bool:
    """D91: dia primeiro, salvo quando só o segundo campo passa de 12."""
    primeiro, segundo = _numeros(extraido, "a"), _numeros(extraido, "b")
    return bool((primeiro > LIMITE_DIA_MES).any()) or not (segundo > LIMITE_DIA_MES).any()


def _partes_dmy(extraido: pd.DataFrame) -> dict[str, pd.Series]:
    dia, mes = ("a", "b") if _dia_primeiro(extraido) else ("b", "a")
    return {
        "year": _numeros(extraido, "ano"),
        "month": _numeros(extraido, mes),
        "day": _numeros(extraido, dia),
    }


def _partes_iso(extraido: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "year": _numeros(extraido, "ano"),
        "month": _numeros(extraido, "mes"),
        "day": _numeros(extraido, "dia"),
    }


def _partes_hora(extraido: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "hour": _numeros(extraido, "hora"),
        "minute": _numeros(extraido, "minuto"),
        "second": _numeros(extraido, "segundo").fillna(0),
    }


def _partes_so_hora(extraido: pd.DataFrame) -> dict[str, pd.Series]:
    fixas = {
        chave: pd.Series(valor, index=extraido.index) for chave, valor in DATA_DOS_HORARIOS.items()
    }
    return fixas | _partes_hora(extraido)


def _com_hora(
    partes_data: Callable[[pd.DataFrame], dict[str, pd.Series]],
) -> Callable[[pd.DataFrame], dict[str, pd.Series]]:
    return lambda extraido: partes_data(extraido) | _partes_hora(extraido)


@dataclass(frozen=True, slots=True)
class _Padrao:
    formato: FormatoData
    regex: re.Pattern[str]
    partes: Callable[[pd.DataFrame], dict[str, pd.Series]]


def _padrao(
    formato: FormatoData, expressao: str, partes: Callable[..., dict[str, pd.Series]]
) -> _Padrao:
    return _Padrao(formato, re.compile(f"^{expressao}$"), partes)


PADROES: tuple[_Padrao, ...] = (
    _padrao("dd/mm/aaaa", _DMY, _partes_dmy),
    _padrao("aaaa-mm-dd", _ISO, _partes_iso),
    _padrao("data_hora", f"{_DMY}{_SEPARADOR_HORA}{_HORA}", _com_hora(_partes_dmy)),
    _padrao("data_hora", f"{_ISO}{_SEPARADOR_HORA}{_HORA}", _com_hora(_partes_iso)),
    _padrao("hora", _HORA, _partes_so_hora),
)


def _converter(textos: pd.Series, padrao: _Padrao) -> pd.Series:
    """Datas dos textos que casam com o padrão; o resto (e datas impossíveis) vira NaT."""
    extraido = textos.str.extract(padrao.regex)
    casaram = extraido.notna().any(axis="columns")
    datas = pd.Series(pd.NaT, index=textos.index, dtype="datetime64[ns]")
    if not casaram.any():
        return datas
    partes = pd.DataFrame(padrao.partes(extraido[casaram]))
    datas[casaram] = pd.to_datetime(partes, errors="coerce")
    return datas


def _formato_real(padrao: _Padrao, textos: pd.Series) -> FormatoData:
    if padrao.formato != "dd/mm/aaaa":
        return padrao.formato
    extraido = textos.str.extract(padrao.regex).dropna()
    return "dd/mm/aaaa" if _dia_primeiro(extraido) else "mm/dd/aaaa"


def _leitura(formato: FormatoData, datas: pd.Series, originais: pd.Series) -> LeituraDatas | None:
    reconhecidas = datas.notna()
    if not reconhecidas.any():
        return None
    exemplo = originais[reconhecidas].iloc[0]
    texto = exemplo if isinstance(exemplo, str) else formatar_data(exemplo)
    return LeituraDatas(formato, datas, float(reconhecidas.mean()), texto)


def _formato_da_planilha(datas: pd.Series) -> FormatoData:
    """Só horários, só datas com horário ou datas (com ou sem horário), como nos textos."""
    validas = datas.dropna()
    dias = validas.dt.normalize()
    if (dias == pd.Timestamp(date(**DATA_DOS_HORARIOS))).all():
        return "hora"
    if (dias != validas).all():
        return "data_hora"
    return "planilha"


def _da_planilha(validos: pd.Series) -> LeituraDatas | None:
    """Células de data/hora do XLSX chegam como datetime64 ou objetos date/time."""
    if pd.api.types.is_datetime64_any_dtype(validos):
        return _leitura(_formato_da_planilha(validos), validos, validos)
    eh_data = validos.map(lambda v: isinstance(v, date | time))
    if not eh_data.any():
        return None
    datas = pd.to_datetime(validos.where(eh_data).map(_como_datetime, na_action="ignore"))
    return _leitura(_formato_da_planilha(datas), datas, validos)


def _como_datetime(valor: date | time) -> datetime:
    if isinstance(valor, time):
        return datetime.combine(date(**DATA_DOS_HORARIOS), valor)
    if isinstance(valor, datetime):
        return valor
    return datetime.combine(valor, time())


def _dos_textos(validos: pd.Series) -> LeituraDatas | None:
    textos = validos.astype("string").str.strip()
    melhor: LeituraDatas | None = None
    for formato in dict.fromkeys(p.formato for p in PADROES):
        padroes = [p for p in PADROES if p.formato == formato]
        datas = _converter(textos, padroes[0])
        for extra in padroes[1:]:
            datas = datas.fillna(_converter(textos, extra))
        leitura = _leitura(_formato_real(padroes[0], textos), datas, validos)
        if leitura is not None and (melhor is None or leitura.proporcao > melhor.proporcao):
            melhor = leitura
    return melhor


def reconhecer_datas(serie: pd.Series) -> LeituraDatas | None:
    """Melhor formato de data/hora da série (só valores não faltantes), ou None."""
    validos = serie.dropna()
    if validos.empty:
        return None
    return _da_planilha(validos) or _dos_textos(validos)


def formatar_data(valor: object) -> str:
    """07/10/2026 · 07/10/2026 08:30 · 08:30 (pt-BR); texto volta como está."""
    if isinstance(valor, time):
        return _formatar_hora(valor)
    if isinstance(valor, datetime):
        return _formatar_data_hora(valor)
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _formatar_hora(valor: time) -> str:
    return valor.strftime("%H:%M:%S" if valor.second else "%H:%M")


def _formatar_data_hora(valor: datetime) -> str:
    if valor.date() == date(**DATA_DOS_HORARIOS):
        return _formatar_hora(valor.time())
    if valor.time() == time():
        return valor.strftime("%d/%m/%Y")
    return f"{valor.strftime('%d/%m/%Y')} {_formatar_hora(valor.time())}"
