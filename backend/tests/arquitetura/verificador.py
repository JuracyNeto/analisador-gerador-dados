"""Verifica as regras de docs/padroes-codigo.md §1–2 lendo os imports com ast."""

import ast
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

LIMITE_LINHAS = 500
FRAMEWORKS_HTTP = frozenset({"fastapi", "pydantic", "pydantic_settings", "starlette"})
CAMADAS_COM_FRAMEWORK = frozenset({"router", "schemas"})
PREFIXO_DOMINIOS = "app.dominios."
PREFIXO_COMPARTILHADO = "app.compartilhado"
CAMADA_PUBLICA = "servico"


@dataclass(frozen=True, slots=True)
class Violacao:
    arquivo: str
    regra: str
    detalhe: str


def _nome_modulo(raiz: Path, arquivo: Path) -> str:
    partes = arquivo.relative_to(raiz).with_suffix("").parts
    return ".".join(parte for parte in partes if parte != "__init__")


def _importacoes(arquivo: Path) -> list[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nomes: list[str] = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.extend(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.extend(f"{no.module}.{alias.name}" for alias in no.names)
    return nomes


def _dominio(modulo: str) -> str | None:
    if not modulo.startswith(PREFIXO_DOMINIOS):
        return None
    return modulo.removeprefix(PREFIXO_DOMINIOS).split(".")[0]


def violacao_framework(modulo: str, importado: str) -> str | None:
    """Só router e schemas de um domínio podem usar framework HTTP/validação."""
    if _dominio(modulo) is None or modulo.rsplit(".", 1)[-1] in CAMADAS_COM_FRAMEWORK:
        return None
    if importado.split(".", maxsplit=1)[0] not in FRAMEWORKS_HTTP:
        return None
    return f"{modulo} importa {importado}; só router/schemas podem usar framework"


def violacao_entre_dominios(modulo: str, importado: str) -> str | None:
    """Um domínio só usa outro pela fachada servico.py."""
    origem, destino = _dominio(modulo), _dominio(importado)
    if origem is None or destino is None or origem == destino:
        return None
    partes = importado.removeprefix(PREFIXO_DOMINIOS).split(".")
    if len(partes) > 1 and partes[1] == CAMADA_PUBLICA:
        return None
    return f"{modulo} importa {importado}; use app.dominios.{destino}.servico"


def violacao_compartilhado(modulo: str, importado: str) -> str | None:
    """compartilhado/ não depende de domínios nem de core."""
    if not modulo.startswith(PREFIXO_COMPARTILHADO):
        return None
    if not importado.startswith(("app.dominios", "app.core")):
        return None
    return f"{modulo} importa {importado}; compartilhado não pode depender de domínio/core"


REGRAS_IMPORTACAO: tuple[Callable[[str, str], str | None], ...] = (
    violacao_framework,
    violacao_entre_dominios,
    violacao_compartilhado,
)


def _violacoes_de_tamanho(relativo: str, arquivo: Path) -> list[Violacao]:
    linhas = len(arquivo.read_text(encoding="utf-8").splitlines())
    if linhas <= LIMITE_LINHAS:
        return []
    return [Violacao(relativo, "tamanho", f"{linhas} linhas (limite {LIMITE_LINHAS})")]


def _violacoes_de_importacao(relativo: str, modulo: str, arquivo: Path) -> list[Violacao]:
    return [
        Violacao(relativo, regra.__name__, detalhe)
        for importado in _importacoes(arquivo)
        for regra in REGRAS_IMPORTACAO
        if (detalhe := regra(modulo, importado))
    ]


def verificar(raiz: Path) -> list[Violacao]:
    """Retorna todas as violações encontradas em raiz/app."""
    violacoes: list[Violacao] = []
    for arquivo in sorted((raiz / "app").rglob("*.py")):
        relativo = arquivo.relative_to(raiz).as_posix()
        violacoes += _violacoes_de_tamanho(relativo, arquivo)
        violacoes += _violacoes_de_importacao(relativo, _nome_modulo(raiz, arquivo), arquivo)
    return violacoes
