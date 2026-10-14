import numpy as np
import pandas as pd

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r06_temporal import RegraTemporal
from app.dominios.detector.tabela import TabelaDetector
from tests.dominios.detector.apoio import tabela_de

TIPOS = {"data": TipoVariavel.DATA, "x": TipoVariavel.CONTINUA, "y": TipoVariavel.CONTINUA}


def _semanas(n: int = 100) -> pd.DatetimeIndex:
    return pd.date_range("2026-01-05", periods=n, freq="7D")


def _tabela(x: np.ndarray, y: np.ndarray, datas: pd.DatetimeIndex | None = None) -> TabelaDetector:
    dados = pd.DataFrame(
        {"data": _semanas(len(x)) if datas is None else datas, "x": np.round(x, 2), "y": y}
    )
    return tabela_de(dados, TIPOS)


def _normais(n: int = 100, semente: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(semente)
    return rng.normal(50, 10, n), np.round(rng.normal(20, 5, n), 2)


def test_segunda_metade_com_variacao_bem_menor_dispara_alta() -> None:
    x, y = _normais()
    x[50:] = 50 + (x[50:] - 50) * 0.3

    resultado = RegraTemporal().executar(_tabela(x, y))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R6"
    assert aviso.nome_regra == "Comparação temporal"
    assert aviso.severidade == Severidade.ALTA
    assert aviso.colunas == ("x",)
    assert aviso.titulo == "Variação menor depois de 14/12/2026 em x"
    assert aviso.resumo.startswith(
        "Os dados de x depois de 14/12/2026 variam bem menos em relação aos anteriores "
        "(desvio padrão "
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas[0] == 51
    assert aviso.detalhes.teste == "F de Snedecor (unilateral)"


def test_linhas_novas_que_copiam_antigas_disparam_alta() -> None:
    x, y = _normais()
    copiadas = [55, 61, 70, 77, 84, 93]
    x[copiadas], y[copiadas] = x[[3, 10, 18, 25, 31, 44]], y[[3, 10, 18, 25, 31, 44]]

    (aviso,) = RegraTemporal().executar(_tabela(x, y)).avisos

    assert aviso.colunas == ()
    assert aviso.titulo == "Linhas novas repetem linhas antigas"
    assert aviso.resumo == (
        "Os dados depois de 14/12/2026 copiam os anteriores: 6 das 50 linhas novas (12%) "
        "são iguais a linhas de antes, fora a data."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (56, 62, 71, 78, 85, 94)
    assert aviso.exemplo.texto == (
        "Linhas 56, 62, 71, 78, 85 e 94: iguais às linhas 4, 11, 19, 26, 32 e 45, fora a data"
    )


def test_ordem_das_linhas_nao_importa_so_a_data() -> None:
    x, y = _normais()
    x[50:] = 50 + (x[50:] - 50) * 0.3
    ordem = np.random.default_rng(1).permutation(100)

    resultado = RegraTemporal().executar(_tabela(x[ordem], y[ordem], _semanas()[ordem]))

    assert [aviso.colunas for aviso in resultado.avisos] == [("x",)]


def test_dados_parecidos_no_tempo_nao_disparam() -> None:
    resultado = RegraTemporal().executar(_tabela(*_normais()))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_poucos_valores_distintos_repetem_ao_acaso_e_nao_disparam() -> None:
    rng = np.random.default_rng(2)
    dados = pd.DataFrame({"data": _semanas(), "nota": rng.integers(1, 4, 100)})

    tabela = tabela_de(dados, {"data": TipoVariavel.DATA, "nota": TipoVariavel.DISCRETA})

    assert RegraTemporal().executar(tabela).avisos == ()


def test_sem_coluna_de_data_a_regra_nao_se_aplica() -> None:
    tabela = tabela_de(pd.DataFrame({"x": np.arange(50.0)}), {"x": TipoVariavel.CONTINUA})

    resultado = RegraTemporal().executar(tabela)

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.frase == (
        "Comparação temporal não verificada: o arquivo não tem uma coluna de data."
    )
    assert not resultado.verificada


def test_poucas_linhas_nao_se_aplica() -> None:
    x, y = _normais(30)

    nao_aplicadas = RegraTemporal().executar(_tabela(x, y)).nao_aplicadas

    assert {(n.coluna, n.motivo) for n in nao_aplicadas} == {
        ("x", "precisa de 40 valores ou mais; a coluna tem 30"),
        ("y", "precisa de 40 valores ou mais; a coluna tem 30"),
        (None, "precisa de 40 linhas ou mais; o arquivo tem 30"),
    }


def test_datas_que_nao_se_dividem_em_dois_periodos_nao_se_aplicam() -> None:
    x, y = _normais(60)
    datas = pd.DatetimeIndex([pd.Timestamp("2026-03-01")] * 55 + list(_semanas(5)))

    nao_aplicadas = RegraTemporal().executar(_tabela(x, y, datas)).nao_aplicadas

    assert {n.motivo for n in nao_aplicadas} == {
        "precisa de 10 linhas ou mais antes e depois da data do meio"
    }


def _duas_datas(primeira: pd.DatetimeIndex, segunda: pd.DatetimeIndex, x: np.ndarray) -> object:
    dados = pd.DataFrame({"nascimento": primeira, "dia": segunda, "x": np.round(x, 2)})
    tipos = {
        "nascimento": TipoVariavel.DATA,
        "dia": TipoVariavel.DATA,
        "x": TipoVariavel.CONTINUA,
    }
    return tabela_de(dados, tipos)


def test_usa_a_coluna_de_data_que_acompanha_a_ordem_das_linhas() -> None:
    """Num cadastro com nascimento e dia do registro, a linha do tempo é o dia (D130)."""
    x, _ = _normais()
    x[50:] = 50 + (x[50:] - 50) * 0.3
    nascimentos = pd.DatetimeIndex(
        np.random.default_rng(5).permutation(pd.date_range("1960-01-01", periods=100, freq="90D"))
    )

    (aviso,) = RegraTemporal().executar(_duas_datas(nascimentos, _semanas(), x)).avisos

    assert aviso.titulo == "Variação menor depois de 14/12/2026 em x"
    assert aviso.detalhes.medida == (
        "Desvio padrão antes e depois de 14/12/2026 (data do meio de dia)"
    )


def test_sem_data_que_acompanhe_as_linhas_usa_a_primeira() -> None:
    rng = np.random.default_rng(6)
    ordem = rng.permutation(100)
    primeira = _semanas()[ordem]
    x, _ = _normais()
    x[ordem >= 50] = 50 + (x[ordem >= 50] - 50) * 0.3
    segunda = pd.DatetimeIndex(rng.permutation(_semanas()))

    (aviso,) = RegraTemporal().executar(_duas_datas(primeira, segunda, x)).avisos

    assert aviso.detalhes.medida.endswith("(data do meio de nascimento)")
