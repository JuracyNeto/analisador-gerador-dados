import numpy as np
import pandas as pd

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r02_correlacao_blocos import RegraCorrelacaoBlocos
from tests.dominios.detector.apoio import tabela_de

CONTINUAS = {"x": TipoVariavel.CONTINUA, "y": TipoVariavel.CONTINUA}


def _pares(n: int, rho: float, semente: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(semente)
    x = rng.normal(0, 1, n)
    y = rho * x + np.sqrt(1 - rho**2) * rng.normal(0, 1, n)
    return x, y


def _tabela(x: np.ndarray, y: np.ndarray) -> object:
    return tabela_de(pd.DataFrame({"x": np.round(x, 2), "y": np.round(y, 2)}), CONTINUAS)


def _puxada() -> tuple[np.ndarray, np.ndarray]:
    """100 pares com r ≈ 0,3 e 25 pares finais alinhados numa faixa mais larga."""
    x, y = _pares(100, 0.3, 1)
    final = np.linspace(-4, 4, 25)
    ruido = np.random.default_rng(2).normal(0, 0.1, 25)
    return np.concatenate([x, final]), np.concatenate([y, final + ruido])


def test_bloco_final_que_puxa_a_correlacao_dispara_alta() -> None:
    resultado = RegraCorrelacaoBlocos().executar(_tabela(*_puxada()))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R2"
    assert aviso.nome_regra == "Correlação por blocos"
    assert aviso.severidade == Severidade.ALTA
    assert aviso.colunas == ("x", "y")
    assert aviso.titulo == "Correlação puxada em x e y"
    assert aviso.resumo.startswith("A correlação geral entre x e y é 0,")
    assert ", mas a média dos blocos é só 0," in aviso.resumo
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == tuple(range(101, 121))
    assert aviso.exemplo.texto.startswith("Linhas 101 a 120: −4 · −")
    assert aviso.detalhes.formula == "r = Σ(x − x̄)(y − ȳ) / √[Σ(x − x̄)² · Σ(y − ȳ)²]"


def test_correlacao_negativa_puxada_tambem_dispara() -> None:
    x, y = _puxada()

    (aviso,) = RegraCorrelacaoBlocos().executar(_tabela(x, -y)).avisos

    assert aviso.resumo.startswith("A correlação geral entre x e y é −0,")


def test_correlacao_homogenea_nao_dispara() -> None:
    resultado = RegraCorrelacaoBlocos().executar(_tabela(*_pares(300, 0.7, 4)))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_bloco_que_muda_a_correlacao_dispara_pela_remocao() -> None:
    """Blocos com r ≈ 0,6 e um bloco largo e alinhado: a média dos blocos fica perto de r,
    mas sem esse bloco r cai mais de 0,3."""
    x, y = _pares(240, 0.6, 5)
    x[:48] = np.linspace(-8, 8, 48)
    y[:48] = x[:48] + np.random.default_rng(9).normal(0, 0.1, 48)

    (aviso,) = RegraCorrelacaoBlocos().executar(_tabela(x, y)).avisos

    assert ", mas sem as linhas 1–48 ela fica em 0," in aviso.resumo
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas[0] == 1


def test_todos_os_pares_de_numericas_sao_examinados() -> None:
    x, y = _pares(80, 0.5, 6)
    dados = pd.DataFrame({"a": x, "b": y, "c": x + y, "nome": ["p"] * 80})
    tipos = {
        "a": TipoVariavel.CONTINUA,
        "b": TipoVariavel.CONTINUA,
        "c": TipoVariavel.DISCRETA,
        "nome": TipoVariavel.NOMINAL,
    }

    resultado = RegraCorrelacaoBlocos().executar(tabela_de(dados, tipos))

    assert resultado.verificada
    assert resultado.nao_aplicadas == ()


def test_poucos_pares_nao_se_aplica() -> None:
    x, y = _pares(50, 0.5, 7)

    (nao_aplicada,) = RegraCorrelacaoBlocos().executar(_tabela(x, y)).nao_aplicadas

    assert nao_aplicada.coluna == "x e y"
    assert nao_aplicada.frase == (
        "Correlação por blocos não verificada em x e y: precisa de 60 pares ou mais; o par tem 50."
    )


def test_bloco_sem_variacao_nao_se_aplica() -> None:
    x, y = _pares(100, 0.5, 8)
    x[:20] = 1.0

    (nao_aplicada,) = RegraCorrelacaoBlocos().executar(_tabela(x, y)).nao_aplicadas

    assert nao_aplicada.motivo == "os valores não variam em algum dos 5 blocos"


def test_sem_duas_numericas_a_regra_nao_se_aplica_ao_arquivo() -> None:
    tabela = tabela_de(pd.DataFrame({"x": np.arange(80.0)}), {"x": TipoVariavel.CONTINUA})

    (nao_aplicada,) = RegraCorrelacaoBlocos().executar(tabela).nao_aplicadas

    assert nao_aplicada.coluna is None
    assert nao_aplicada.motivo == "o arquivo não tem duas colunas numéricas"


def test_valor_digitado_errado_que_derruba_r_nao_dispara() -> None:
    """r geral perto de 0 e blocos com r ≈ 0,6: a correlação geral é mais fraca, não puxada."""
    x, y = _pares(230, 0.6, 10)
    x[76] = 120.0

    assert RegraCorrelacaoBlocos().executar(_tabela(x, y)).avisos == ()


def test_relacao_que_muda_numa_serie_no_tempo_fica_em_atencao() -> None:
    # Temperatura mínima × média: a relação muda com as estações do ano (D137).
    x, y = _puxada()
    dados = pd.DataFrame(
        {"dia": pd.date_range("2025-01-01", periods=len(x)), "x": np.round(x, 2), "y": y}
    )
    tipos = {"dia": TipoVariavel.DATA} | CONTINUAS

    (aviso,) = RegraCorrelacaoBlocos().executar(tabela_de(dados, tipos)).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.pode_ser_normal == (
        "…a relação muda com o tempo (as linhas seguem a coluna dia; ex.: estações do ano)."
    )
