"""Textos das regras de bloco e ordem (R1, R2, R6, R10, R11; spec 16, ADR 0005).

Continua `textos.py` (que passaria de 500 linhas) com os mesmos formatadores.
"""

from collections.abc import Sequence

from app.compartilhado.numeros import (
    formatar_fixo,
    formatar_inteiro,
    formatar_numero,
)
from app.compartilhado.textos import p_valor_em_palavras, pluralizar
from app.dominios.detector import textos
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso

MENOR_PERCENTUAL = 0.01
"""Abaixo de 0,01%, a diferença aparece como "menos de 0,01%"."""
ALGARISMOS_PERCENTUAL = 2
CASAS_DISTANCIA = 6


def diferenca_percentual(fracao: float) -> str:
    """0,003 → "0,3%"; abaixo de 0,01% → "menos de 0,01%"."""
    pct = fracao * 100
    if pct < MENOR_PERCENTUAL:
        return f"menos de {formatar_numero(MENOR_PERCENTUAL)}%"
    return f"{formatar_numero(pct, ALGARISMOS_PERCENTUAL)}%"


# R1 — Bloco alinhado ------------------------------------------------------------------------


def r01_textos(coluna: str, k: int, linhas: tuple[int, int], diferenca: float) -> TextosAviso:
    """ "Um bloco de {k} linhas ({ini}–{fim}) tem média e desvio quase idênticos aos do
    restante dos dados…" (spec 16, D142)."""
    return TextosAviso(
        titulo=f"Bloco alinhado ao restante dos dados em {coluna}",
        resumo=(
            f"Um bloco de {k} linhas ({linhas[0]}–{linhas[1]}) tem média e desvio quase "
            f"idênticos aos do restante dos dados (diferença de {diferenca_percentual(diferenca)})."
        ),
        por_que=(
            "Em dados reais, pedaços pequenos variam bastante; um bloco que 'bate' tudo "
            "pode ter sido colocado para alinhar as estatísticas."
        ),
        pode_ser_normal="…o conjunto foi ordenado ou amostrado de forma sistemática.",
        o_que_fazer="Confira de onde vieram essas linhas e se foram geradas ou ajustadas depois.",
    )


def r01_texto_exemplo(
    linhas: tuple[int, int], bloco: tuple[float, float], resto: tuple[float, float]
) -> str:
    """ "Linhas 401 a 421: média 71,12 (resto 71,12) · DP 11,94 (resto 11,94)"."""
    return (
        f"Linhas {linhas[0]} a {linhas[1]}: média {textos.numero(bloco[0])} "
        f"(resto {textos.numero(resto[0])}) · DP {textos.numero(bloco[1])} "
        f"(resto {textos.numero(resto[1])})"
    )


def distancia(valor: float) -> str:
    """dᵤ ou dₛ sem o ruído das contas: abaixo de 0,000001 vira 0."""
    return textos.numero(round(valor, CASAS_DISTANCIA))


def r01_detalhes(
    tamanhos: tuple[int, int, int], distancias: tuple[float, float], simulacoes: int, p: float
) -> DetalhesAviso:
    """dᵤ e dₛ do trecho mais parecido com o restante e a proporção de embaralhamentos.

    `tamanhos` = (k das janelas, menor e maior fim do arquivo) (D148).
    """
    k, menor, maior = tamanhos
    embaralhamentos = textos.quantidade(simulacoes, "embaralhamento", "embaralhamentos")
    return DetalhesAviso(
        medida=(
            f"Janelas de {k} linhas seguidas e o fim do arquivo (de {menor} a "
            f"{formatar_inteiro(maior)} linhas): diferença de média (dᵤ) e de desvio (dₛ) "
            "para o restante das linhas, em desvios padrão do restante"
        ),
        valor=f"dᵤ = {distancia(distancias[0])} · dₛ = {distancia(distancias[1])}",
        limiar="dᵤ e dₛ < 0,01 e menos de 1% dos embaralhamentos com uma janela tão parecida",
        teste=f"Simulação: {embaralhamentos} da coluna (semente fixa)",
        formula="dᵤ = |x̄_bloco − x̄_resto| / s_resto · dₛ = |s_bloco − s_resto| / s_resto",
        p_valor=p,
        p_em_palavras=textos.p_em_palavras(p),
    )


# R2 — Correlação por blocos -----------------------------------------------------------------

CASAS_CORRELACAO = 2
BLOCO_SEM_VARIACAO = "os valores não variam em algum dos 5 blocos"


def correlacao(r: float) -> str:
    """r com 2 casas e o sinal de menos: −0,41."""
    return formatar_fixo(r, CASAS_CORRELACAO)


def poucos_pares(minimo: int, n: int) -> str:
    return f"precisa de {formatar_inteiro(minimo)} pares ou mais; o par tem {formatar_inteiro(n)}"


def r02_textos(
    par: tuple[str, str],
    correlacoes: tuple[float, float],
    sem_bloco: tuple[int, int, float] | None,
    linha_do_tempo: str | None,
) -> TextosAviso:
    """ "A correlação geral entre {x} e {y} é {r}, mas a média dos blocos é só {rb}." (spec 16).

    `correlacoes` = (r geral, média dos blocos). Quando o que dispara é um bloco só, o resumo
    diz quanto r fica sem ele; numa série no tempo, o "pode ser normal" fala das épocas (D137).
    """
    x, y = par
    r, media_blocos = correlacoes
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
        pode_ser_normal=(
            "…os blocos têm faixas de valores muito diferentes."
            if linha_do_tempo is None
            else f"…a relação muda com o tempo (as linhas seguem a coluna {linha_do_tempo}; "
            "ex.: estações do ano)."
        ),
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


# R6 — Comparação temporal -------------------------------------------------------------------

SEM_DATA = "o arquivo não tem uma coluna de data"
SO_DATAS = "o arquivo só tem datas e identificadores"
POR_QUE_R6 = "Dados novos que copiam os antigos ou variam pouco demais podem ter sido inseridos."
PODE_SER_NORMAL_R6 = "…houve mudança real no processo."
PODE_SER_NORMAL_R6_VARIACAO = (
    "…houve mudança real no processo ou a época do ano muda os dados "
    "(ex.: chuva, vendas de fim de ano)."
)


def data_do_meio(data: str, coluna: str) -> str:
    """ "14/12/2026 (data do meio de dia)": a data e a coluna de data usada (D130)."""
    return f"{data} (data do meio de {coluna})"


def poucas_linhas_por_periodo(minimo: int) -> str:
    return f"precisa de {formatar_inteiro(minimo)} linhas ou mais antes e depois da data do meio"


def r06_textos_variacao(
    coluna: str, data: str, desvios: tuple[float, float], zeros: int
) -> TextosAviso:
    """ "Os dados de {col} depois de {data} variam bem menos em relação aos anteriores…"."""
    antes, depois = (textos.numero(desvio) for desvio in desvios)
    medida = "desvio padrão fora os zeros" if zeros else "desvio padrão"
    return TextosAviso(
        titulo=f"Variação menor depois de {data} em {coluna}",
        resumo=(
            f"Os dados de {coluna} depois de {data} variam bem menos em relação aos anteriores "
            f"({medida} {depois}; antes, {antes})."
        ),
        por_que=POR_QUE_R6,
        pode_ser_normal=PODE_SER_NORMAL_R6_VARIACAO,
        o_que_fazer=f"Confira como os dados depois de {data} foram coletados.",
    )


def r06_detalhes_variacao(
    referencia: str, desvios: tuple[float, float], linhas: tuple[int, int], p: float, zeros: int
) -> DetalhesAviso:
    antes, depois = desvios
    sem_zeros = f", fora os {formatar_inteiro(zeros)} zeros" if zeros else ""
    return DetalhesAviso(
        medida=f"Desvio padrão antes e depois de {referencia}{sem_zeros}",
        valor=(
            f"antes: {textos.numero(antes)} ({textos.quantidade(linhas[0], 'linha', 'linhas')}) · "
            f"depois: {textos.numero(depois)} "
            f"({textos.quantidade(linhas[1], 'linha', 'linhas')}) · "
            f"razão {textos.numero(depois / antes)}"
        ),
        limiar="DP depois < 0,5 × DP antes, improvável ao acaso (p < 0,01)",
        teste="F de Snedecor (unilateral)",
        formula="F = s²_depois / s²_antes",
        p_valor=p,
        p_em_palavras=textos.p_em_palavras(p),
    )


def r06_texto_exemplo_copias(novas: Sequence[int], antigas: Sequence[int]) -> str:
    """ "Linhas 56, 62 e 71: iguais às linhas 4, 11 e 19, fora a data"."""
    referencia = textos.faixa_de_linhas(antigas)
    artigo = "à" if len(antigas) == 1 else "às"
    iguais = pluralizar(len(novas), "igual", "iguais")
    return (
        f"{textos.faixa_de_linhas(novas)}: {iguais} {artigo} "
        f"{referencia[0].lower()}{referencia[1:]}, fora a data"
    )


def r06_textos_copias(data: str, copias: int, novas: int) -> TextosAviso:
    """ "Os dados depois de {data} copiam os anteriores: {k} das {m} linhas novas ({pct})…"."""
    return TextosAviso(
        titulo="Linhas novas repetem linhas antigas",
        resumo=(
            f"Os dados depois de {data} copiam os anteriores: {formatar_inteiro(copias)} das "
            f"{formatar_inteiro(novas)} linhas novas ({textos.percentual(copias / novas)}) "
            "são iguais a linhas de antes, fora a data."
        ),
        por_que=POR_QUE_R6,
        pode_ser_normal=PODE_SER_NORMAL_R6,
        o_que_fazer="Confira se essas linhas são registros novos de verdade.",
    )


def r06_detalhes_copias(
    referencia: str, contagem: tuple[int, int], acaso: float, p: float
) -> DetalhesAviso:
    """contagem = (linhas novas iguais a antigas, linhas novas)."""
    copias, novas = contagem
    return DetalhesAviso(
        medida=(
            f"Linhas depois de {referencia} iguais a alguma linha de antes "
            "(fora as datas e os identificadores)"
        ),
        valor=(
            f"{textos.percentual(copias / novas)} ({formatar_inteiro(copias)} de "
            f"{formatar_inteiro(novas)}) · entre as linhas de antes, "
            f"{textos.percentual(acaso)} se repetem"
        ),
        limiar="≥ 10% das linhas novas e acima do que as antigas repetem entre si (p < 0,01)",
        teste="Binomial unilateral",
        formula="P(X ≥ k), X ~ Binomial(linhas novas; fração das antigas que se repetem)",
        p_valor=p,
        p_em_palavras=textos.p_em_palavras(p),
    )


# R10 — Normal perfeita demais ---------------------------------------------------------------

CASAS_FORMA = 3


def medida_de_forma(valor: float) -> str:
    """G₁ e G₂ com 3 casas: 0,009 · −0,045 (somar 0,0 tira o "−0,000")."""
    return formatar_fixo(round(valor, CASAS_FORMA) + 0.0, CASAS_FORMA)


def r10_textos(coluna: str, assimetria: float, curtose: float) -> TextosAviso:
    """ "{col} parece uma curva Normal perfeita demais (assimetria {g1}, curtose {g2})."."""
    return TextosAviso(
        titulo=f"Curva Normal perfeita demais em {coluna}",
        resumo=(
            f"{coluna} parece uma curva Normal perfeita demais (assimetria "
            f"{medida_de_forma(assimetria)}, curtose {medida_de_forma(curtose)})."
        ),
        por_que=(
            "Dados reais quase nunca são tão perfeitos; "
            "isso é típico de números gerados por computador."
        ),
        pode_ser_normal="…a amostra é grande e o fenômeno é realmente Normal.",
        o_que_fazer="Confira se essa coluna foi medida ou gerada por um programa.",
    )


def r10_detalhes(assimetria: float, curtose: float, teste: str, p: float) -> DetalhesAviso:
    """Com p alto, a chance que importa é a de uma Normal de verdade ajustar tão bem: 1 − p."""
    return DetalhesAviso(
        medida="Assimetria (G₁), curtose (G₂) e aderência à Normal",
        valor=(
            f"G₁ = {medida_de_forma(assimetria)} · G₂ = {medida_de_forma(curtose)} · "
            f"p = {formatar_numero(p, 3)}"
        ),
        limiar="|G₁| < 0,05, |G₂| < 0,1 e p > 0,99",
        teste=teste,
        formula="G₁ e G₂ amostrais, como na aba Forma; p do teste de aderência à Normal",
        p_valor=p,
        p_em_palavras=(
            "chance de dados Normais de verdade ficarem tão perto da curva: "
            f"{p_valor_em_palavras(1 - p)}"
        ),
    )


# R11 — Sequência ----------------------------------------------------------------------------

R11_PADROES = {
    "parecidos": "cada valor é muito parecido com o anterior",
    "alterna": "valores alternam acima e abaixo do meio com regularidade",
    "sequencias": "valores acima e abaixo do meio aparecem em sequências longas",
}
R11_TESTES = {
    "progressao": "Poisson: progressões × acaso",
    "alterna": "Runs de Wald-Wolfowitz",
    "sequencias": "Runs de Wald-Wolfowitz",
}


def r11_padrao(padrao: str, linhas: tuple[int, int]) -> str:
    """O padrão em palavras; a progressão diz onde está."""
    if padrao == "progressao":
        return f"progressão aritmética nas linhas {linhas[0]}–{linhas[1]}"
    return R11_PADROES[padrao]


def r11_textos(coluna: str, padrao: str, linha_do_tempo: str | None) -> TextosAviso:
    """ "A ordem dos valores de {col} segue um padrão ({padrao})." (spec 16).

    Numa série no tempo, o "pode ser normal" diz a coluna de data que as linhas seguem (D137).
    """
    return TextosAviso(
        titulo=f"Ordem dos valores segue um padrão em {coluna}",
        resumo=f"A ordem dos valores de {coluna} segue um padrão ({padrao}).",
        por_que="Em dados reais, a sequência costuma parecer aleatória.",
        pode_ser_normal=(
            "…os dados estão ordenados por tempo ou por outra coluna."
            if linha_do_tempo is None
            else f"…é uma série no tempo (as linhas seguem a coluna {linha_do_tempo}): "
            "valores vizinhos costumam ser parecidos."
        ),
        o_que_fazer=(
            "Confira se o arquivo foi ordenado ou se esses valores foram digitados em sequência."
        ),
    )


def r11_detalhes(
    medidas: tuple[int, float, float, int], padrao: str, p: float | None
) -> DetalhesAviso:
    """medidas = (sequências do runs, z, ρ₁, progressões)."""
    runs, z, autocorrelacao, progressoes = medidas
    return DetalhesAviso(
        medida=(
            "Ordem dos valores: sequências acima e abaixo da mediana (runs), "
            "progressões aritméticas e autocorrelação"
        ),
        valor=(
            f"{textos.quantidade(runs, 'sequência', 'sequências')} (z = {textos.numero(z)}) · "
            f"ρ₁ = {textos.numero(autocorrelacao)} · "
            f"{textos.quantidade(progressoes, 'progressão', 'progressões')}"
        ),
        limiar=(
            "Runs com p < 0,01, progressão de 6 valores ou mais improvável ao acaso "
            "(p < 0,01) ou |ρ₁| > 0,8"
        ),
        teste=R11_TESTES.get(padrao),
        formula="Z = (R − μ_R) / σ_R · ρ₁ = Σ(xₜ − x̄)(xₜ₊₁ − x̄) / Σ(xₜ − x̄)²",
        p_valor=p,
        p_em_palavras=None if p is None else textos.p_em_palavras(p),
    )
