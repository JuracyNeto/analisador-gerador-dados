import numpy as np
import pandas as pd
import pytest

from app.dominios.analise.servico import ServicoAnalise
from app.dominios.gerador.comparacao import (
    MedidasPar,
    comparar_categoricos,
    comparar_numericos,
    comparar_pares,
)


def test_comparar_numericos_na_ordem_com_diferenca_absoluta() -> None:
    original = ServicoAnalise.resumo_numerico(np.array([60.0, 70, 80, 90]))
    gerado = ServicoAnalise.resumo_numerico(np.array([61.0, 71, 79, 92]))

    linhas = comparar_numericos(original, gerado)

    assert [linha.estatistica for linha in linhas] == [
        "n",
        "Média",
        "Mediana",
        "Desvio padrão",
        "Mínimo",
        "Máximo",
        "Assimetria",
        "Curtose",
    ]
    media = linhas[1]
    assert media.diferenca == pytest.approx(media.gerado - media.original)
    assert linhas[4].diferenca == pytest.approx(1.0)


def test_comparar_numericos_sem_origem() -> None:
    gerado = ServicoAnalise.resumo_numerico(np.array([1.0, 2, 3, 4, 5]))

    linhas = comparar_numericos(None, gerado)

    assert all(linha.original is None for linha in linhas)
    assert all(linha.diferenca is None for linha in linhas)


def test_comparar_categoricos_em_pontos_percentuais() -> None:
    original = pd.Series(["F", "F", "M", "M"])
    gerado = pd.Series(["F", "M", "M", "M"])

    linhas = comparar_categoricos(original, gerado)

    assert linhas[0].estatistica == "n"
    feminino = next(linha for linha in linhas if linha.estatistica == "fr% · F")
    assert (feminino.original, feminino.gerado, feminino.diferenca) == (50.0, 25.0, -25.0)


def test_comparar_categoricos_categoria_que_nao_saiu() -> None:
    linhas = comparar_categoricos(pd.Series(["a", "b", "c"]), pd.Series(["a", "a"]))

    sem_sorteio = next(linha for linha in linhas if linha.estatistica == "fr% · c")
    assert sem_sorteio.gerado == 0.0


def test_comparar_pares_sem_origem_usa_o_alvo() -> None:
    alvo = MedidasPar(100, 1.7, 70.0, 0.09, 11.0, 0.7)
    gerado = MedidasPar(100, 1.7, 70.0, 0.09, 11.0, 0.7)

    linhas = comparar_pares("altura_m", "peso_kg", alvo, gerado)

    assert linhas[-1].estatistica == "Correlação (r)"
    assert linhas[1].estatistica == "Média de altura_m"
    assert linhas[-1].diferenca == pytest.approx(0.0)
