"""Value objects do detector: aviso em 8 partes, não aplicadas e resumo (spec 12, spec 16)."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from app.compartilhado.tipos import Severidade


@dataclass(frozen=True, slots=True)
class ExemploAviso:
    """Linhas e valores concretos do alerta ("Linhas 120 a 138: 70, 75, 80…")."""

    linhas: tuple[int, ...]
    valores: tuple[str, ...]
    texto: str


@dataclass(frozen=True, slots=True)
class DetalhesAviso:
    """Detalhes técnicos, recolhidos na tela: medida, valor, limiar, teste, p e fórmula."""

    medida: str
    valor: str
    limiar: str
    teste: str | None = None
    p_valor: float | None = None
    p_em_palavras: str | None = None
    formula: str | None = None


@dataclass(frozen=True, slots=True)
class TextosAviso:
    """Partes escritas do aviso (spec 16), montadas só em textos.py."""

    titulo: str
    resumo: str
    por_que: str
    pode_ser_normal: str
    o_que_fazer: str


@dataclass(frozen=True, slots=True)
class GraficoBlocos:
    """Média de cada bloco de k linhas e o bloco alinhado (R1); a figura sai no serviço (D123)."""

    coluna: str
    tamanho: int
    linhas_do_meio: tuple[float, ...]
    medias: tuple[float, ...]
    geral: tuple[float, float]
    """(média, DP) do conjunto."""
    alinhado: tuple[int, int, float]
    """(primeira linha, última linha, média) do bloco alinhado."""


type PosicaoDigito = Literal["primeiro", "ultimo"]


@dataclass(frozen=True, slots=True)
class GraficoDigitos:
    """Proporção de cada dígito, observada × esperada (R8: primeiro; R9: último)."""

    coluna: str
    posicao: PosicaoDigito
    digitos: tuple[int, ...]
    observadas: tuple[float, ...]
    esperadas: tuple[float, ...]


type Grafico = GraficoBlocos | GraficoDigitos


class FiguraPronta(Protocol):
    """Figura montada pelo domínio graficos; o serviço a põe no aviso (D123)."""

    @property
    def id(self) -> str: ...

    @property
    def titulo(self) -> str: ...

    @property
    def dados(self) -> Mapping[str, Any]: ...


@dataclass(frozen=True, slots=True)
class Aviso:
    """Um alerta com as 8 partes da spec 16 e, em R1, R8 e R9, os dados do gráfico."""

    regra: str
    nome_regra: str
    severidade: Severidade
    colunas: tuple[str, ...]
    titulo: str
    resumo: str
    por_que: str
    exemplo: ExemploAviso | None
    pode_ser_normal: str
    o_que_fazer: str
    detalhes: DetalhesAviso
    grafico: Grafico | None = None
    figura: FiguraPronta | None = None


@dataclass(frozen=True, slots=True)
class RegraNaoAplicada:
    """Regra (ou parte dela) não verificada numa coluna, no par ou no arquivo, com o motivo."""

    regra: str
    nome_regra: str
    coluna: str | None
    motivo: str
    frase: str


@dataclass(frozen=True, slots=True)
class PorSeveridade:
    alta: int
    atencao: int
    info: int


@dataclass(frozen=True, slots=True)
class ResumoDetector:
    """Topo da tela 7: contagens e frases ("Encontramos 5 alertas em 3 colunas")."""

    total: int
    por_severidade: PorSeveridade
    colunas_afetadas: tuple[str, ...]
    regras_verificadas: int
    regras_nao_aplicadas: int
    frase: str
    detalhe: str
    vazio: str | None


@dataclass(frozen=True, slots=True)
class ResultadoDetector:
    resumo: ResumoDetector
    avisos: tuple[Aviso, ...]
    nao_aplicadas: tuple[RegraNaoAplicada, ...]
