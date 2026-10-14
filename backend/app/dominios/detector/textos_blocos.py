"""Textos das regras de bloco e ordem (R1, R2, R6, R10, R11; spec 16, ADR 0005).

Continua `textos.py` (que passaria de 500 linhas) com os mesmos formatadores.
"""

from collections.abc import Sequence

from app.compartilhado.numeros import (
    com_sinal_de_menos,
    formatar_fixo,
    formatar_inteiro,
    formatar_numero,
)
from app.dominios.detector import textos
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso

MENOR_PERCENTUAL = 0.01
"""Abaixo de 0,01%, a diferença aparece como "menos de 0,01%"."""
ALGARISMOS_PERCENTUAL = 2


def diferenca_percentual(fracao: float) -> str:
    """0,003 → "0,3%"; abaixo de 0,01% → "menos de 0,01%"."""
    pct = fracao * 100
    if pct < MENOR_PERCENTUAL:
        return f"menos de {formatar_numero(MENOR_PERCENTUAL)}%"
    return f"{formatar_numero(pct, ALGARISMOS_PERCENTUAL)}%"


# R1 — Bloco alinhado ------------------------------------------------------------------------


def r01_textos(coluna: str, k: int, linhas: tuple[int, int], diferenca: float) -> TextosAviso:
    """ "Um bloco de {k} linhas ({ini}–{fim}) tem média e desvio quase idênticos…" (spec 16)."""
    return TextosAviso(
        titulo=f"Bloco alinhado ao conjunto em {coluna}",
        resumo=(
            f"Um bloco de {k} linhas ({linhas[0]}–{linhas[1]}) tem média e desvio quase "
            f"idênticos ao conjunto todo (diferença de {diferenca_percentual(diferenca)})."
        ),
        por_que=(
            "Em dados reais, pedaços pequenos variam bastante; um bloco que 'bate' tudo "
            "pode ter sido colocado para alinhar as estatísticas."
        ),
        pode_ser_normal="…o conjunto foi ordenado ou amostrado de forma sistemática.",
        o_que_fazer="Confira de onde vieram essas linhas e se foram geradas ou ajustadas depois.",
    )


def r01_texto_exemplo(
    linhas: Sequence[int], bloco: tuple[float, float], geral: tuple[float, float]
) -> str:
    """ "Linhas 181 a 200: média 1,702 (geral 1,701) · DP 0,0881 (geral 0,0884)"."""
    return (
        f"{textos.faixa_de_linhas(linhas)}: média {textos.numero(bloco[0])} "
        f"(geral {textos.numero(geral[0])}) · DP {textos.numero(bloco[1])} "
        f"(geral {textos.numero(geral[1])})"
    )


def r01_detalhes(
    k: int, distancias: tuple[float, float], simulacoes: int, p: float
) -> DetalhesAviso:
    """dᵤ e dₛ da janela mais parecida e a proporção de embaralhamentos tão parecidos."""
    embaralhamentos = textos.quantidade(simulacoes, "embaralhamento", "embaralhamentos")
    return DetalhesAviso(
        medida=(
            f"Janelas de {k} linhas seguidas: diferença de média (dᵤ) e de desvio (dₛ) "
            "para o conjunto todo, em desvios padrão"
        ),
        valor=f"dᵤ = {textos.numero(distancias[0])} · dₛ = {textos.numero(distancias[1])}",
        limiar="dᵤ e dₛ < 0,01 e menos de 1% dos embaralhamentos com uma janela tão parecida",
        teste=f"Simulação: {embaralhamentos} da coluna (semente fixa)",
        formula="dᵤ = |x̄_bloco − x̄| / s · dₛ = |s_bloco − s| / s",
        p_valor=p,
        p_em_palavras=textos.p_em_palavras(p),
    )


# R2 — Correlação por blocos -----------------------------------------------------------------

CASAS_CORRELACAO = 2
BLOCO_SEM_VARIACAO = "os valores não variam em algum dos 5 blocos"


def correlacao(r: float) -> str:
    """r com 2 casas e o sinal de menos: −0,41."""
    return com_sinal_de_menos(formatar_fixo(r, CASAS_CORRELACAO))


def poucos_pares(minimo: int, n: int) -> str:
    return f"precisa de {formatar_inteiro(minimo)} pares ou mais; o par tem {formatar_inteiro(n)}"


def r02_textos(
    par: tuple[str, str], r: float, media_blocos: float, sem_bloco: tuple[int, int, float] | None
) -> TextosAviso:
    """ "A correlação geral entre {x} e {y} é {r}, mas a média dos blocos é só {rb}." (spec 16).

    Quando o que dispara é um bloco só, o resumo diz quanto r fica sem ele.
    """
    x, y = par
    if sem_bloco is None:
        contraste = f"a média dos blocos é só {correlacao(media_blocos)}"
    else:
        inicio, fim, sem = sem_bloco
        contraste = f"sem as linhas {inicio}–{fim} ela fica em {correlacao(sem)}"
    return TextosAviso(
        titulo=f"Correlação puxada em {x} e {y}",
        resumo=f"A correlação geral entre {x} e {y} é {correlacao(r)}, mas {contraste}.",
        por_que=(
            "Se poucos dados novos fazem a correlação subir muito, "
            "eles podem ter sido adicionados para 'puxar' a relação."
        ),
        pode_ser_normal="…os blocos têm faixas de valores muito diferentes.",
        o_que_fazer=(
            "Compare os blocos e confira de onde vieram as linhas que mais mudam a correlação."
        ),
    )


def r02_detalhes(
    r: float, por_bloco: Sequence[float], sem_bloco: tuple[int, int, float]
) -> DetalhesAviso:
    """r geral, r de cada bloco e r sem o bloco que mais muda a correlação."""
    blocos = "; ".join(correlacao(valor) for valor in por_bloco)
    media = correlacao(sum(por_bloco) / len(por_bloco))
    inicio, fim, sem = sem_bloco
    return DetalhesAviso(
        medida="Correlação de Pearson: geral, em cada um dos 5 blocos seguidos e sem cada bloco",
        valor=(
            f"r = {correlacao(r)} · blocos: {blocos} (média {media}) · "
            f"sem as linhas {inicio}–{fim}: {correlacao(sem)}"
        ),
        limiar=(
            "|r| passa |média dos blocos| em mais de 0,3, ou tirar um bloco baixa |r| "
            "em mais de 0,3"
        ),
        formula="r = Σ(x − x̄)(y − ȳ) / √[Σ(x − x̄)² · Σ(y − ȳ)²]",
    )
