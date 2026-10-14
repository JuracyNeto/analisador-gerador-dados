from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import Configuracao
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.servico import (
    OpcoesLeitura,
    ServicoDatasets,
    obter_servico_datasets,
)
from app.dominios.gerador.servico import RepositorioGerados, obter_repositorio_gerados
from app.main import create_app

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def servico_datasets() -> ServicoDatasets:
    """Serviço com repositório novo: cada teste começa sem datasets."""
    config = Configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)


@pytest.fixture
def cliente(servico_datasets: ServicoDatasets) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[obter_servico_datasets] = lambda: servico_datasets
    gerados: RepositorioGerados[Any] = RepositorioGerados(Configuracao().max_gerados)
    app.dependency_overrides[obter_repositorio_gerados] = lambda: gerados
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def cadastro_variado(servico_datasets: ServicoDatasets) -> str:
    """Id do cadastro com tipos de dado variados (fixtures/cadastro_variado.txt, D131).

    Importado no mesmo serviço que o `cliente` usa: os testes podem seguir pela API.
    """
    caminho = FIXTURES / "cadastro_variado.txt"
    importacao = servico_datasets.importar(caminho.read_bytes(), caminho.name, OpcoesLeitura())
    return importacao.dataset_id
