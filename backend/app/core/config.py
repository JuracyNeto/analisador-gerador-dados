"""Configuração da aplicação, lida de variáveis de ambiente com prefixo AGD_."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    """Parâmetros globais; limiares documentados em docs/specs/02-tipos.md e ADR 0004."""

    model_config = SettingsConfigDict(env_prefix="AGD_", env_file=".env", extra="ignore")

    nome_app: str = "Analisador e Gerador de Dados"
    versao: str = "0.0.0"
    cors_origens: list[str] = ["http://localhost:5173"]
    limite_arquivo_mb: int = 50
    max_datasets: int = 20
    limiar_discreta: int = 30
    limiar_unicos_identificador: float = 0.95


@lru_cache
def obter_configuracao() -> Configuracao:
    """Instância única, injetada via Depends."""
    return Configuracao()
