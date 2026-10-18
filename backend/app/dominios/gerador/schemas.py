"""Contratos da API do gerador (spec 11, spec 14)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.esquemas import Figura, Formula

LIMITE_GERACAO = 1_000_000
MAX_SEMENTE = 2**32 - 1

type Celula = float | int | str | None


class Modelo(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrigemColuna(BaseModel):
    dataset_id: str
    coluna: str


class PedidoUnivariado(BaseModel):
    """Sem origem, só "parametros" (contínua, discreta ou binária)."""

    origem: OrigemColuna | None = None
    tipo: Literal["continua", "discreta", "binaria"] | None = None
    x: int = Field(ge=1, le=LIMITE_GERACAO)
    modo: Literal["preservar", "parametros"] = "preservar"
    media: float | None = None
    desvio: float | None = Field(default=None, gt=0)
    p: float | None = Field(default=None, ge=0, le=1)
    rotulos: tuple[str, str] | None = None
    semente: int | None = Field(default=None, ge=0, le=MAX_SEMENTE)
    limitar_faixa: bool = False


class OrigemPar(BaseModel):
    dataset_id: str
    x: str
    y: str


class PedidoBivariado(BaseModel):
    """Com origem, o que for omitido vem do par (médias, desvios e r de Pearson)."""

    origem: OrigemPar | None = None
    n: int = Field(ge=3, le=LIMITE_GERACAO)
    media_x: float | None = None
    media_y: float | None = None
    desvio_x: float | None = Field(default=None, gt=0)
    desvio_y: float | None = Field(default=None, gt=0)
    rho: float | None = Field(default=None, ge=-1, le=1)
    nome_x: str | None = Field(default=None, min_length=1)
    nome_y: str | None = Field(default=None, min_length=1)
    ajuste_exato: bool = True
    semente: int | None = Field(default=None, ge=0, le=MAX_SEMENTE)


class ParametroGeracao(Modelo):
    nome: str
    valor: str


class LinhaComparacao(Modelo):
    estatistica: str
    original: float | None
    gerado: float | None
    diferenca: float | None


class OrigemGeracao(Modelo):
    dataset_id: str
    nome_arquivo: str
    colunas: list[str]


class Gerado(Modelo):
    gerado_id: str
    tipo: Literal["univariado", "bivariado"]
    colunas: list[str]
    n: int
    semente: int
    origem: OrigemGeracao | None
    metodo: str
    explicacao: str
    parametros: list[ParametroGeracao]
    amostra: list[dict[str, Celula]]
    comparacao: list[LinhaComparacao]
    figuras: list[Figura]
    formulas: list[Formula]


class PedidoAdotar(BaseModel):
    modo: Literal["novo", "anexar"]
    dataset_id: str | None = None


class Adotado(Modelo):
    dataset_id: str
    nome_arquivo: str
    n_linhas: int
    modo: Literal["novo", "anexar"]


class ResumoOrigem(Modelo):
    coluna: str
    tipo: Literal["nominal", "ordinal", "discreta", "continua", "binaria"]
    n: int
    media: float | None
    desvio: float | None
    minimo: float | None
    maximo: float | None
    sucesso: str | None
    fracasso: str | None
    chance: float | None
    so_preservar: bool


class ResumoOrigemPar(Modelo):
    x: str
    y: str
    n: int
    media_x: float
    media_y: float
    desvio_x: float
    desvio_y: float
    r: float
