"""Fachada do domínio graficos: figuras por tipo e HTML para o relatório (spec 08).

Sem estado nem dependências: funções simples (a classe de fachada da D54 só vale para domínios
com estado ou que dependem de outros).
"""

import html
import json
import re
from collections.abc import Mapping
from importlib import resources
from typing import Any

from app.dominios.graficos.entradas import (
    Barra,
    BinomialFigura,
    CurvaFigura,
    DadosBivariados,
    DadosForma,
    DadosMatriz,
    DadosUnivariados,
    FiguraPronta,
    QQFigura,
)
from app.dominios.graficos.fabrica import (
    figura_matriz,
    figuras_bivariadas,
    figuras_forma,
    figuras_univariadas,
)
from app.dominios.graficos.tema import CORES_CLARAS, colorir, layout_claro, mesclar

__all__ = [
    "Barra",
    "BinomialFigura",
    "CurvaFigura",
    "DadosBivariados",
    "DadosForma",
    "DadosMatriz",
    "DadosUnivariados",
    "FiguraPronta",
    "QQFigura",
    "codigo_plotlyjs",
    "endereco_plotlyjs_cdn",
    "figura_html",
    "figura_matriz",
    "figuras_bivariadas",
    "figuras_forma",
    "figuras_univariadas",
]

CONFIG_RELATORIO = {"displaylogo": False, "responsive": True}
ARQUIVO_PLOTLYJS = ("plotly", "package_data", "plotly.min.js")
_VERSAO = re.compile(r"plotly\.js v(\d+\.\d+\.\d+)")
ESCAPE_FECHAMENTO = r"<\/"


def figura_html(identificador: str, dados: Mapping[str, Any]) -> str:
    """<div> + <script> que desenha a figura com o tema claro (o plotly.js entra uma vez só)."""
    figura = {
        "data": colorir(dict(dados), CORES_CLARAS)["data"],
        "layout": mesclar(layout_claro(), dict(dados.get("layout", {}))),
    }
    argumentos = ", ".join(
        json.dumps(parte, ensure_ascii=False)
        for parte in (identificador, figura["data"], figura["layout"], CONFIG_RELATORIO)
    )
    # "</" dentro de um <script> fecharia a tag antes da hora.
    seguro = argumentos.replace("</", ESCAPE_FECHAMENTO)
    alvo = html.escape(identificador)
    return f'<div id="{alvo}" class="grafico"></div>\n<script>Plotly.newPlot({seguro});</script>'


def codigo_plotlyjs() -> str:
    """plotly.js que acompanha o pacote Python, para o relatório funcionar sem internet."""
    pasta, *resto = ARQUIVO_PLOTLYJS
    return resources.files(pasta).joinpath(*resto).read_text(encoding="utf-8")


def endereco_plotlyjs_cdn() -> str:
    """Endereço da mesma versão do plotly.js no CDN oficial."""
    casamento = _VERSAO.search(codigo_plotlyjs()[:200])
    versao = casamento.group(1) if casamento else "latest"
    return f"https://cdn.plot.ly/plotly-{versao}.min.js"
