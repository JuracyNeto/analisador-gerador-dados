"""Monta o HTML do relatório com Jinja2 (spec 13): arquivo único, CSS embutido."""

from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.dominios.relatorio.conteudo import ConteudoRelatorio
from app.dominios.relatorio.textos import TITULOS_SECOES

PASTA_TEMPLATES = Path(__file__).parent / "templates"
TEMPLATE = "relatorio.html.j2"


@lru_cache
def _ambiente() -> Environment:
    return Environment(
        loader=FileSystemLoader(PASTA_TEMPLATES),
        autoescape=select_autoescape(enabled_extensions=("html", "j2"), default=True),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def renderizar(conteudo: ConteudoRelatorio) -> str:
    """HTML completo; textos são escapados, só figuras e o script do Plotly entram como estão."""
    return _ambiente().get_template(TEMPLATE).render(c=conteudo, titulos=TITULOS_SECOES)
