from collections.abc import Callable

import numpy as np
import pytest

from app.compartilhado.tipos import Severidade
from app.dominios.detector.regras.r01_bloco_alinhado import RegraBlocoAlinhado
from app.dominios.detector.resultados import GraficoBlocos
from tests.dominios.detector.apoio import tabela_numerica

FAMILIAS: dict[str, Callable[[np.random.Generator, int], np.ndarray]] = {
    "normal": lambda rng, n: rng.normal(70, 10, n),
    "exponencial": lambda rng, n: rng.exponential(10, n),
}


def _normal(n: int = 400, semente: int = 3) -> np.ndarray:
    return np.round(np.random.default_rng(semente).normal(70, 10, n), 2)


def alinhar_bloco(valores: np.ndarray, inicio: int, k: int) -> np.ndarray:
    """Troca as linhas do bloco por valores com a média e o DP exatos do restante (sem arredondar).

    É o que sai de gerar k valores "preservando" a coluna e anexá-los a ela.
    """
    resultado = valores.copy()
    resto = np.delete(valores, np.arange(inicio, inicio + k))
    z = np.random.default_rng(99).normal(0, 1, k)
    z = (z - z.mean()) / z.std(ddof=1)
    resultado[inicio : inicio + k] = resto.mean() + resto.std(ddof=1) * z
    return resultado


def test_bloco_com_media_e_desvio_do_restante_dispara_alta() -> None:
    valores = alinhar_bloco(_normal(), 180, 20)

    resultado = RegraBlocoAlinhado().executar(tabela_numerica(valores, nome="peso"))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R1"
    assert aviso.nome_regra == "Bloco alinhado"
    assert aviso.severidade == Severidade.ALTA
    assert aviso.colunas == ("peso",)
    assert aviso.titulo == "Bloco alinhado ao restante dos dados em peso"
    assert aviso.resumo == (
        "Um bloco de 20 linhas (181–200) tem média e desvio quase idênticos "
        "aos do restante dos dados (diferença de menos de 0,01%)."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == tuple(range(181, 201))
    assert aviso.exemplo.texto.startswith("Linhas 181 a 200: média ")
    assert " · desvio padrão " in aviso.exemplo.texto
    assert "(restante " in aviso.exemplo.texto
    grafico = aviso.grafico
    assert isinstance(grafico, GraficoBlocos)
    assert grafico.tamanho == 20
    assert len(grafico.medias) == 20
    assert grafico.linhas_do_meio[0] == 10.5
    assert grafico.alinhado[:2] == (181, 200)
    assert grafico.geral[0] == pytest.approx(valores.mean())


@pytest.mark.parametrize("familia", FAMILIAS)
@pytest.mark.parametrize("semente", range(5))
def test_bloco_igual_ao_restante_dispara_em_qualquer_amostra(familia: str, semente: int) -> None:
    """Comparado ao conjunto todo, o bloco ficava a ~1/(2n) e disparava só às vezes."""
    amostra = np.round(FAMILIAS[familia](np.random.default_rng(semente), 400), 2)

    valores = alinhar_bloco(amostra, 380, 20)

    (aviso,) = RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith("Um bloco de 20 linhas (381–400)")


@pytest.mark.parametrize(
    ("n", "inicio", "tamanho", "linhas"),
    [(242, 221, 21, "222–242"), (400, 365, 35, "366–400"), (300, 260, 40, "261–300")],
    ids=["21_anexados_com_k_12", "35_com_k_20", "40_com_k_15"],
)
def test_bloco_no_fim_dispara_com_qualquer_tamanho(
    n: int, inicio: int, tamanho: int, linhas: str
) -> None:
    """Anexar valores gerados exigia acertar k = max(10, ⌊n/20⌋); o fim vale com 10 a n/2
    linhas (D148)."""
    valores = alinhar_bloco(_normal(n), inicio, tamanho)

    (aviso,) = RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith(f"Um bloco de {tamanho} linhas ({linhas})")
    assert aviso.exemplo is not None
    assert aviso.exemplo.texto.startswith(f"Linhas {linhas.replace('–', ' a ')}: média ")


@pytest.mark.parametrize(
    ("tamanho", "achado"), [(20, True), (37, False)], ids=["com_k_linhas", "com_37_linhas"]
)
def test_bloco_no_comeco_so_e_achado_com_k_linhas(tamanho: int, achado: bool) -> None:
    """Limite (D150): o começo de qualquer tamanho tiraria força do fim, onde o Gerador anexa
    (junto com o fim), ou somaria alertas falsos (com acaso próprio)."""
    valores = alinhar_bloco(_normal(), 0, tamanho)

    avisos = RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos

    assert bool(avisos) is achado


def test_detalhes_trazem_a_simulacao() -> None:
    (aviso,) = (
        RegraBlocoAlinhado().executar(tabela_numerica(alinhar_bloco(_normal(), 180, 20))).avisos
    )

    detalhes = aviso.detalhes
    assert detalhes.teste == "Simulação: 1.000 embaralhamentos da coluna (semente fixa)"
    assert detalhes.p_valor == 0.0
    assert detalhes.p_em_palavras == "chance de acontecer por acaso: menos de 1 em 1.000"
    assert detalhes.valor == "dᵤ = 0 · dₛ = 0"
    assert detalhes.formula == (
        "dᵤ = |x̄_bloco − x̄_resto| / s_resto · dₛ = |s_bloco − s_resto| / s_resto"
    )
    assert "para o restante das linhas" in detalhes.medida
    assert detalhes.medida.startswith(
        "Janelas de 20 linhas seguidas e o fim do arquivo (de 10 a 200 linhas)"
    )


def test_exemplo_cita_o_bloco_inteiro_mesmo_com_mais_de_20_linhas() -> None:
    valores = alinhar_bloco(_normal(440), 400, 22)

    (aviso,) = RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos

    assert aviso.exemplo is not None
    assert len(aviso.exemplo.linhas) == 20
    assert aviso.exemplo.texto.startswith("Linhas 401 a 422: média ")


def test_mesma_media_aparece_igual_no_bloco_e_no_restante() -> None:
    """Média 70,125 na fronteira do arredondamento: o ruído das contas não muda o texto."""
    rng = np.random.default_rng(2)
    resto = rng.normal(70, 10, 380)
    resto = resto - resto.mean() + 70.125
    z = rng.normal(0, 1, 20)
    bloco = resto.mean() + resto.std(ddof=1) * (z - z.mean()) / z.std(ddof=1)

    (aviso,) = RegraBlocoAlinhado().executar(tabela_numerica(np.concatenate([resto, bloco]))).avisos

    assert aviso.exemplo is not None
    assert aviso.exemplo.texto.startswith(
        "Linhas 381 a 400: média 70,12 (restante 70,12) · desvio padrão "
    )


def test_normal_sem_bloco_nao_dispara() -> None:
    resultado = RegraBlocoAlinhado().executar(tabela_numerica(_normal()))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_bloco_parecido_mas_comum_ao_acaso_nao_dispara() -> None:
    """Com k grande, quase toda janela fica a menos de 1% do restante: o acaso decide."""
    valores = np.random.default_rng(1).normal(0, 1, 40_000)

    assert RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos == ()


@pytest.mark.parametrize("semente", [1575, 1816])
def test_empates_com_a_candidata_contam_como_tao_parecidos(semente: int) -> None:
    """Com poucos valores distintos, janelas embaralhadas empatam com a candidata.

    As somas acumuladas arredondam diferente conforme a posição (~10⁻¹⁶): sem contar os
    empates, 8 ou 9 embaralhamentos ficavam "tão parecidos" (p < 1%), e não 17 ou 18.
    """
    alturas = np.round(np.random.default_rng(semente).normal(1.70, 0.09, 220), 2)

    resultado = RegraBlocoAlinhado().executar(tabela_numerica(alturas))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_poucos_valores_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraBlocoAlinhado().executar(tabela_numerica(_normal(50))).nao_aplicadas

    assert nao_aplicada.regra == "R1"
    assert nao_aplicada.motivo == "precisa de 60 valores ou mais; a coluna tem 50"


def test_coluna_constante_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraBlocoAlinhado().executar(tabela_numerica([3.0] * 80)).nao_aplicadas

    assert nao_aplicada.motivo == "todos os valores são iguais"


def test_variacao_so_dentro_de_um_bloco_nao_quebra_a_regra() -> None:
    """Fora do bloco tudo igual: o DP do restante é zero e a janela não vira candidata."""
    valores = np.full(80, 3.0)
    valores[40:43] = (1.0, 5.0, 4.0)

    resultado = RegraBlocoAlinhado().executar(tabela_numerica(valores))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_bloco_tem_ao_menos_10_linhas() -> None:
    valores = alinhar_bloco(_normal(100), 40, 10)

    (aviso,) = RegraBlocoAlinhado().executar(tabela_numerica(valores)).avisos

    assert aviso.resumo.startswith("Um bloco de 10 linhas (41–50)")
