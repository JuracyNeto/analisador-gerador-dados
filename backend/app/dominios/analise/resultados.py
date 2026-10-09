"""Value objects dos resultados da análise univariada (specs 04–07, contrato `Analise`)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

from app.compartilhado.tipos import TipoVariavel

type Valor = float | str | None
type TipoSeparatriz = Literal["quartil", "decil", "percentil"]
type Distribuicao = Literal["normal", "binomial", "bernoulli"]
type ClasseAssimetria = Literal["simetrica", "moderada", "forte"]
type Sentido = Literal["direita", "esquerda"]
type ClasseCurtose = Literal["mesocurtica", "leptocurtica", "platicurtica"]


@dataclass(frozen=True, slots=True, eq=False)
class Amostra:
    """Valores válidos de uma coluna: números (discreta/contínua) ou textos (categóricas)."""

    coluna: str
    tipo: TipoVariavel
    valores: pd.Series
    n_faltantes: int
    ordem: tuple[str, ...] = ()

    @property
    def n(self) -> int:
        return len(self.valores)


@dataclass(frozen=True, slots=True)
class NaoAplicavel:
    item: str
    motivo: str


@dataclass(frozen=True, slots=True)
class Formula:
    chave: str
    nome: str
    latex: str
    texto: str


@dataclass(frozen=True, slots=True)
class Medida:
    """Uma medida com valor, ou não aplicável com motivo (spec 16: nunca some)."""

    valor: Valor = None
    aplicavel: bool = True
    motivo: str | None = None
    calculo: str | None = None
    interpretacao: str | None = None
    formula: str | None = None


def nao_aplicavel(motivo: str) -> Medida:
    return Medida(aplicavel=False, motivo=motivo)


@dataclass(frozen=True, slots=True)
class LinhaFrequencia:
    rotulo: str
    valor: Valor
    fi: int
    fri: float
    fr_pct: float
    limite_inferior: float | None = None
    limite_superior: float | None = None
    ponto_medio: float | None = None
    f_acum: int | None = None
    fr_acum: float | None = None
    fr_acum_pct: float | None = None


@dataclass(frozen=True, slots=True)
class TabelaFrequencia:
    tipo: TipoVariavel
    linhas: tuple[LinhaFrequencia, ...]
    total: int
    acumulada_aplicavel: bool
    motivo_acumulada: str | None = None
    indice_modal: int | None = None
    k: int | None = None
    k_sturges: int | None = None
    h: float | None = None
    metodo_classes: Literal["sturges", "usuario"] | None = None


@dataclass(frozen=True, slots=True)
class Moda:
    valores: tuple[float | str, ...]
    classificacao: Literal["amodal", "unimodal", "bimodal", "multimodal"]
    interpretacao: str


@dataclass(frozen=True, slots=True)
class Tendencia:
    media: Medida
    mediana: Medida
    moda: Moda
    moda_czuber: Medida
    proporcao: Medida


@dataclass(frozen=True, slots=True)
class ValorSeparatriz:
    rotulo: str
    p: float
    valor: float | str


@dataclass(frozen=True, slots=True)
class Separatrizes:
    quartis: tuple[ValorSeparatriz, ...]
    decis: tuple[ValorSeparatriz, ...]
    percentis: tuple[ValorSeparatriz, ...]
    destaques: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Dispersao:
    amplitude: Medida
    variancia: Medida
    variancia_populacional: Medida
    desvio_padrao: Medida
    desvio_padrao_populacional: Medida
    iqr: Medida
    cv: Medida
    classificacao_cv: Literal["baixa", "media", "alta"] | None = None


@dataclass(frozen=True, slots=True)
class Posicao:
    valor: float
    tipo: TipoSeparatriz
    regiao: str
    indice: int
    limite_inferior: float | None
    limite_superior: float | None
    posicao_percentil: float
    fora_da_faixa: Literal["abaixo", "acima"] | None
    minimo: float
    maximo: float
    marcas: tuple[ValorSeparatriz, ...]
    frase: str


@dataclass(frozen=True, slots=True)
class Figura:
    """Figura Plotly pronta (M1.5); `dados` = {"data": [...], "layout": {...}} sem template."""

    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Parametro:
    """Parâmetro estimado de uma distribuição (μ̂, σ̂, n, p̂, E[X], Var)."""

    simbolo: str
    nome: str
    valor: float


@dataclass(frozen=True, slots=True)
class TesteAderencia:
    nome: str
    estatistica: float
    gl: int | None
    p_valor: float
    compativel: bool


@dataclass(frozen=True, slots=True)
class Ajuste:
    """Distribuição ajustada com teste de aderência, ou não aplicável com motivo (spec 09)."""

    distribuicao: Distribuicao
    aplicavel: bool = True
    motivo: str | None = None
    parametros: tuple[Parametro, ...] = ()
    teste: TesteAderencia | None = None
    complementar: TesteAderencia | None = None
    frase: str | None = None
    calculo: str | None = None
    formula: str | None = None


def ajuste_nao_aplicavel(distribuicao: Distribuicao, motivo: str) -> Ajuste:
    return Ajuste(distribuicao, aplicavel=False, motivo=motivo)


@dataclass(frozen=True, slots=True)
class Forma:
    """Assimetria, curtose e ajustes de uma coluna (spec 09, contrato `Analise.forma`)."""

    assimetria: Medida
    assimetria_pearson_1: Medida
    assimetria_pearson_2: Medida
    curtose: Medida
    curtose_percentilica: Medida
    normal: Ajuste
    binomial: Ajuste
    classificacao_assimetria: ClasseAssimetria | None = None
    sentido_assimetria: Sentido | None = None
    classificacao_curtose: ClasseCurtose | None = None
    tentativas: int | None = None
    interpretacao: str | None = None
    figuras: tuple[Figura, ...] = ()


@dataclass(frozen=True, slots=True)
class Analise:
    coluna: str
    tipo: TipoVariavel
    n: int
    n_faltantes: int
    aplicavel: Mapping[str, bool]
    nao_aplicavel: tuple[NaoAplicavel, ...]
    frequencias: TabelaFrequencia
    tendencia: Tendencia
    separatrizes: Separatrizes | None
    dispersao: Dispersao | None
    interpretacoes: tuple[str, ...]
    formulas: tuple[Formula, ...]
    figuras: tuple[Figura, ...] = ()
    forma: Forma | None = None
