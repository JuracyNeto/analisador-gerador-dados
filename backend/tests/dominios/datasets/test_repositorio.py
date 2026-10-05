import pandas as pd
import pytest

from app.core.erros import NaoEncontrado
from app.dominios.datasets.modelos import Dataset, MetadadosLeitura
from app.dominios.datasets.repositorio import RepositorioDatasets


def _dataset(identificador: str) -> Dataset:
    dados = pd.DataFrame({"a": [1]})
    metadados = MetadadosLeitura("csv", "utf-8", ",", ".", True, 1, 1)
    return Dataset(identificador, "a.csv", metadados, dados, dados.copy(), {})


def test_repositorio_guarda_e_devolve() -> None:
    repositorio = RepositorioDatasets(limite=2)
    repositorio.adicionar(_dataset("a"))

    assert repositorio.obter("a").id == "a"


def test_repositorio_descarta_o_mais_antigo() -> None:
    repositorio = RepositorioDatasets(limite=2)
    for identificador in ("a", "b", "c"):
        repositorio.adicionar(_dataset(identificador))

    assert len(repositorio) == 2
    with pytest.raises(NaoEncontrado) as erro:
        repositorio.obter("a")
    assert erro.value.codigo == "DATASET_NAO_ENCONTRADO"


def test_repositorio_remove() -> None:
    repositorio = RepositorioDatasets(limite=2)
    repositorio.adicionar(_dataset("a"))

    repositorio.remover("a")

    assert len(repositorio) == 0
