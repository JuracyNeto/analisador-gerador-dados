import json

import numpy as np
import plotly.graph_objects as go

from app.dominios.graficos import textos
from app.dominios.graficos.servico import (
    DadosBlocos,
    DadosDigitos,
    figura_benford,
    figura_blocos,
    figura_ultimo_digito,
)
from app.dominios.graficos.tema import PAPEL_PRINCIPAL, PAPEL_REFERENCIA

BLOCOS = DadosBlocos(
    coluna="altura_m",
    k=20,
    x=tuple(10.5 + 20 * i for i in range(20)),
    medias=tuple(1.70 + 0.01 * np.sin(np.arange(20))),
    media=1.701,
    desvio=0.0884,
    destaque_linhas=(181, 200),
    destaque_media=1.701,
)
BENFORD = np.log10(1 + 1 / np.arange(1, 10))


def test_media_por_bloco_com_faixa_e_bloco_destacado() -> None:
    figura = figura_blocos(BLOCOS)

    go.Figure(figura.dados)
    tracos = figura.dados["data"]
    assert [t["name"] for t in tracos] == [
        "Média de cada bloco",
        "Média geral",
        "Média ± 1 desvio padrão",
        "Média ± 1 desvio padrão",
        "Bloco alinhado (linhas 181–200)",
    ]
    assert [t["meta"] for t in tracos] == [PAPEL_PRINCIPAL] + [PAPEL_REFERENCIA] * 4
    assert tracos[2]["y"] == [1.701 + 0.0884] * 2
    assert tracos[4]["x"] == [190.5]
    assert figura.titulo == "Média de altura_m por bloco de 20 linhas"
    assert figura.resumo == "A média das linhas 181–200 fica em cima da média geral (1,701)."
    assert figura.id == "blocos"
    assert figura.recomendado


def test_benford_compara_observado_e_esperado() -> None:
    observadas = (0.12, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11)
    dados = DadosDigitos("vendas", tuple(range(1, 10)), observadas, tuple(BENFORD))

    figura = figura_benford(dados)

    go.Figure(figura.dados)
    observado, esperado = figura.dados["data"]
    assert observado["type"] == "bar"
    assert observado["meta"] == PAPEL_PRINCIPAL
    assert esperado["meta"] == PAPEL_REFERENCIA
    assert esperado["name"] == "Lei de Benford"
    assert observado["y"][0] == 12.0
    assert figura.titulo == "1º dígito de vendas: observado × Benford"
    assert figura.resumo == "O 9 abre 11% dos valores; pela Lei de Benford seriam 4,6%."


def test_ultimo_digito_com_a_linha_de_10_porcento() -> None:
    observadas = (0.24,) + (0.76 / 9,) * 9
    dados = DadosDigitos("idade", tuple(range(10)), observadas, (0.1,) * 10)

    figura = figura_ultimo_digito(dados)

    go.Figure(figura.dados)
    barras, esperado = figura.dados["data"]
    assert barras["x"] == [str(d) for d in range(10)]
    assert esperado["name"] == "Esperado (10%)"
    assert esperado["line"]["dash"] == "dash"
    assert figura.titulo == "Último dígito de idade"
    assert figura.resumo == "O 0 aparece em 24% dos valores; o esperado é 10%."


def test_figuras_do_detector_sao_leves() -> None:
    for figura in (figura_blocos(BLOCOS), figura_benford(DadosDigitos("x", (1,), (1.0,), (1.0,)))):
        assert len(json.dumps(figura.dados, ensure_ascii=False)) < 5_000


def test_textos_do_bloco_com_ponto_de_milhar_nas_linhas() -> None:
    """Os números de linha seguem os do detector ("Linhas 1.181 a 1.200"; T4 do M4.3)."""
    assert textos.resumo_blocos((1181, 1200), 1.701) == (
        "A média das linhas 1.181–1.200 fica em cima da média geral (1,701)."
    )
    assert textos.nome_bloco_destacado((1181, 1200)) == "Bloco alinhado (linhas 1.181–1.200)"
