"""Textos do detector (spec 16, ADR 0005): tom neutro, número com contexto, p em palavras.

Nenhuma regra monta texto fora deste módulo, de `textos_blocos.py` e de `textos_duplicatas.py`
(D118).
"""

from collections.abc import Sequence
from itertools import pairwise

from app.compartilhado.numeros import (
    formatar_fixo,
    formatar_inteiro,
    formatar_numero,
    formatar_percentual,
)
from app.compartilhado.textos import (
    juntar_lista,
    p_valor_em_palavras,
    pluralizar,
    quantidade,
)
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso
from app.dominios.detector.tabela import ColunaDetector

MAX_ITENS_TEXTO = 8
MIN_LINHAS_FAIXA = 3
"""Com 3 linhas seguidas ou mais, o exemplo diz "Linhas 120 a 138"."""
CASAS_SIGNIFICATIVAS_VALOR = 7
RETICENCIAS = "…"


# Formatação ---------------------------------------------------------------------------------


def valor(numero: float) -> str:
    """Valor de uma célula como o usuário escreveria: 70 · 1,62 · −3,5."""
    return formatar_numero(numero, CASAS_SIGNIFICATIVAS_VALOR)


def numero(medida: float) -> str:
    """Medida calculada com até 4 algarismos significativos: 80,5 · 0,0881."""
    return formatar_numero(medida)


def percentual(fracao: float) -> str:
    """Fração (0–1) como percentual sem casas: 0,46 → 46%."""
    return formatar_percentual(fracao * 100, 0)


def razao(vezes: float) -> str:
    """Quantas vezes o esperado: 2,3×."""
    return f"{formatar_fixo(vezes, 1)}×"


def p_em_palavras(p: float) -> str:
    return f"chance de acontecer por acaso: {p_valor_em_palavras(p)}"


# Exemplo e regras não aplicadas -------------------------------------------------------------


def _seguidas(linhas: Sequence[int]) -> bool:
    return all(b == a + 1 for a, b in pairwise(linhas))


def linha(numero_da_linha: int) -> str:
    """Número de linha com ponto de milhar, como na etapa Limpeza: 1.234."""
    return formatar_inteiro(numero_da_linha)


def intervalo_de_linhas(linhas: tuple[int, int]) -> str:
    """ "1.201–1.230"."""
    return f"{linha(linhas[0])}–{linha(linhas[1])}"


def faixa_de_linhas(linhas: Sequence[int]) -> str:
    """ "Linha 12" · "Linhas 1.200 a 1.238" · "Linhas 3, 9 e 14" · "Linhas 1, 3, …, 15…"."""
    escritas = [linha(numero_da_linha) for numero_da_linha in linhas]
    if len(linhas) == 1:
        return f"Linha {escritas[0]}"
    if len(linhas) >= MIN_LINHAS_FAIXA and _seguidas(linhas):
        return f"Linhas {escritas[0]} a {escritas[-1]}"
    if len(linhas) > MAX_ITENS_TEXTO:
        return f"Linhas {', '.join(escritas[:MAX_ITENS_TEXTO])}{RETICENCIAS}"
    return f"Linhas {juntar_lista(escritas)}"


def lista_de_valores(valores: Sequence[str]) -> str:
    """Até 8 valores, com "…" se houver mais; com decimais, "; " separa sem ambiguidade."""
    mostrados = valores[:MAX_ITENS_TEXTO]
    separador = "; " if any("," in valor for valor in mostrados) else ", "
    texto = separador.join(mostrados)
    return texto + RETICENCIAS if len(valores) > MAX_ITENS_TEXTO else texto


def texto_exemplo(linhas: Sequence[int], valores: Sequence[str]) -> str:
    """ "Linhas 120 a 138: 70, 75, 80, 75, 70…" (spec 16, parte 5)."""
    return f"{faixa_de_linhas(linhas)}: {lista_de_valores(valores)}"


def frase_nao_aplicada(nome_regra: str, coluna: str | None, motivo: str) -> str:
    """ "{regra} não verificada em {col}: {motivo}." (spec 16)."""
    onde = f" em {coluna}" if coluna is not None else ""
    return f"{nome_regra} não verificada{onde}: {motivo}."


def poucos_valores(minimo: int, n: int) -> str:
    return (
        f"precisa de {formatar_inteiro(minimo)} valores ou mais; a coluna tem {formatar_inteiro(n)}"
    )


def poucos_valores_diferentes(k: int) -> str:
    return f"a coluna tem só {k} valores diferentes"


def fora_os_zeros(motivo: str) -> str:
    """R4 e R9 não olham os zeros (D134): "…; a coluna tem 40, fora os zeros"."""
    return f"{motivo}, fora os zeros"


SEPARADOR_CELULAS = " · "


def poucas_linhas(minimo: int, n: int) -> str:
    return (
        f"precisa de {formatar_inteiro(minimo)} linhas ou mais; o arquivo tem {formatar_inteiro(n)}"
    )


def linha_como_texto(colunas: Sequence[ColunaDetector], posicao: int) -> str:
    """A linha na `posicao` das colunas, com o nome delas (R5, R6; D171).

    "sexo F · idade 34 · peso_kg 58,2"; as vazias no fim: "peso_kg 70,1 (sexo e idade vazias)".
    """
    celulas = [(coluna.nome, coluna.textos[posicao]) for coluna in colunas]
    preenchidas = SEPARADOR_CELULAS.join(f"{nome} {texto}" for nome, texto in celulas if texto)
    vazias = [nome for nome, texto in celulas if not texto]
    if not vazias:
        return preenchidas
    return f"{preenchidas} ({juntar_lista(vazias)} {pluralizar(len(vazias), 'vazia', 'vazias')})"


SEM_NUMERICAS = "o arquivo não tem colunas numéricas"
SEM_CONTINUAS = "o arquivo não tem colunas contínuas"
SEM_PAR_NUMERICO = "o arquivo não tem duas colunas numéricas"
VALORES_IGUAIS = "todos os valores são iguais"
DIGITO_CONSTANTE = "o último dígito é sempre o mesmo"
POUCA_VARIACAO = "os valores variam pouco para o último dígito ser aleatório"
VALORES_PEQUENOS = "os valores são pequenos demais para o último dígito ser aleatório"
METADE_CENTRAL_IGUAL = "a metade central dos valores é toda igual"


# R7 — Valores distantes ---------------------------------------------------------------------


def r07_exemplo_fora(exemplo: float, limite: float) -> str:
    """Exemplo fora da cerca de 1,5·IQR, a mesma da etapa Limpeza: "(ex.: 712); o limite…"."""
    return f"(ex.: {valor(exemplo)}); o limite usual seria {numero(limite)}"


def r07_exemplo_fora_ajustado(exemplo: float, limite: float) -> str:
    """Exemplo fora da cerca alargada pela cauda longa (D136), que a etapa Limpeza não usa."""
    limite_ajustado = f"o limite, ajustado à assimetria da coluna, seria {numero(limite)}"
    return f"(ex.: {valor(exemplo)}); {limite_ajustado}"


def r07_exemplo_pelo_z(exemplo: float) -> str:
    """Exemplo dentro das cercas, marcado só por |z| > 3 (achado D-a do M4.3)."""
    return f"(ex.: {valor(exemplo)}, a mais de 3 desvios padrão da média)"


def r07_textos(coluna: str, k: int, exemplo: str) -> TextosAviso:
    """ "{k} valores de {col} estão muito longe dos demais (ex.: {v}); …" (spec 16).

    `exemplo` diz o critério que marcou o valor (`r07_exemplo_*`).
    """
    longe = f"{pluralizar(k, 'está', 'estão')} muito longe dos demais"
    return TextosAviso(
        titulo=f"{quantidade(k, 'valor distante', 'valores distantes')} dos demais em {coluna}",
        resumo=f"{quantidade(k, 'valor', 'valores')} de {coluna} {longe} {exemplo}.",
        por_que="Valores extremos podem ser erros de digitação ou casos especiais.",
        pode_ser_normal="…são casos raros, mas reais.",
        o_que_fazer=(
            "Confira esses valores na fonte; se forem erros de digitação, corrija no arquivo e "
            "envie de novo, ou remova-os na etapa Limpeza."
        ),
    )


def r07_detalhes(
    moderados: int, extremos: int, cercas: tuple[float, ...], mc: float, zeros: int
) -> DetalhesAviso:
    """Cercas de 1,5·IQR e de 3·IQR, alargadas pela assimetria (MC; D136), sem os zeros (D143)."""
    baixo, alto, baixo_extremo, alto_extremo = (numero(c) for c in cercas)
    sem_zeros = f", fora os {formatar_inteiro(zeros)} zeros" if zeros else ""
    return DetalhesAviso(
        medida=f"Valores fora das cercas de Tukey ajustadas à assimetria ou com |z| > 3{sem_zeros}",
        valor=(
            f"{quantidade(moderados, 'moderado', 'moderados')} e "
            f"{quantidade(extremos, 'extremo', 'extremos')}"
        ),
        limiar=(
            f"Moderado: fora de {baixo} a {alto} (1,5·IQR) ou |z| > 3 · "
            f"extremo: fora de {baixo_extremo} a {alto_extremo} (3·IQR)"
        ),
        formula=(
            f"IQR = Q3 − Q1 · z = (x − x̄) / s · MC = {numero(mc)} (medcouple); "
            "com MC > 0 a cerca de cima vai a Q3 + k·e^(3·MC)·IQR, nunca abaixo de Q3 + k·IQR; "
            "a etapa Limpeza usa as cercas sem o ajuste"
        ),
    )


# R4 — Valores redondos ----------------------------------------------------------------------

TERMINACOES = {5: "terminam em 0 ou 5", 10: "terminam em 0"}


def r04_textos(
    coluna: str, proporcao: float, esperado: float, multiplo: int, passo: float
) -> TextosAviso:
    """ "46% dos valores terminam em 0 ou 5; … cerca de 20% (2,3× mais)" (spec 16)."""
    return TextosAviso(
        titulo=f"Muitos valores redondos em {coluna}",
        resumo=(
            f"{percentual(proporcao)} dos valores {TERMINACOES[multiplo]}; em medições reais "
            f"o esperado seria cerca de {percentual(esperado)} "
            f"({razao(proporcao / esperado)} mais)."
        ),
        por_que=(
            "Quando números são inventados ou digitados de cabeça, as pessoas tendem a arredondar."
        ),
        pode_ser_normal=f"…o instrumento só mede de {valor(passo)} em {valor(passo)}.",
        o_que_fazer="Confira a origem dessas linhas.",
    )


def r04_detalhes(multiplo: int, k: int, n: int, esperado: float, p: float) -> DetalhesAviso:
    return DetalhesAviso(
        medida=f"Valores que {TERMINACOES[multiplo]} (último dígito na precisão da coluna)",
        valor=f"{percentual(k / n)} ({formatar_inteiro(k)} de {formatar_inteiro(n)})",
        limiar=f"p < 0,01 e pelo menos 1,5× o esperado ({percentual(esperado)})",
        teste="Binomial unilateral",
        formula=(
            f"P(X ≥ {formatar_inteiro(k)}), X ~ Binomial({formatar_inteiro(n)}; {numero(esperado)})"
        ),
        p_valor=p,
        p_em_palavras=p_em_palavras(p),
    )


# R9 — Último dígito -------------------------------------------------------------------------


def r09_textos(coluna: str, digito: int, proporcao: float) -> TextosAviso:
    """ "O último dígito de {col} não está bem distribuído: o {d} aparece {pct}%…" (spec 16)."""
    return TextosAviso(
        titulo=f"Último dígito repetido em {coluna}",
        resumo=(
            f"O último dígito de {coluna} não está bem distribuído: o {digito} aparece "
            f"{percentual(proporcao)} das vezes (esperado 10%)."
        ),
        por_que=(
            "Medições reais têm o último dígito quase aleatório; "
            "pessoas evitam ou repetem certos dígitos."
        ),
        pode_ser_normal="…são preços (ex.: 5,99) ou o instrumento arredonda.",
        o_que_fazer="Confira como esses valores foram medidos ou digitados.",
    )


def r09_detalhes(digito: int, proporcao: float, p: float) -> DetalhesAviso:
    return DetalhesAviso(
        medida="Frequência do último dígito (0 a 9)",
        valor=f"o {digito} em {percentual(proporcao)} (esperado 10%)",
        limiar="p < 0,01 e o dígito mais comum com pelo menos 1,5× o esperado (15%)",
        teste="Qui-quadrado de uniformidade (gl = 9)",
        formula="χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ, com Eᵢ = n / 10",
        p_valor=p,
        p_em_palavras=p_em_palavras(p),
    )


# R8 — Lei de Benford ------------------------------------------------------------------------

VALORES_NEGATIVOS = "tem valores negativos"
POUCAS_ORDENS = "precisa de valores que variem em várias ordens de grandeza"


def poucos_positivos(minimo: int, n: int) -> str:
    return (
        f"precisa de {formatar_inteiro(minimo)} valores maiores que zero; "
        f"a coluna tem {formatar_inteiro(n)}"
    )


def fora_os_pequenos(motivo: str, passos: int, passo: float) -> str:
    """R8 não conta os valores perto do passo do instrumento (D145)."""
    limite, vezes = numero(passos * passo), formatar_inteiro(passos)
    return (
        f"{motivo}, fora os valores abaixo de {limite} "
        f"({vezes} vezes o passo de {numero(passo)} do instrumento)"
    )


def r08_textos(coluna: str, digito: int, proporcao: float, esperado: float) -> TextosAviso:
    """ "Os primeiros dígitos de {col} não seguem o padrão natural (Lei de Benford)" (spec 16)."""
    return TextosAviso(
        titulo=f"Primeiros dígitos fora do padrão em {coluna}",
        resumo=(
            f"Os primeiros dígitos de {coluna} não seguem o padrão natural (Lei de Benford): "
            f"o {digito} abre {percentual(proporcao)} dos valores; "
            f"o esperado seria cerca de {percentual(esperado)}."
        ),
        por_que=(
            "Em muitos dados reais, o dígito 1 aparece no início cerca de 30% das vezes; "
            "números inventados tendem a ser mais 'uniformes'."
        ),
        pode_ser_normal="…os dados têm faixa limitada (ex.: idades, notas).",
        o_que_fazer="Confira de onde vieram esses valores e se foram digitados à mão.",
    )


def r08_detalhes(mad: float, p: float, pequenos: int, limite: float) -> DetalhesAviso:
    medida = "Frequência do primeiro dígito comparada à Lei de Benford"
    if pequenos:
        medida += f", fora os {quantidade(pequenos, 'valor', 'valores')} abaixo de {numero(limite)}"
    return DetalhesAviso(
        medida=medida,
        valor=f"MAD = {numero(mad)}",
        limiar="p < 0,01 e MAD > 0,015 (Nigrini: não conformidade)",
        teste="Qui-quadrado (gl = 8)",
        formula="P(d) = log₁₀(1 + 1/d) · MAD = média de |observado − esperado|",
        p_valor=p,
        p_em_palavras=p_em_palavras(p),
    )


# R3 — Formato numérico ----------------------------------------------------------------------


def _onde_inteiros(passo: int) -> str:
    return "aparecem juntos" if passo == 1 else f"aparecem a cada {passo} linhas"


def r03_textos(
    coluna: str, proporcao: float, k: int, passo: int, linhas: tuple[int, int]
) -> TextosAviso:
    """ "Em {col}, {pct}% dos valores têm casas decimais, mas {k} inteiros…" (spec 16)."""
    return TextosAviso(
        titulo=f"Inteiros no meio de decimais em {coluna}",
        resumo=(
            f"Em {coluna}, {percentual(proporcao)} dos valores têm casas decimais, "
            f"mas {formatar_inteiro(k)} inteiros {_onde_inteiros(passo)} "
            f"(linhas {intervalo_de_linhas(linhas)})."
        ),
        por_que="Uma mudança de formato no meio dos dados pode indicar outra origem.",
        pode_ser_normal="…parte dos dados veio de outro instrumento.",
        o_que_fazer="Confira de onde vieram essas linhas.",
    )


def r03_detalhes(proporcao: float, k: int, passo: int, p: float) -> DetalhesAviso:
    return DetalhesAviso(
        medida="Valores com casas decimais e posição dos inteiros",
        valor=(
            f"{percentual(proporcao)} com decimais · "
            f"{formatar_inteiro(k)} inteiros {_onde_inteiros(passo)}"
        ),
        limiar=(
            "≥ 80% com decimais e ≥ 5 inteiros seguidos ou a passo constante "
            "(4 repetições ou mais), improváveis ao acaso (p < 0,01)"
        ),
        teste="Poisson: padrão × inteiros espalhados ao acaso",
        formula="Esperados = nº de inteiros · P(intervalo = passo)^repetições",
        p_valor=p,
        p_em_palavras=p_em_palavras(p),
    )


# Resumo -------------------------------------------------------------------------------------

NENHUM_ALERTA = "Nenhum alerta"
SEM_GARANTIA = (
    "Isso não garante que os dados sejam reais, mas não vimos sinais comuns de dados artificiais."
)


def frase_resumo(total: int, colunas: int) -> str:
    """ "Encontramos 5 alertas em 3 colunas" (tela 7)."""
    if total == 0:
        return NENHUM_ALERTA
    onde = f" em {quantidade(colunas, 'coluna', 'colunas')}" if colunas else ""
    return f"Encontramos {quantidade(total, 'alerta', 'alertas')}{onde}"


def detalhe_resumo(colunas: Sequence[str], verificadas: int, nao_aplicadas: int) -> str:
    """ "altura_m, peso_kg e idade · 9 regras verificadas, 2 não se aplicam a este arquivo"."""
    regras = quantidade(verificadas, "regra verificada", "regras verificadas")
    if nao_aplicadas:
        verbo = pluralizar(nao_aplicadas, "se aplica", "se aplicam")
        regras += f", {formatar_inteiro(nao_aplicadas)} não {verbo} a este arquivo"
    return " · ".join([juntar_lista(list(colunas)), regras] if colunas else [regras])


def vazio_resumo(regras: int, verificadas: int) -> str:
    """Texto da spec 16 quando nenhuma regra encontra suspeitas."""
    if verificadas == 0:
        return (
            "Nenhuma das regras se aplica a este arquivo; "
            "os motivos estão em Regras não verificadas."
        )
    if regras == 1:
        return f"A regra pedida não encontrou suspeitas. {SEM_GARANTIA}"
    return f"Nenhuma das {regras} regras encontrou suspeitas. {SEM_GARANTIA}"
