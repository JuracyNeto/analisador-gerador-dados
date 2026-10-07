from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Configuracao
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.main import create_app


@pytest.fixture
def servico_datasets() -> ServicoDatasets:
    """Serviço com repositório novo: cada teste começa sem datasets."""
    config = Configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)


@pytest.fixture
def cliente(servico_datasets: ServicoDatasets) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[obter_servico_datasets] = lambda: servico_datasets
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
