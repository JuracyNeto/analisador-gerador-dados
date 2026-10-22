"""Contratos HTTP do detector (spec 12, spec 14)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, TypeAdapter

from app.compartilhado.tipos import Severidade
from app.core.esquemas import Figura

type CodigoRegra = Literal["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11"]
CODIGOS_REGRA = TypeAdapter(list[CodigoRegra])


class Modelo(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ExemploAviso(Modelo):
    linhas: list[int]
    valores: list[str]
    texto: str
    total_linhas: int


class DetalhesAviso(Modelo):
    medida: str
    valor: str
    limiar: str
    teste: str | None
    p_valor: float | None
    p_em_palavras: str | None
    formula: str | None


class AvisoDetector(Modelo):
    """Um alerta em 8 partes (spec 16); `colunas` vazio = linhas inteiras (R5, R6).

    `figura`: gráfico dos detalhes técnicos em R1, R8 e R9 (spec 08, D123).
    """

    regra: CodigoRegra
    nome_regra: str
    severidade: Severidade
    colunas: list[str]
    titulo: str
    resumo: str
    por_que: str
    exemplo: ExemploAviso | None
    pode_ser_normal: str
    o_que_fazer: str
    detalhes: DetalhesAviso
    figura: Figura | None


class RegraNaoAplicada(Modelo):
    regra: CodigoRegra
    nome_regra: str
    coluna: str | None
    motivo: str
    frase: str


class PorSeveridade(Modelo):
    alta: int
    atencao: int
    info: int


class ResumoDetector(Modelo):
    total: int
    por_severidade: PorSeveridade
    colunas_afetadas: list[str]
    regras_verificadas: int
    regras_nao_aplicadas: int
    frase: str
    detalhe: str
    vazio: str | None


class ResultadoDetector(Modelo):
    resumo: ResumoDetector
    avisos: list[AvisoDetector]
    nao_aplicadas: list[RegraNaoAplicada]
