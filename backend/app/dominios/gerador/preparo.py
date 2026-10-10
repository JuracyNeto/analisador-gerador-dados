"""Validação dos pedidos e montagem dos contextos de texto (regras puras do gerador)."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.gerador import erros, textos
from app.dominios.gerador.comparacao import MedidasPar
from app.dominios.gerador.estrategias.base import EntradaEstrategia
from app.dominios.gerador.parametros import DescricaoUnivariada, origem_coluna
from app.dominios.gerador.pedidos import PedidoBivariado, PedidoUnivariado
from app.dominios.gerador.reescala import casas_decimais
from app.dominios.gerador.resultados import OrigemGeracao
from app.dominios.gerador.univariado import TIPOS_SO_PRESERVAR

CASAS_SEM_ORIGEM = 2
TIPOS_SEM_ORIGEM = frozenset({TipoVariavel.CONTINUA, TipoVariavel.DISCRETA, TipoVariavel.BINARIA})
ROTULOS_SEM_ORIGEM = ("0", "1")
CAMPOS_BIVARIADO = ("a média de X", "a média de Y", "o desvio de X", "o desvio de Y", "ρ")


@dataclass(frozen=True, slots=True, eq=False)
class Preparo:
    """Pedido univariado pronto para a estratégia."""

    tipo: TipoVariavel
    coluna: str
    entrada: EntradaEstrategia
    origem: OrigemGeracao | None = None


def _faltando(tipo: TipoVariavel, pedido: PedidoUnivariado) -> list[str]:
    if pedido.modo != "parametros":
        return []
    if tipo == TipoVariavel.BINARIA:
        return [] if pedido.p is not None else ["a chance de sucesso"]
    campos = [("a média", pedido.media), ("o desvio", pedido.desvio)]
    return [nome for nome, valor in campos if valor is None]


def validar_parametros(tipo: TipoVariavel, pedido: PedidoUnivariado) -> None:
    """Nominal/ordinal só preservam; novos parâmetros exigem os campos do tipo."""
    if pedido.modo == "parametros" and tipo in TIPOS_SO_PRESERVAR:
        raise erros.modo_nao_aplicavel(tipo)
    faltando = _faltando(tipo, pedido)
    if faltando:
        raise erros.parametros_incompletos(faltando)


def casas_da_coluna(tipo: TipoVariavel, valores: pd.Series) -> int:
    if tipo != TipoVariavel.CONTINUA:
        return 0
    return casas_decimais(valores.to_numpy(dtype="float64"))


def preparo_sem_origem(pedido: PedidoUnivariado) -> Preparo:
    """Só "Parâmetros manuais": contínua, discreta ou binária."""
    if pedido.modo == "preservar":
        raise erros.origem_obrigatoria()
    if pedido.tipo is None:
        raise erros.parametros_incompletos(["o tipo"])
    if pedido.tipo not in TIPOS_SEM_ORIGEM:
        raise erros.modo_nao_aplicavel(pedido.tipo)
    validar_parametros(pedido.tipo, pedido)
    entrada = EntradaEstrategia(
        x=pedido.x,
        modo="parametros",
        media=pedido.media,
        desvio=pedido.desvio,
        p=pedido.p,
        rotulos=pedido.rotulos or ROTULOS_SEM_ORIGEM,
        casas=CASAS_SEM_ORIGEM if pedido.tipo == TipoVariavel.CONTINUA else 0,
    )
    return Preparo(pedido.tipo, textos.COLUNA_SEM_ORIGEM, entrada)


def _numeros(preparo: Preparo) -> np.ndarray | None:
    originais = preparo.entrada.originais
    if originais is None or preparo.tipo not in TIPOS_NUMERICOS:
        return None
    return originais.to_numpy(dtype="float64")


def _medidas(pedido: PedidoUnivariado, numeros: np.ndarray | None) -> tuple[float | None, ...]:
    if pedido.modo == "preservar" and numeros is not None:
        return float(numeros.mean()), float(numeros.std(ddof=1))
    return pedido.media, pedido.desvio


def _chance(
    pedido: PedidoUnivariado, originais: pd.Series | None, sucesso: str | None
) -> float | None:
    if pedido.modo == "preservar" and originais is not None and sucesso is not None:
        return float((originais.astype(str) == sucesso).mean())
    return pedido.p


def contexto_univariado(
    pedido: PedidoUnivariado, preparo: Preparo, metodo: str, semente: int
) -> textos.ContextoExplicacao:
    """O que "Como geramos" precisa: medidas usadas, rótulos, casas e faixa."""
    entrada = preparo.entrada
    numeros = _numeros(preparo)
    media, desvio = _medidas(pedido, numeros)
    fracasso, sucesso = entrada.rotulos or (None, None)
    faixa = (
        (float(numeros.min()), float(numeros.max()))
        if entrada.limitar_faixa and numeros is not None
        else None
    )
    return textos.ContextoExplicacao(
        metodo=metodo,
        quantidade=pedido.x,
        semente=semente,
        coluna=preparo.coluna if preparo.origem is not None else None,
        media=media,
        desvio=desvio,
        chance=_chance(pedido, entrada.originais, sucesso),
        sucesso=sucesso,
        fracasso=fracasso,
        casas=entrada.casas,
        faixa=faixa,
        sem_negativos=numeros is not None and float(numeros.min()) >= 0,
        preservar=pedido.modo == "preservar",
    )


def descricao_univariada(
    pedido: PedidoUnivariado, preparo: Preparo, contexto: textos.ContextoExplicacao
) -> DescricaoUnivariada:
    origem = (
        origem_coluna(preparo.origem.colunas, preparo.origem.nome_arquivo)
        if preparo.origem is not None
        else textos.PARAMETROS_MANUAIS
    )
    binaria = preparo.tipo == TipoVariavel.BINARIA
    numerica = preparo.tipo in TIPOS_NUMERICOS
    return DescricaoUnivariada(
        origem=origem,
        quantidade=pedido.x,
        modo=pedido.modo,
        semente=contexto.semente,
        media=contexto.media if numerica else None,
        desvio=contexto.desvio if numerica else None,
        sucesso=contexto.sucesso if binaria else None,
        chance=contexto.chance if binaria else None,
        limitar_faixa=preparo.entrada.limitar_faixa,
    )


def medidas_par(x: np.ndarray, y: np.ndarray) -> MedidasPar:
    r = float(np.corrcoef(x, y)[0, 1]) if len(x) > 1 else 0.0
    return MedidasPar(
        len(x),
        float(x.mean()),
        float(y.mean()),
        float(x.std(ddof=1)),
        float(y.std(ddof=1)),
        0.0 if np.isnan(r) else r,
    )


@dataclass(frozen=True, slots=True)
class BaseBivariada:
    """Nomes, valores pedidos, padrões (do par de origem), casas e o original para comparar."""

    nomes: tuple[str, str]
    pedidos: tuple[float | None, ...]
    padroes: tuple[float | None, ...]
    casas: tuple[int, int]
    original: MedidasPar | None = None
    pontos_originais: tuple[tuple[float, ...], tuple[float, ...]] | None = None
    origem: OrigemGeracao | None = None

    def valores(self) -> tuple[float, ...]:
        """Médias, desvios e ρ: o pedido ou, se omitido, o do par de origem."""
        return tuple(
            float(pedido if pedido is not None else padrao or 0.0)
            for pedido, padrao in zip(self.pedidos, self.padroes, strict=True)
        )


def valores_pedidos(pedido: PedidoBivariado) -> tuple[float | None, ...]:
    return (pedido.media_x, pedido.media_y, pedido.desvio_x, pedido.desvio_y, pedido.rho)


def base_sem_origem(pedido: PedidoBivariado) -> BaseBivariada:
    """Sem origem, médias, desvios e ρ são obrigatórios; nomes padrão "x" e "y"."""
    pedidos = valores_pedidos(pedido)
    faltando = [
        nome for nome, valor in zip(CAMPOS_BIVARIADO, pedidos, strict=True) if valor is None
    ]
    if faltando:
        raise erros.parametros_incompletos(faltando)
    nomes = (
        pedido.nome_x or textos.NOMES_SEM_ORIGEM[0],
        pedido.nome_y or textos.NOMES_SEM_ORIGEM[1],
    )
    return BaseBivariada(
        nomes=nomes,
        pedidos=pedidos,
        padroes=(None,) * len(pedidos),
        casas=(CASAS_SEM_ORIGEM, CASAS_SEM_ORIGEM),
    )


def base_com_origem(
    pedido: PedidoBivariado, x: np.ndarray, y: np.ndarray, origem: OrigemGeracao
) -> BaseBivariada:
    """Omitidos = copiados do par (médias e DPs amostrais, r de Pearson)."""
    medidas = medidas_par(x, y)
    return BaseBivariada(
        nomes=(origem.colunas[0], origem.colunas[1]),
        pedidos=valores_pedidos(pedido),
        padroes=(medidas.media_x, medidas.media_y, medidas.desvio_x, medidas.desvio_y, medidas.r),
        casas=(casas_decimais(x), casas_decimais(y)),
        original=medidas,
        pontos_originais=(tuple(float(v) for v in x), tuple(float(v) for v in y)),
        origem=origem,
    )
