import numpy as np

from app.compartilhado.tipos import Severidade
from app.dominios.detector.regras.r01_bloco_alinhado import RegraBlocoAlinhado
from tests.dominios.detector.apoio import tabela_numerica


def _normal(n: int = 400, semente: int = 3) -> np.ndarray:
    return np.round(np.random.default_rng(semente).normal(70, 10, n), 2)


def alinhar_bloco(valores: np.ndarray, inicio: int, k: int) -> np.ndarray:
    """Troca as linhas do bloco por valores com a média e o DP exatos do conjunto final.

    Com a média do bloco igual à do resto, s² = SQ_resto / (n − k) faz o DP do bloco
    coincidir com o DP do conjunto todo.
    """
    resultado = valores.copy()
    resto = np.delete(valores, np.arange(inicio, inicio + k))
    z = np.random.default_rng(99).normal(0, 1, k)
    z = (z - z.mean()) / z.std(ddof=1)
    desvio = np.sqrt(np.sum((resto - resto.mean()) ** 2) / (len(valores) - k))
    resultado[inicio : inicio + k] = resto.mean() + desvio * z
    return resultado


def test_bloco_com_media_e_desvio_do_conjunto_dispara_alta() -> None:
    valores = alinhar_bloco(_normal(), 180, 20)

    resultado = RegraBlocoAlinhado().executar(tabela_numerica(valores, nome="peso"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R1"
    assert aviso.nome_regra == "Bloco alinhado"
    assert aviso.severidade == Severidade.ALTA
    assert aviso.colunas == ("peso",)
    assert aviso.titulo == "Bloco alinhado ao conjunto em peso"
    assert aviso.resumo == (
        "Um bloco de 20 linhas (181–200) tem média e desvio quase idênticos "
        "ao conjunto todo (diferença de menos de 0,01%)."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == tuple(range(181, 201))
    assert aviso.exemplo.texto.startswith("Linhas 181 a 200: média ")
    assert " · DP " in aviso.exemplo.texto
    assert "(geral " in aviso.exemplo.texto


def test_detalhes_trazem_a_simulacao() -> None:
    (aviso,) = (
        RegraBlocoAlinhado().executar(tabela_numerica(alinhar_bloco(_normal(), 180, 20))).avisos
    )

    detalhes = aviso.detalhes
    assert detalhes.teste == "Simulação: 1.000 embaralhamentos da coluna (semente fixa)"
    assert detalhes.p_valor == 0.0
    assert detalhes.p_em_palavras == "chance de acontecer por acaso: menos de 1 em 1.000"
    assert detalhes.formula == "dᵤ = |x̄_bloco − x̄| / s · dₛ = |s_bloco − s| / s"


def test_normal_sem_bloco_nao_dispara() -> None:
    resultado = RegraBlocoAlinhado().executar(tabela_numerica(_normal()))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_bloco_parecido_mas_comum_ao_acaso_nao_dispara() -> None:
    """Com k grande, quase toda janela fica a menos de 1% do conjunto: o acaso decide."""
    valores = np.random.default_rng(1).normal(0, 1, 40_000)

    assert RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos == ()


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraBlocoAlinhado().executar(tabela_numerica(_normal(50))).nao_aplicadas

    assert nao_aplicada.regra == "R1"
    assert nao_aplicada.motivo == "precisa de 60 valores ou mais; a coluna tem 50"


def test_coluna_constante_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraBlocoAlinhado().executar(tabela_numerica([3.0] * 80)).nao_aplicadas

    assert nao_aplicada.motivo == "todos os valores são iguais"


def test_bloco_tem_ao_menos_10_linhas() -> None:
    valores = alinhar_bloco(_normal(100), 40, 10)

    (aviso,) = RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith("Um bloco de 10 linhas (41–50)")
