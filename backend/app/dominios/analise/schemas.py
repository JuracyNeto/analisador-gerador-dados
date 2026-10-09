"""Contratos HTTP do domínio analise (spec 14; nomes na visão geral do M1)."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.compartilhado.tipos import TipoVariavel

type Valor = float | str | None


class Modelo(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class NaoAplicavel(Modelo):
    item: str
    motivo: str


class Formula(Modelo):
    chave: str
    nome: str
    latex: str
    texto: str


class Medida(Modelo):
    valor: Valor
    aplicavel: bool
    motivo: str | None
    calculo: str | None
    interpretacao: str | None
    formula: str | None


class LinhaFrequencia(Modelo):
    rotulo: str
    valor: Valor
    limite_inferior: float | None
    limite_superior: float | None
    ponto_medio: float | None
    fi: int
    fri: float
    fr_pct: float
    f_acum: int | None
    fr_acum: float | None
    fr_acum_pct: float | None


class TabelaFrequencia(Modelo):
    tipo: TipoVariavel
    linhas: list[LinhaFrequencia]
    total: int
    k: int | None
    k_sturges: int | None
    h: float | None
    metodo_classes: Literal["sturges", "usuario"] | None
    acumulada_aplicavel: bool
    motivo_acumulada: str | None
    indice_modal: int | None


class Moda(Modelo):
    valores: list[float | str]
    classificacao: Literal["amodal", "unimodal", "bimodal", "multimodal"]
    interpretacao: str


class Tendencia(Modelo):
    media: Medida
    mediana: Medida
    moda: Moda
    moda_czuber: Medida
    proporcao: Medida


class ValorSeparatriz(Modelo):
    rotulo: str
    p: float
    valor: float | str


class Separatrizes(Modelo):
    quartis: list[ValorSeparatriz]
    decis: list[ValorSeparatriz]
    percentis: list[ValorSeparatriz]
    destaques: list[str]


class Dispersao(Modelo):
    amplitude: Medida
    variancia: Medida
    variancia_populacional: Medida
    desvio_padrao: Medida
    desvio_padrao_populacional: Medida
    iqr: Medida
    cv: Medida
    classificacao_cv: Literal["baixa", "media", "alta"] | None


class Figura(Modelo):
    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: dict[str, Any]


class Parametro(Modelo):
    simbolo: str
    nome: str
    valor: float


class TesteAderencia(Modelo):
    nome: str
    estatistica: float
    gl: int | None
    p_valor: float
    compativel: bool


class Ajuste(Modelo):
    distribuicao: Literal["normal", "binomial", "bernoulli"]
    aplicavel: bool
    motivo: str | None
    parametros: list[Parametro]
    teste: TesteAderencia | None
    complementar: TesteAderencia | None
    frase: str | None
    calculo: str | None
    formula: str | None


class Forma(Modelo):
    assimetria: Medida
    assimetria_pearson_1: Medida
    assimetria_pearson_2: Medida
    curtose: Medida
    curtose_percentilica: Medida
    classificacao_assimetria: Literal["simetrica", "moderada", "forte"] | None
    sentido_assimetria: Literal["direita", "esquerda"] | None
    classificacao_curtose: Literal["mesocurtica", "leptocurtica", "platicurtica"] | None
    normal: Ajuste
    binomial: Ajuste
    tentativas: int | None
    interpretacao: str | None
    figuras: list[Figura]


class Analise(Modelo):
    coluna: str
    tipo: TipoVariavel
    n: int
    n_faltantes: int
    aplicavel: dict[str, bool]
    nao_aplicavel: list[NaoAplicavel]
    frequencias: TabelaFrequencia
    tendencia: Tendencia
    separatrizes: Separatrizes | None
    dispersao: Dispersao | None
    forma: Forma | None
    interpretacoes: list[str]
    formulas: list[Formula]
    figuras: list[Figura]


class Posicao(Modelo):
    valor: float
    tipo: Literal["quartil", "decil", "percentil"]
    regiao: str
    indice: int
    limite_inferior: float | None
    limite_superior: float | None
    posicao_percentil: float
    fora_da_faixa: Literal["abaixo", "acima"] | None
    minimo: float
    maximo: float
    marcas: list[ValorSeparatriz]
    frase: str
