from collections.abc import Callable, Sequence

import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.resultados import Amostra

type CriarAmostra = Callable[..., Amostra]

ESCALA_SATISFACAO = ("ruim", "regular", "bom", "ótimo")


def _criar(
    tipo: TipoVariavel, valores: Sequence[float | str], ordem: tuple[str, ...] = ()
) -> Amostra:
    serie = pd.Series(list(valores), index=pd.RangeIndex(1, len(valores) + 1))
    return Amostra("x", tipo, serie, 0, ordem)


@pytest.fixture
def criar_amostra() -> CriarAmostra:
    """Fábrica de amostras: criar_amostra(TipoVariavel.CONTINUA, [1.5, 2.0])."""
    return _criar
