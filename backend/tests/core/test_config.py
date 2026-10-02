import pytest

from app.core.config import Configuracao


def test_valores_padrao_seguem_as_specs() -> None:
    config = Configuracao()

    assert config.limite_arquivo_mb == 50
    assert config.max_datasets == 20
    assert config.limiar_discreta == 30
    assert config.limiar_unicos_identificador == 0.95
    assert "http://localhost:5173" in config.cors_origens


def test_variavel_de_ambiente_sobrescreve_padrao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGD_LIMIAR_DISCRETA", "40")

    assert Configuracao().limiar_discreta == 40
