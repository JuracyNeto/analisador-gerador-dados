"""Configuração da aplicação, lida de variáveis de ambiente com prefixo AGD_."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class Exemplo:
    """Arquivo de demonstração em dados-exemplo/ que o usuário pode escolher (D124)."""

    arquivo: str
    descricao: str


EXEMPLOS = (
    Exemplo("pesquisa_saude.txt", "Pesquisa de saúde (valores fora de faixa e duplicados)"),
    Exemplo("alturas_reais.txt", "Alturas reais (sem manipulação)"),
    Exemplo("alturas_plantadas.txt", "Alturas com dados plantados"),
    Exemplo("vendas_correlacao_puxada.txt", "Vendas com correlação puxada"),
)


class Configuracao(BaseSettings):
    """Parâmetros globais; limiares documentados em docs/specs/02-tipos.md e ADR 0004."""

    model_config = SettingsConfigDict(env_prefix="AGD_", env_file=".env", extra="ignore")

    nome_app: str = "Analisador e Gerador de Dados"
    versao: str = "0.2.0"
    cors_origens: list[str] = ["http://localhost:5173"]
    limite_arquivo_mb: int = 50
    max_datasets: int = 20
    limiar_discreta: int = 30
    limiar_unicos_identificador: float = 0.95
    limiar_numerico: float = 0.9
    limiar_data: float = 0.9
    tamanho_previa: int = 20
    pasta_exemplos: Path = RAIZ_REPOSITORIO / "dados-exemplo"
    arquivo_exemplo: str = "pesquisa_saude.txt"
    exemplos: tuple[Exemplo, ...] = EXEMPLOS
    max_gerados: int = 20
    limite_geracao: int = 1_000_000
    tamanho_amostra_gerada: int = 50

    @property
    def limite_arquivo_bytes(self) -> int:
        return self.limite_arquivo_mb * 1024 * 1024


@lru_cache
def obter_configuracao() -> Configuracao:
    """Instância única, injetada via Depends."""
    return Configuracao()
