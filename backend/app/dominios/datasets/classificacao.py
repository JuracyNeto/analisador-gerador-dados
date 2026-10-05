"""Classificação automática do tipo de cada coluna (spec 02, ADR 0006).

Chain of Responsibility: as regras são testadas em ordem e a primeira que responder vence;
se nenhuma responder, a coluna é contínua.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.series import converter_para_numero, eh_inteira
from app.compartilhado.textos import normalizar_texto, pluralizar
from app.compartilhado.tipos import TIPOS_CATEGORICOS, OrigemTipo, TipoVariavel
from app.dominios.datasets.escalas_ordinais import ordenar_por_escala
from app.dominios.datasets.modelos import TipoColuna

N_MINIMO_IDENTIFICADOR = 20
N_EXEMPLOS = 5
VALORES_BINARIA = 2
PRECISAO_TEXTO = 12
_NOME_DE_CODIGO = re.compile(r"^(id|cod|codigo|cpf|cnpj|cep|telefone|fone|matricula)\b")


@dataclass(frozen=True, slots=True)
class Limiares:
    """Limiares de config.py (spec 02, D48)."""

    discreta: int = 30
    unicos_identificador: float = 0.95
    numerico: float = 0.9


@dataclass(frozen=True, slots=True)
class Classificacao:
    tipo: TipoVariavel
    motivo: str
    categorias_ordem: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, eq=False)
class ColunaLida:
    """Coluna pronta para classificar: valores válidos e, se for numérica, os números."""

    nome: str
    serie: pd.Series
    numeros: pd.Series | None
    textos: pd.Series
    limiares: Limiares

    @property
    def validos(self) -> pd.Series:
        return self.textos.dropna()

    @property
    def n_distintos(self) -> int:
        serie = self.validos if self.numeros is None else self.numeros.dropna()
        return int(serie.nunique())

    def categorias(self) -> list[str]:
        """Valores distintos como texto, em ordem crescente (numérica quando for número)."""
        if self.numeros is None:
            return sorted(str(v) for v in self.validos.unique())
        return [texto_do_numero(v) for v in sorted(self.numeros.dropna().unique())]


def serie_numerica(serie: pd.Series, decimal: str | None, limiar: float) -> pd.Series | None:
    """Série convertida para número se ≥ limiar dos valores válidos viram número (D48)."""
    n_validos = int(serie.notna().sum())
    if n_validos == 0:
        return None
    numeros = converter_para_numero(serie, decimal)
    return numeros if numeros.notna().sum() / n_validos >= limiar else None


def texto_do_numero(valor: float) -> str:
    """Inteiros sem separador de milhar (códigos, contagens); decimais com vírgula."""
    if float(valor).is_integer():
        return str(int(valor))
    return formatar_numero(float(valor), PRECISAO_TEXTO)


def _textos(serie: pd.Series, numeros: pd.Series | None) -> pd.Series:
    if numeros is None:
        return serie.map(lambda v: v if pd.isna(v) else str(v))
    return numeros.map(lambda v: v if pd.isna(v) else texto_do_numero(v))


def ler_coluna(nome: str, serie: pd.Series, decimal: str | None, limiares: Limiares) -> ColunaLida:
    """Converte uma vez e guarda números e textos (números no formato pt-BR)."""
    numeros = serie_numerica(serie, decimal, limiares.numerico)
    return ColunaLida(nome, serie, numeros, _textos(serie, numeros), limiares)


def _eh_decimal(coluna: ColunaLida) -> bool:
    return coluna.numeros is not None and not eh_inteira(coluna.numeros)


def _vazia(coluna: ColunaLida) -> Classificacao | None:
    if not coluna.validos.empty:
        return None
    return Classificacao(TipoVariavel.IDENTIFICADOR, "A coluna está vazia; foi ignorada.")


def _identificador(coluna: ColunaLida) -> Classificacao | None:
    nome = normalizar_texto(coluna.nome).replace("_", " ").replace("-", " ")
    if _NOME_DE_CODIGO.match(nome):
        motivo = f"O nome da coluna indica um código ({coluna.nome})."
        return Classificacao(TipoVariavel.IDENTIFICADOR, motivo)
    n = len(coluna.validos)
    if _eh_decimal(coluna) or n < N_MINIMO_IDENTIFICADOR:
        return None
    unicos = coluna.n_distintos / n
    if unicos < coluna.limiares.unicos_identificador:
        return None
    motivo = f"Parece um código: {formatar_numero(unicos * 100, 3)}% dos valores são únicos."
    return Classificacao(TipoVariavel.IDENTIFICADOR, motivo)


def _binaria(coluna: ColunaLida) -> Classificacao | None:
    if coluna.n_distintos != VALORES_BINARIA:
        return None
    a, b = coluna.categorias()
    return Classificacao(TipoVariavel.BINARIA, f"Tem só dois valores: {a} e {b}.")


def _ordinal(coluna: ColunaLida) -> Classificacao | None:
    ordem = ordenar_por_escala(coluna.categorias()) if coluna.numeros is None else None
    if ordem is None:
        return None
    motivo = f"Os valores seguem uma escala conhecida: {' < '.join(ordem)}."
    return Classificacao(TipoVariavel.ORDINAL, motivo, ordem)


def _nominal(coluna: ColunaLida) -> Classificacao | None:
    if coluna.numeros is not None:
        return None
    k = coluna.n_distintos
    motivo = f"São categorias sem ordem natural ({k} {pluralizar(k, 'categoria', 'categorias')})."
    return Classificacao(TipoVariavel.NOMINAL, motivo)


def _discreta(coluna: ColunaLida) -> Classificacao | None:
    if _eh_decimal(coluna) or coluna.n_distintos > coluna.limiares.discreta:
        return None
    motivo = f"Números inteiros com {coluna.n_distintos} valores diferentes (contagem)."
    return Classificacao(TipoVariavel.DISCRETA, motivo)


def _continua(coluna: ColunaLida) -> Classificacao:
    if _eh_decimal(coluna):
        return Classificacao(TipoVariavel.CONTINUA, "Números com casas decimais.")
    k = coluna.n_distintos
    motivo = f"Inteiros com muitos valores diferentes ({k}); tratada como contínua."
    return Classificacao(TipoVariavel.CONTINUA, motivo)


type Regra = Callable[[ColunaLida], Classificacao | None]

REGRAS: tuple[Regra, ...] = (_vazia, _identificador, _binaria, _ordinal, _nominal, _discreta)


def classificar(coluna: ColunaLida) -> Classificacao:
    """Primeira regra que responder; sem resposta, a coluna é contínua (regra 6)."""
    for regra in REGRAS:
        resultado = regra(coluna)
        if resultado is not None:
            return resultado
    return _continua(coluna)


def descrever(coluna: ColunaLida, classificacao: Classificacao, origem: OrigemTipo) -> TipoColuna:
    """Junta o tipo com contagens, exemplos e (para categóricas) as frequências."""
    contagens = coluna.validos.value_counts()
    categorica = classificacao.tipo in TIPOS_CATEGORICOS
    return TipoColuna(
        coluna=coluna.nome,
        tipo=classificacao.tipo,
        motivo=classificacao.motivo,
        origem=origem,
        n_validos=len(coluna.validos),
        n_faltantes=int(coluna.serie.isna().sum()),
        n_distintos=coluna.n_distintos,
        exemplos=tuple(str(v) for v in coluna.validos.unique()[:N_EXEMPLOS]),
        categorias_ordem=classificacao.categorias_ordem,
        contagens={str(k): int(v) for k, v in contagens.items()} if categorica else {},
    )


def classificar_tabela(
    dados: pd.DataFrame, decimal: str | None, limiares: Limiares
) -> dict[str, TipoColuna]:
    """Classifica todas as colunas (origem automática)."""
    resultado: dict[str, TipoColuna] = {}
    for nome in dados.columns:
        coluna = ler_coluna(str(nome), dados[nome], decimal, limiares)
        resultado[str(nome)] = descrever(coluna, classificar(coluna), OrigemTipo.AUTO)
    return resultado
