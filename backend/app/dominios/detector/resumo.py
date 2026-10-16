"""Resultado do detector: avisos em ordem, regras não aplicadas e o resumo (spec 12, tela 7)."""

from collections.abc import Sequence

from app.compartilhado.tipos import ORDEM_SEVERIDADE, Severidade
from app.dominios.detector import textos
from app.dominios.detector.regras.base import ResultadoRegra
from app.dominios.detector.resultados import (
    Aviso,
    PorSeveridade,
    ResultadoDetector,
    ResumoDetector,
)


def _chave(aviso: Aviso) -> tuple[int, int, tuple[str, ...]]:
    """Severidade (alta → atenção → info), depois o número da regra, depois a coluna."""
    return ORDEM_SEVERIDADE.index(aviso.severidade), int(aviso.regra[1:]), aviso.colunas


def _contagem(avisos: Sequence[Aviso], severidade: Severidade) -> int:
    return sum(aviso.severidade == severidade for aviso in avisos)


def _resumo(avisos: Sequence[Aviso], regras: int, verificadas: int) -> ResumoDetector:
    colunas = tuple(dict.fromkeys(coluna for aviso in avisos for coluna in aviso.colunas))
    nao_aplicadas = regras - verificadas
    return ResumoDetector(
        total=len(avisos),
        por_severidade=PorSeveridade(
            alta=_contagem(avisos, Severidade.ALTA),
            atencao=_contagem(avisos, Severidade.ATENCAO),
            info=_contagem(avisos, Severidade.INFO),
        ),
        colunas_afetadas=colunas,
        regras_verificadas=verificadas,
        regras_nao_aplicadas=nao_aplicadas,
        frase=textos.frase_resumo(len(avisos), len(colunas)),
        detalhe=textos.detalhe_resumo(colunas, verificadas, nao_aplicadas),
        vazio=None if avisos else textos.vazio_resumo(regras, verificadas),
    )


def montar_resultado(resultados: Sequence[ResultadoRegra]) -> ResultadoDetector:
    """Junta o que cada regra encontrou; verificada = aplicou-se a pelo menos um alvo."""
    avisos = tuple(sorted((a for r in resultados for a in r.avisos), key=_chave))
    verificadas = sum(resultado.verificada for resultado in resultados)
    return ResultadoDetector(
        resumo=_resumo(avisos, len(resultados), verificadas),
        avisos=avisos,
        nao_aplicadas=tuple(item for resultado in resultados for item in resultado.nao_aplicadas),
    )
