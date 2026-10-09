"""Ajuste manual do tipo de uma coluna (spec 02, "Ajuste manual")."""

from app.compartilhado.datas import reconhecer_datas
from app.compartilhado.tipos import TIPOS_NUMERICOS, OrigemTipo, TipoVariavel
from app.dominios.datasets import erros
from app.dominios.datasets.classificacao import (
    VALORES_BINARIA,
    Classificacao,
    ColunaLida,
    descrever,
)
from app.dominios.datasets.escalas_ordinais import ordenar_por_escala
from app.dominios.datasets.modelos import TipoColuna

MOTIVO_MANUAL = "Tipo escolhido por você."
SEM_DATAS = "Esta coluna não tem datas ou horários que dê para reconhecer."
MOTIVO_ORDEM_ALFABETICA = (
    "Tipo escolhido por você. Sem escala conhecida, usamos a ordem alfabética; "
    "ajuste a ordem das categorias."
)


def _tem_datas(coluna: ColunaLida) -> bool:
    leitura = reconhecer_datas(coluna.serie)
    return leitura is not None and leitura.proporcao >= coluna.limiares.data


def _validar(coluna: ColunaLida, tipo: TipoVariavel) -> None:
    if tipo == TipoVariavel.DATA and not _tem_datas(coluna):
        raise erros.tipo_incompativel(SEM_DATAS)
    if tipo in TIPOS_NUMERICOS and coluna.numeros is None:
        raise erros.tipo_incompativel("Esta coluna tem textos; não pode ser numérica.")
    if tipo == TipoVariavel.BINARIA and coluna.n_distintos != VALORES_BINARIA:
        mensagem = f"Binária precisa de exatamente 2 valores; esta coluna tem {coluna.n_distintos}."
        raise erros.tipo_incompativel(mensagem)


def _ordem_informada(coluna: ColunaLida, ordem: list[str]) -> Classificacao:
    presentes = coluna.categorias()
    faltando = [c for c in presentes if c not in ordem]
    if faltando:
        raise erros.categorias_incompletas(faltando)
    ordenadas = tuple(c for c in ordem if c in presentes)
    return Classificacao(TipoVariavel.ORDINAL, MOTIVO_MANUAL, ordenadas)


def _ordem_automatica(coluna: ColunaLida) -> Classificacao:
    ordem = ordenar_por_escala(coluna.categorias())
    if ordem is None:
        alfabetica = tuple(sorted(coluna.categorias()))
        return Classificacao(TipoVariavel.ORDINAL, MOTIVO_ORDEM_ALFABETICA, alfabetica)
    return Classificacao(TipoVariavel.ORDINAL, MOTIVO_MANUAL, ordem)


def ajustar_tipo(
    coluna: ColunaLida, tipo: TipoVariavel, categorias_ordem: list[str] | None
) -> TipoColuna:
    """Aplica o tipo escolhido pelo usuário (origem manual) depois de validar."""
    _validar(coluna, tipo)
    if tipo != TipoVariavel.ORDINAL:
        return descrever(coluna, Classificacao(tipo, MOTIVO_MANUAL), OrigemTipo.MANUAL)
    if categorias_ordem:
        return descrever(coluna, _ordem_informada(coluna, categorias_ordem), OrigemTipo.MANUAL)
    return descrever(coluna, _ordem_automatica(coluna), OrigemTipo.MANUAL)
