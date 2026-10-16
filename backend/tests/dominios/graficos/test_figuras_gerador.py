import json

import numpy as np
import pandas as pd

from app.dominios.graficos.servico import (
    DadosParesGerados,
    DadosSobreposicao,
    figura_pares_gerados,
    figura_sobreposicao_categorica,
    figura_sobreposicao_numerica,
)
from app.dominios.graficos.tema import PAPEL_PRINCIPAL, PAPEL_REFERENCIA

RNG = np.random.default_rng(11)
ORIGINAL = pd.Series(np.round(RNG.normal(70, 11, 227), 1))


def test_sobreposicao_numerica_com_um_milhao_de_valores_fica_leve() -> None:
    gerado = pd.Series(RNG.normal(70, 11, 1_000_000))
    dados = DadosSobreposicao("peso_kg", gerado, ORIGINAL, len(ORIGINAL))

    figura = figura_sobreposicao_numerica(dados)

    assert len(json.dumps(figura.dados)) < 50_000
    tracos = figura.dados["data"]
    assert [t["meta"] for t in tracos] == [PAPEL_PRINCIPAL, PAPEL_REFERENCIA]
    assert tracos[0]["name"] == "Original (n = 227)"
    assert tracos[1]["name"] == "Gerado (n = 1.000.000)"
    assert figura.dados["layout"]["barmode"] == "overlay"
    assert figura.titulo == "peso_kg: original e gerado sobrepostos"
    assert figura.resumo == "As duas distribuições têm formas parecidas."
    assert abs(sum(tracos[1]["y"]) - 100) < 1e-6


def test_sobreposicao_sem_origem_so_tem_o_gerado() -> None:
    figura = figura_sobreposicao_numerica(DadosSobreposicao("valor", ORIGINAL))

    assert len(figura.dados["data"]) == 1
    assert figura.titulo == "valor: valores gerados"
    assert figura.resumo == "Distribuição dos 227 valores gerados."


def test_sobreposicao_categorica_agrupa_por_categoria() -> None:
    original = pd.Series(["a"] * 50 + ["b"] * 50)
    gerado = pd.Series(["a"] * 90 + ["b"] * 5 + ["c"] * 5)

    figura = figura_sobreposicao_categorica(DadosSobreposicao("cat", gerado, original, 100))

    tracos = figura.dados["data"]
    assert tracos[0]["x"] == ["a", "b", "c"]
    assert tracos[0]["y"] == [50.0, 50.0, 0.0]
    assert figura.dados["layout"]["barmode"] == "group"
    assert figura.resumo == "As distribuições diferem em alguns trechos."


def test_pares_gerados_com_originais() -> None:
    x = tuple(float(v) for v in RNG.normal(0, 1, 6000))
    dados = DadosParesGerados("altura_m", "peso_kg", x, x, 0.7, x[:100], x[:100])

    figura = figura_pares_gerados(dados)

    tracos = figura.dados["data"]
    assert [t["meta"] for t in tracos] == [PAPEL_PRINCIPAL, PAPEL_REFERENCIA]
    assert len(tracos[1]["x"]) == 5000
    assert figura.titulo == "Pares gerados (n = 6.000)"
    assert figura.resumo == "Correlação obtida: r = 0,7. Mostramos 5.000 dos 6.000 pontos."
