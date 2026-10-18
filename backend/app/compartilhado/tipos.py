"""Enums e value objects compartilhados entre domínios (padroes-codigo.md §2)."""

from dataclasses import dataclass
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


class Severidade(StrEnum):
    """Severidade de um alerta do detector (spec 12, spec 16)."""

    INFO = "info"
    ATENCAO = "atencao"
    ALTA = "alta"


ORDEM_SEVERIDADE = (Severidade.ALTA, Severidade.ATENCAO, Severidade.INFO)


@dataclass(frozen=True, slots=True)
class Formula:
    """Fórmula em LaTeX (KaTeX) e em texto de reserva; usada na análise, no gerador e no
    relatório (D152)."""

    chave: str
    nome: str
    latex: str
    texto: str
