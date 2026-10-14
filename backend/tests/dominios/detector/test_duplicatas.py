import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.detector.duplicatas import (
    SEM_PARES,
    ColunasComparaveis,
    ContraOAcaso,
    GrupoRepetido,
    acaso_das_repeticoes,
    chaves_das_colunas,
    pares_quase_iguais,
    repetidos,
    seguidas_contra_o_acaso,
)
from tests.dominios.detector.apoio import tabela_de

TIPOS = {
    "a": TipoVariavel.CONTINUA,
    "c": TipoVariavel.CONTINUA,
    "b": TipoVariavel.NOMINAL,
    "d": TipoVariavel.NOMINAL,
}
type Dados = dict[str, list[float | str | None]]


def _chaves(dados: Dados) -> ColunasComparaveis:
    tipos = {nome: TIPOS[nome] for nome in dados}
    tabela = tabela_de(pd.DataFrame(dados), tipos)
    return chaves_das_colunas(tuple(tabela.colunas.values()))


def _posicoes(grupos: tuple[GrupoRepetido, ...]) -> list[list[int]]:
    return [grupo.posicoes.tolist() for grupo in grupos]


def _com_copia_quase_igual() -> Dados:
    """20 linhas; a 16ª repete a 4ª com 0,001 a mais em `a`."""
    a: list[float | str | None] = [float(v) for v in range(1, 21)]
    c: list[float | str | None] = [100.0 + 3 * v for v in range(20)]
    b: list[float | str | None] = ["x", "y"] * 10
    a[15], c[15], b[15] = 4.001, c[3], b[3]
    return {"a": a, "c": c, "b": b}


def _aleatorias(semente: int, n: int = 500) -> Dados:
    rng = np.random.default_rng(semente)
    return {
        "a": list(np.round(rng.normal(50, 10, n), 2)),
        "c": list(np.round(rng.normal(170, 8, n), 2)),
    }


def _acaso(dados: Dados) -> tuple[np.ndarray, ContraOAcaso, ContraOAcaso]:
    chaves = _chaves(dados)
    quase = pares_quase_iguais(chaves)
    acaso = acaso_das_repeticoes(chaves, repetidos(chaves, SEM_PARES), quase)
    return quase, acaso.iguais, acaso.quase


def test_linhas_identicas_formam_um_grupo() -> None:
    chaves = _chaves({"a": [1.0, 2.0, 1.0, 3.0, 2.0], "b": ["x", "y", "x", "x", "z"]})

    assert _posicoes(repetidos(chaves, SEM_PARES)) == [[0, 2]]


def test_faltantes_iguais_contam_como_iguais() -> None:
    chaves = _chaves({"a": [None, 2.0, None], "b": [None, "y", None]})

    assert _posicoes(repetidos(chaves, SEM_PARES)) == [[0, 2]]


def test_pares_quase_iguais_dados_entram_nos_grupos() -> None:
    chaves = _chaves(_com_copia_quase_igual())

    grupos = repetidos(chaves, np.array([[3, 15]]))

    assert _posicoes(grupos) == [[3, 15]]
    assert not grupos[0].exato


def test_copia_quase_igual_passa_do_acaso() -> None:
    quase, _, acaso = _acaso(_com_copia_quase_igual())

    assert quase.tolist() == [[3, 15]]
    assert acaso.p_valor < 0.01


def test_quase_iguais_precisam_ter_as_demais_colunas_iguais() -> None:
    dados = _com_copia_quase_igual()
    dados["b"][15] = "z"

    assert len(pares_quase_iguais(_chaves(dados))) == 0


@pytest.mark.parametrize("semente", [3, 4, 5])
def test_com_duas_colunas_aleatorias_parecidas_e_iguais_sao_acaso(semente: int) -> None:
    quase, iguais, acaso_quase = _acaso(_aleatorias(semente))

    assert len(quase) > 0
    assert acaso_quase.p_valor > 0.01
    assert iguais.p_valor > 0.01


def test_copias_plantadas_em_colunas_aleatorias_passam_do_acaso() -> None:
    dados = _aleatorias(3)
    for coluna in ("a", "c"):
        dados[coluna][400:410] = dados[coluna][100:110]

    _, iguais, _ = _acaso(dados)

    assert iguais.observados >= 10
    assert iguais.p_valor < 0.01


def test_sem_colunas_numericas_o_acaso_supoe_colunas_independentes() -> None:
    """Duas colunas 2/2: P(coincidir) = 4/12 em cada; C(4,2)·(1/3)² pares iguais por acaso."""
    _, iguais, quase = _acaso({"b": ["x", "x", "y", "y"], "d": ["1", "2", "1", "2"]})

    assert iguais.observados == 0
    assert iguais.esperados == pytest.approx(6 * (4 / 12) ** 2)
    assert quase == ContraOAcaso(0, 0.0)


def test_p_valor_do_poisson() -> None:
    assert ContraOAcaso(0, 2.0).p_valor == 1.0
    assert ContraOAcaso(1, 0.0).p_valor == 0.0
    assert 0.3 < ContraOAcaso(1, 0.5).p_valor < 0.4


def test_tres_seguidas_sao_improvaveis_com_poucas_repeticoes() -> None:
    grupos = (GrupoRepetido(np.array([10, 11, 12]), exato=True),)

    acaso = seguidas_contra_o_acaso(grupos, 200)

    assert acaso.observados == 1
    assert acaso.esperados == pytest.approx(6 / (200 * 199))
    assert acaso.p_valor < 0.001


def test_maior_sequencia_de_linhas_seguidas() -> None:
    grupo = GrupoRepetido(np.array([2, 10, 11, 12, 30]), exato=True)

    assert grupo.maior_sequencia.tolist() == [10, 11, 12]
    assert grupo.copias == 4
