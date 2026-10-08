"""Enums e value objects compartilhados entre domínios (padroes-codigo.md §2)."""

from enum import StrEnum


class TipoVariavel(StrEnum):
    """Tipos de variável da spec 02; identificador e data são auxiliares (fora das análises)."""

    NOMINAL = "nominal"
    ORDINAL = "ordinal"
    DISCRETA = "discreta"
    CONTINUA = "continua"
    BINARIA = "binaria"
    IDENTIFICADOR = "identificador"
    DATA = "data"


class OrigemTipo(StrEnum):
    """Quem definiu o tipo: a classificação automática ou o usuário."""

    AUTO = "auto"
    MANUAL = "manual"


TIPOS_NUMERICOS = frozenset({TipoVariavel.DISCRETA, TipoVariavel.CONTINUA})
TIPOS_CATEGORICOS = frozenset({TipoVariavel.NOMINAL, TipoVariavel.ORDINAL, TipoVariavel.BINARIA})
TIPOS_AUXILIARES = frozenset({TipoVariavel.IDENTIFICADOR, TipoVariavel.DATA})
