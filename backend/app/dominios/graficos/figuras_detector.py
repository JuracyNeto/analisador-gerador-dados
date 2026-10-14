"""Figuras do detector (spec 08, D123): média por bloco (R1), Benford (R8) e último dígito (R9).

Só valores agregados (uma média por bloco, uma barra por dígito): a figura fica leve com
qualquer tamanho de arquivo (ADR 0003).
"""

from typing import Any

from app.dominios.graficos.entradas import DadosBlocos, DadosDigitos
from app.dominios.graficos.figuras import LARGURA_LINHA, MARCADOR_BARRA, Figura, figura_basica
from app.dominios.graficos.tema import PAPEL_PRINCIPAL, PAPEL_REFERENCIA

PERCENTUAL = 100
CASAS_PERCENTUAL = 6
TAMANHO_DESTAQUE = 12
EIXO_BLOCOS = "Linha (meio do bloco)"
EIXO_PERCENTUAL = "Frequência (%)"


def _horizontal(pontas: list[float], altura: float, nome: str, traco: str) -> dict[str, Any]:
    return {
        "type": "scatter",
        "mode": "lines",
        "x": pontas,
        "y": [altura, altura],
        "name": nome,
        "meta": PAPEL_REFERENCIA,
        "line": {"width": 1.5, "dash": traco},
    }


def _com_legenda(figura: Figura) -> Figura:
    figura["layout"]["showlegend"] = True
    return figura


def media_por_bloco(dados: DadosBlocos, destaque: str) -> Figura:
    """Linha da média de cada bloco, média geral, faixa x̄ ± s e o bloco destacado."""
    pontas = [dados.x[0], dados.x[-1]]
    inicio, fim = dados.destaque_linhas
    tracos = [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "x": list(dados.x),
            "y": list(dados.medias),
            "name": "Média de cada bloco",
            "meta": PAPEL_PRINCIPAL,
            "line": {"width": LARGURA_LINHA},
        },
        _horizontal(pontas, dados.media, "Média geral", "solid"),
        _horizontal(pontas, dados.media + dados.desvio, "Média ± 1 desvio padrão", "dash"),
        _horizontal(pontas, dados.media - dados.desvio, "Média ± 1 desvio padrão", "dash")
        | {"showlegend": False},
        {
            "type": "scatter",
            "mode": "markers",
            "x": [(inicio + fim) / 2],
            "y": [dados.destaque_media],
            "name": destaque,
            "meta": PAPEL_REFERENCIA,
            "marker": {"size": TAMANHO_DESTAQUE, "symbol": "diamond"},
        },
    ]
    return _com_legenda(figura_basica(tracos, EIXO_BLOCOS, dados.coluna))


def _percentuais(proporcoes: tuple[float, ...]) -> list[float]:
    return [round(PERCENTUAL * valor, CASAS_PERCENTUAL) for valor in proporcoes]


def observado_esperado(dados: DadosDigitos, eixo_x: str, nome_esperado: str) -> Figura:
    """Barras da frequência observada de cada dígito e a linha do esperado."""
    digitos = [str(digito) for digito in dados.digitos]
    tracos = [
        {
            "type": "bar",
            "x": digitos,
            "y": _percentuais(dados.observadas),
            "name": "Observado",
            "meta": PAPEL_PRINCIPAL,
            "marker": MARCADOR_BARRA,
        },
        {
            "type": "scatter",
            "mode": "lines+markers",
            "x": digitos,
            "y": _percentuais(dados.esperadas),
            "name": nome_esperado,
            "meta": PAPEL_REFERENCIA,
            "line": {"width": LARGURA_LINHA, "dash": "dash"},
        },
    ]
    return _com_legenda(figura_basica(tracos, eixo_x, EIXO_PERCENTUAL))
