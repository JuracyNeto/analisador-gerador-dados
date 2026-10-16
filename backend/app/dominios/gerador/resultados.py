"""Value objects do gerador (spec 11): parâmetros, comparação e origem de uma geração."""

from dataclasses import dataclass
from typing import Literal, Protocol

type TipoGeracao = Literal["univariado", "bivariado"]


@dataclass(frozen=True, slots=True)
class Parametro:
    """Parâmetro já formatado para a tela e o relatório: "Média" · "70,31"."""

    nome: str
    valor: str


@dataclass(frozen=True, slots=True)
class LinhaComparacao:
    estatistica: str
    original: float | None
    gerado: float | None
    diferenca: float | None


@dataclass(frozen=True, slots=True)
class OrigemGeracao:
    dataset_id: str
    nome_arquivo: str
    colunas: tuple[str, ...]


class ResumoComparavel(Protocol):
    """Medidas que a comparação usa (o `ResumoNumerico` da análise cumpre este contrato)."""

    @property
    def n(self) -> int: ...
    @property
    def media(self) -> float: ...
    @property
    def mediana(self) -> float: ...
    @property
    def desvio_padrao(self) -> float: ...
    @property
    def minimo(self) -> float: ...
    @property
    def maximo(self) -> float: ...
    @property
    def assimetria(self) -> float | None: ...
    @property
    def curtose(self) -> float | None: ...
