""" "Onde está meu valor?": posição percentil e região entre separatrizes (spec 06)."""

import math
from typing import Literal

import numpy as np

from app.compartilhado.numeros import formatar_numero
from app.dominios.analise.resultados import Posicao, TipoSeparatriz, ValorSeparatriz
from app.dominios.analise.separatrizes import DESTAQUES, DIVISOES, quantis

MAX_PERCENTIL = 100

type Marcas = tuple[ValorSeparatriz, ...]


def posicao_percentil(valores: np.ndarray, valor: float) -> float:
    """PR = 100 · (nº de xᵢ < v + 0,5 · nº de xᵢ = v) / n."""
    menores, iguais = np.sum(valores < valor), np.sum(valores == valor)
    return float(100 * (menores + 0.5 * iguais) / len(valores))


def _indice(valor: float, tipo: TipoSeparatriz, marcas: Marcas, pr: float) -> int:
    """Região 1…k: até a 1ª marca é 1; acima da última, a última região."""
    if tipo == "percentil":
        return min(max(math.ceil(pr), 1), MAX_PERCENTIL)
    limites = [float(m.valor) for m in marcas]
    return int(np.searchsorted(limites, valor, side="left")) + 1


def _vizinhas(indice: int, marcas: Marcas) -> tuple[ValorSeparatriz | None, ValorSeparatriz | None]:
    inferior = marcas[indice - 2] if indice > 1 else None
    superior = marcas[indice - 1] if indice <= len(marcas) else None
    return inferior, superior


def _marca(marca: ValorSeparatriz) -> str:
    return f"{marca.rotulo} = {formatar_numero(float(marca.valor))}"


def _trecho(inferior: ValorSeparatriz | None, superior: ValorSeparatriz | None) -> str:
    if inferior is None and superior is not None:
        return f"até {_marca(superior)}"
    if superior is None and inferior is not None:
        return f"acima de {_marca(inferior)}"
    if inferior is not None and superior is not None:
        return f"entre {_marca(inferior)} e {_marca(superior)}"
    return "em toda a faixa"


def _regiao(tipo: TipoSeparatriz, indice: int) -> str:
    return f"percentil {indice}" if tipo == "percentil" else f"{indice}º {tipo}"


def _fora(valor: float, minimo: float, maximo: float) -> Literal["abaixo", "acima"] | None:
    if valor < minimo:
        return "abaixo"
    return "acima" if valor > maximo else None


def _aviso_fora(fora: str | None, minimo: float, maximo: float) -> str:
    if fora == "abaixo":
        return f" O valor está abaixo do menor dado observado ({formatar_numero(minimo)})."
    if fora == "acima":
        return f" O valor está acima do maior dado observado ({formatar_numero(maximo)})."
    return ""


def calcular_posicao(valores: np.ndarray, valor: float, tipo: TipoSeparatriz) -> Posicao:
    """Em que quartil/decil/percentil o valor cai e quantos dados ficam abaixo dele."""
    todas = quantis(valores, DIVISOES[tipo])
    pr = posicao_percentil(valores, valor)
    indice = _indice(valor, tipo, todas, pr)
    inferior, superior = _vizinhas(indice, todas)
    minimo, maximo = float(valores.min()), float(valores.max())
    fora = _fora(valor, minimo, maximo)
    regiao = _regiao(tipo, indice)
    frase = (
        f"O valor {formatar_numero(valor)} está no {regiao} ({_trecho(inferior, superior)}). "
        f"Cerca de {round(pr)}% dos dados são menores que ele."
        f"{_aviso_fora(fora, minimo, maximo)}"
    )
    marcas = tuple(m for m in todas if m.rotulo in DESTAQUES) if tipo == "percentil" else todas
    return Posicao(
        valor=valor,
        tipo=tipo,
        regiao=regiao,
        indice=indice,
        limite_inferior=float(inferior.valor) if inferior else None,
        limite_superior=float(superior.valor) if superior else None,
        posicao_percentil=pr,
        fora_da_faixa=fora,
        minimo=minimo,
        maximo=maximo,
        marcas=marcas,
        frase=frase,
    )
