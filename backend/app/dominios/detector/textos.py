"""Textos do detector (spec 16, ADR 0005): tom neutro, número com contexto, p em palavras.

Nenhuma regra monta texto fora deste módulo (D118).
"""

from collections.abc import Sequence
from itertools import pairwise

from app.compartilhado.numeros import (
    formatar_com_sinal,
    formatar_fixo,
    formatar_inteiro,
    formatar_p_valor,
    formatar_percentual,
)
from app.compartilhado.textos import juntar_lista, p_valor_em_palavras, pluralizar
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso

MAX_ITENS_TEXTO = 8
MIN_LINHAS_FAIXA = 3
"""Com 3 linhas seguidas ou mais, o exemplo diz "Linhas 120 a 138"."""
CASAS_SIGNIFICATIVAS_VALOR = 7
RETICENCIAS = "…"


# Formatação ---------------------------------------------------------------------------------


def valor(numero: float) -> str:
    """Valor de uma célula como o usuário escreveria: 70 · 1,62 · −3,5."""
    return formatar_com_sinal(numero, CASAS_SIGNIFICATIVAS_VALOR)


def numero(medida: float) -> str:
    """Medida calculada com até 4 algarismos significativos: 80,5 · 0,0881."""
    return formatar_com_sinal(medida)


def percentual(fracao: float) -> str:
    """Fração (0–1) como percentual sem casas: 0,46 → 46%."""
    return formatar_percentual(fracao * 100, 0)


def razao(vezes: float) -> str:
    """Quantas vezes o esperado: 2,3×."""
    return f"{formatar_fixo(vezes, 1)}×"


def quantidade(n: int, singular: str, plural: str) -> str:
    return f"{formatar_inteiro(n)} {pluralizar(n, singular, plural)}"


def p_em_palavras(p: float) -> str:
    return f"chance de acontecer por acaso: {p_valor_em_palavras(p)}"


def p_formatado(p: float) -> str:
    return formatar_p_valor(p)


# Exemplo e regras não aplicadas -------------------------------------------------------------


def _seguidas(linhas: Sequence[int]) -> bool:
    return all(b == a + 1 for a, b in pairwise(linhas))


def faixa_de_linhas(linhas: Sequence[int]) -> str:
    """ "Linha 12" · "Linhas 120 a 138" · "Linhas 3, 9 e 14" · "Linhas 1, 3, …, 15…"."""
    if len(linhas) == 1:
        return f"Linha {linhas[0]}"
    if len(linhas) >= MIN_LINHAS_FAIXA and _seguidas(linhas):
        return f"Linhas {linhas[0]} a {linhas[-1]}"
    if len(linhas) > MAX_ITENS_TEXTO:
        primeiras = ", ".join(str(linha) for linha in linhas[:MAX_ITENS_TEXTO])
        return f"Linhas {primeiras}{RETICENCIAS}"
    return f"Linhas {juntar_lista([str(linha) for linha in linhas])}"


def lista_de_valores(valores: Sequence[str]) -> str:
    """Até 8 valores separados por vírgula, com "…" se houver mais."""
    texto = ", ".join(valores[:MAX_ITENS_TEXTO])
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


SEM_NUMERICAS = "o arquivo não tem colunas numéricas"
SEM_CONTINUAS = "o arquivo não tem colunas contínuas"
VALORES_IGUAIS = "todos os valores são iguais"
DIGITO_CONSTANTE = "o último dígito é sempre o mesmo"
POUCA_VARIACAO = "os valores variam pouco para o último dígito ser aleatório"
METADE_CENTRAL_IGUAL = "a metade central dos valores é toda igual"


# R7 — Valores distantes ---------------------------------------------------------------------


def r07_textos(coluna: str, k: int, exemplo: float, limite: float) -> TextosAviso:
    """ "{k} valores de {col} estão muito longe dos demais (ex.: {v})" (spec 16)."""
    longe = f"{pluralizar(k, 'está', 'estão')} muito longe dos demais"
    return TextosAviso(
        titulo=f"{quantidade(k, 'valor distante', 'valores distantes')} dos demais em {coluna}",
        resumo=(
            f"{quantidade(k, 'valor', 'valores')} de {coluna} {longe} (ex.: {valor(exemplo)}); "
            f"o limite usual seria {numero(limite)}."
        ),
        por_que="Valores extremos podem ser erros de digitação ou casos especiais.",
        pode_ser_normal="…são casos raros, mas reais.",
        o_que_fazer=(
            "Confira esses valores na fonte; se forem erros de digitação, corrija na etapa Limpeza."
        ),
    )


def r07_detalhes(moderados: int, extremos: int, cercas: tuple[float, ...]) -> DetalhesAviso:
    """Cercas: (Q1 − 1,5·IQR, Q3 + 1,5·IQR, Q1 − 3·IQR, Q3 + 3·IQR)."""
    baixo, alto, baixo_extremo, alto_extremo = (numero(c) for c in cercas)
    return DetalhesAviso(
        medida="Valores fora das cercas de Tukey ou com |z| > 3",
        valor=(
            f"{quantidade(moderados, 'moderado', 'moderados')} e "
            f"{quantidade(extremos, 'extremo', 'extremos')}"
        ),
        limiar=(
            f"Moderado: fora de {baixo} a {alto} (1,5·IQR) · "
            f"extremo: fora de {baixo_extremo} a {alto_extremo} (3·IQR) ou |z| > 3"
        ),
        formula="IQR = Q3 − Q1 · z = (x − x̄) / s",
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
        pode_ser_normal="…o instrumento arredonda.",
        o_que_fazer="Confira como esses valores foram medidos ou digitados.",
    )


def r09_detalhes(digito: int, proporcao: float, p: float) -> DetalhesAviso:
    return DetalhesAviso(
        medida="Frequência do último dígito (0 a 9)",
        valor=f"o {digito} em {percentual(proporcao)} (esperado 10%)",
        limiar="p < 0,01",
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


def r08_detalhes(mad: float, p: float) -> DetalhesAviso:
    return DetalhesAviso(
        medida="Frequência do primeiro dígito comparada à Lei de Benford",
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
            f"(linhas {linhas[0]}–{linhas[1]})."
        ),
        por_que="Uma mudança de formato no meio dos dados pode indicar outra origem.",
        pode_ser_normal="…parte dos dados veio de outro instrumento.",
        o_que_fazer="Confira de onde vieram essas linhas.",
    )


def r03_detalhes(proporcao: float, k: int, passo: int) -> DetalhesAviso:
    return DetalhesAviso(
        medida="Valores com casas decimais e posição dos inteiros",
        valor=(
            f"{percentual(proporcao)} com decimais · "
            f"{formatar_inteiro(k)} inteiros {_onde_inteiros(passo)}"
        ),
        limiar=(
            "≥ 80% com decimais e ≥ 5 inteiros seguidos ou a passo constante (4 repetições ou mais)"
        ),
    )


# R5 — Duplicatas ----------------------------------------------------------------------------

SO_IDENTIFICADORES = "o arquivo só tem identificadores"
POUCAS_COLUNAS = "precisa de 2 colunas ou mais (fora os identificadores)"
SEM_VALOR = "—"
SEPARADOR_CELULAS = " · "


def poucas_linhas(minimo: int, n: int) -> str:
    return (
        f"precisa de {formatar_inteiro(minimo)} linhas ou mais; o arquivo tem {formatar_inteiro(n)}"
    )


def linha_como_texto(celulas: Sequence[str | None]) -> str:
    """Uma linha do arquivo: "F · 34 · 1,62 · 58,2"."""
    return SEPARADOR_CELULAS.join(SEM_VALOR if celula is None else celula for celula in celulas)


def r05_texto_exemplo(linhas: Sequence[int], primeira: str) -> str:
    """ "Linhas 44 a 47: F · 34 · …" (as linhas são iguais: mostra uma só)."""
    return f"{faixa_de_linhas(linhas)}: {primeira}"


def r05_texto_exemplo_quase(linhas: Sequence[int], primeira: str) -> str:
    return f"{faixa_de_linhas(linhas)} (quase iguais): {primeira}"


def _iguais(k: int, grupos_quase: int) -> str:
    """ "iguais" ou, se algum grupo só é quase igual, "iguais ou quase iguais"."""
    igual = pluralizar(k, "igual", "iguais")
    return f"{igual} ou quase {igual}" if grupos_quase else igual


def r05_textos(copias: int, grupos_quase: int, seguidas: tuple[int, int] | None) -> TextosAviso:
    """ "Encontramos {k} linhas iguais (ou quase), {em_sequencia}." (spec 16)."""
    linhas = quantidade(copias, "linha", "linhas")
    outras = pluralizar(copias, "outra", "outras")
    sequencia = (
        f"; as linhas {seguidas[0]} a {seguidas[1]} são {_iguais(2, grupos_quase)} e seguidas"
        if seguidas
        else ""
    )
    return TextosAviso(
        titulo="Linhas iguais em sequência" if seguidas else "Linhas repetidas no arquivo",
        resumo=(
            f"Encontramos {linhas} {_iguais(copias, grupos_quase)} a {outras} do arquivo"
            f"{sequencia}."
        ),
        por_que=(
            "Cópias seguidas costumam surgir de 'copiar e colar'."
            if seguidas
            else "Linhas repetidas podem ter sido copiadas de outras partes do arquivo."
        ),
        pode_ser_normal="…são registros legítimos repetidos (ex.: a mesma compra).",
        o_que_fazer=(
            "Confira se essas linhas são registros diferentes; "
            "se forem cópias, remova os duplicados na etapa Limpeza."
        ),
    )


def r05_formula_quase(numericas: int) -> str:
    return (
        "Quase iguais: distância entre as linhas padronizadas < 0,01·√p "
        f"(p = {numericas} colunas numéricas) e as demais colunas iguais"
    )


R05_FORMULA_IDENTICAS = "Só linhas idênticas"


def r05_detalhes(copias: int, grupos: int, formula: str) -> DetalhesAviso:
    return DetalhesAviso(
        medida="Linhas iguais ou quase iguais em todas as colunas (fora os identificadores)",
        valor=f"{quantidade(copias, 'cópia', 'cópias')} em {quantidade(grupos, 'grupo', 'grupos')}",
        limiar="Qualquer cópia (atenção); 3 linhas iguais seguidas ou mais (suspeita alta)",
        formula=formula,
    )


def r05_ressalva(n: int, limite: int) -> tuple[str, str]:
    """(motivo, frase) das quase duplicatas não verificadas em arquivos grandes (D120)."""
    motivo = f"o arquivo tem {formatar_inteiro(n)} linhas e o limite é {formatar_inteiro(limite)}"
    return motivo, f"Quase duplicatas não verificadas: {motivo}."
