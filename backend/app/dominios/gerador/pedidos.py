"""Pedidos e respostas dos casos de uso do gerador (sem framework; o router converte)."""

from dataclasses import dataclass
from typing import Literal

from app.compartilhado.tipos import TipoVariavel
from app.dominios.gerador.estrategias.base import Modo

type ModoAdotar = Literal["novo", "anexar"]


@dataclass(frozen=True, slots=True)
class Origem:
    dataset_id: str
    coluna: str


@dataclass(frozen=True, slots=True)
class PedidoUnivariado:
    x: int
    modo: Modo = "preservar"
    origem: Origem | None = None
    tipo: TipoVariavel | None = None
    media: float | None = None
    desvio: float | None = None
    p: float | None = None
    rotulos: tuple[str, str] | None = None
    semente: int | None = None
    limitar_faixa: bool = False


@dataclass(frozen=True, slots=True)
class OrigemPar:
    dataset_id: str
    x: str
    y: str


@dataclass(frozen=True, slots=True)
class PedidoBivariado:
    n: int
    origem: OrigemPar | None = None
    media_x: float | None = None
    media_y: float | None = None
    desvio_x: float | None = None
    desvio_y: float | None = None
    rho: float | None = None
    nome_x: str | None = None
    nome_y: str | None = None
    ajuste_exato: bool = True
    semente: int | None = None


@dataclass(frozen=True, slots=True)
class Adotado:
    dataset_id: str
    nome_arquivo: str
    n_linhas: int
    modo: ModoAdotar
