"""Registro das regras do detector, na ordem R1…R11 (adicionar regra = criar arquivo + listar)."""

from collections.abc import Collection

from app.dominios.detector.regras.base import Regra
from app.dominios.detector.regras.r01_bloco_alinhado import RegraBlocoAlinhado
from app.dominios.detector.regras.r02_correlacao_blocos import RegraCorrelacaoBlocos
from app.dominios.detector.regras.r03_formato import RegraFormato
from app.dominios.detector.regras.r04_redondos import RegraRedondos
from app.dominios.detector.regras.r05_duplicatas import RegraDuplicatas
from app.dominios.detector.regras.r07_outliers import RegraOutliers
from app.dominios.detector.regras.r08_benford import RegraBenford
from app.dominios.detector.regras.r09_ultimo_digito import RegraUltimoDigito

REGRAS: tuple[Regra, ...] = (
    RegraBlocoAlinhado(),
    RegraCorrelacaoBlocos(),
    RegraFormato(),
    RegraRedondos(),
    RegraDuplicatas(),
    RegraOutliers(),
    RegraBenford(),
    RegraUltimoDigito(),
)


def regras_pedidas(codigos: Collection[str] | None) -> tuple[Regra, ...]:
    """As regras com os códigos pedidos, na ordem do registro; sem códigos, todas."""
    if not codigos:
        return REGRAS
    return tuple(regra for regra in REGRAS if regra.codigo in codigos)
