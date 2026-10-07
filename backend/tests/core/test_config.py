import pytest

from app.core.config import Configuracao


def test_valores_padrao_seguem_as_specs() -> None:
    config = Configuracao()

    assert config.limite_arquivo_mb == 50
    assert config.limite_arquivo_bytes == 50 * 1024 * 1024
    assert config.max_datasets == 20
    assert config.limiar_discreta == 30
    assert config.limiar_unicos_identificador == 0.95
    assert config.limiar_numerico == 0.9
    assert config.tamanho_previa == 20
    assert "http://localhost:5173" in config.cors_origens


def test_exemplo_padrao_existe_no_repositorio() -> None:
    config = Configuracao()

    assert (config.pasta_exemplos / config.arquivo_exemplo).is_file()


def test_variavel_de_ambiente_sobrescreve_padrao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGD_LIMIAR_DISCRETA", "40")

    assert Configuracao().limiar_discreta == 40
