"""Frases do relatório (spec 13 e 16)."""

from app.compartilhado.numeros import formatar_inteiro
from app.compartilhado.textos import juntar_lista, quantidade
from app.dominios.relatorio.conteudo import DadosLeitura

FORMATOS = {
    "txt": "Arquivo de texto",
    "csv": "Arquivo CSV",
    "tsv": "Arquivo TSV",
    "xlsx": "Planilha do Excel",
    "json": "Arquivo JSON",
}
SEPARADORES = {
    ";": "ponto e vírgula",
    ",": "vírgula",
    "\t": "tabulação",
    "|": "barra vertical",
    r"\s{2,}": "espaços",
}
DECIMAIS = {",": "decimal com vírgula", ".": "decimal com ponto"}
TIPOS_LEGIVEIS = {
    "nominal": "Qualitativa nominal",
    "ordinal": "Qualitativa ordinal",
    "discreta": "Quantitativa discreta",
    "continua": "Quantitativa contínua",
    "binaria": "Binária",
    "identificador": "Identificador (fora das análises)",
    "data": "Data ou hora (fora das análises)",
}
SEM_LIMPEZA = "Não aplicamos nenhuma ação de limpeza."
TITULOS_SECOES = {
    "leitura": "Leitura do arquivo",
    "tipos": "Tipos de variável",
    "limpeza": "Limpeza",
    "bivariada": "Bivariada",
    "gerador": "Gerador de dados",
    "detector": "Detector de dados artificiais",
    "formulas": "Fórmulas usadas",
}
# Grupos do apêndice de fórmulas, na ordem do documento (D151).
GRUPOS_FORMULAS = {
    "analises": "Análise por coluna",
    "distribuicoes": "Forma e distribuição",
    "bivariada": "Bivariada",
    "gerador": "Gerador",
    "detector": "Detector",
}
EM_TODAS_AS_COLUNAS = "em todas as colunas"


def _texto_cabecalho(linha: int) -> str:
    if linha == 0:
        return "sem cabeçalho"
    return "cabeçalho na primeira linha" if linha == 1 else f"cabeçalho na linha {linha}"


def descrever_leitura(dados: DadosLeitura) -> str:
    """Ex.: "Arquivo de texto separado por ponto e vírgula, decimal com vírgula, …"."""
    partes = []
    if dados.separador:
        partes.append(f"separado por {SEPARADORES.get(dados.separador, dados.separador)}")
    if dados.decimal:
        partes.append(DECIMAIS.get(dados.decimal, f"decimal {dados.decimal}"))
    if dados.codificacao:
        partes.append(f"codificação {dados.codificacao.upper()}")
    if dados.linha_cabecalho is not None:
        partes.append(_texto_cabecalho(dados.linha_cabecalho))
    if partes and not partes[0].startswith(("separado", "sem ")):
        partes[0] = f"com {partes[0]}"
    inicio = FORMATOS.get(dados.formato, "Arquivo")
    descricao = f"{inicio} {juntar_lista(partes)}." if partes else f"{inicio}."
    linhas = quantidade(dados.n_linhas, "linha", "linhas")
    colunas = quantidade(dados.n_colunas, "coluna", "colunas")
    return f"{descricao} Lemos {linhas} e {colunas}."


def subtitulo(nome_arquivo: str, n_linhas: int, n_linhas_original: int, n_colunas: int) -> str:
    """Ex.: "pesquisa_saude.txt · 227 linhas após limpeza × 8 colunas"."""
    linhas = quantidade(n_linhas, "linha", "linhas")
    if n_linhas != n_linhas_original:
        linhas += " após limpeza"
    return f"{nome_arquivo} · {linhas} × {quantidade(n_colunas, 'coluna', 'colunas')}"


ROTULOS_FORMA = {
    "assimetria": "Assimetria (G₁)",
    "curtose": "Curtose (G₂)",
    "assimetria_pearson_1": "As₁ (Pearson)",
    "assimetria_pearson_2": "As₂ (Pearson)",
    "curtose_percentilica": "K (percentílica)",
}
SELOS_ASSIMETRIA = {
    "simetrica": "Aproximadamente simétrica",
    "moderada": "Moderada",
    "forte": "Forte",
}
SELOS_CURTOSE = {
    "mesocurtica": "Mesocúrtica",
    "leptocurtica": "Leptocúrtica",
    "platicurtica": "Platicúrtica",
}
SEM_PAR_FORTE = "Nenhum par de colunas numéricas tem correlação moderada ou forte (|r| ≥ 0,3)."


def selo_assimetria(classe: str, sentido: str | None) -> str:
    """Como o selo da aba Forma: "Forte à direita", "Aproximadamente simétrica"."""
    if sentido is None:
        return "Simétrica" if classe == "simetrica" else SELOS_ASSIMETRIA[classe]
    if classe == "simetrica":
        return SELOS_ASSIMETRIA[classe]
    return f"{SELOS_ASSIMETRIA[classe]} à {sentido}"


TIPOS_GERACAO = {
    "univariado": ("Univariado", "valor", "valores"),
    "bivariado": ("Bivariado", "par", "pares"),
}


def subtitulo_gerador(tipo: str, n: int, semente: int) -> str:
    """Ex.: "Univariado · 500 valores · semente 42"; no bivariado, "300 pares"."""
    nome, singular, plural = TIPOS_GERACAO[tipo]
    return f"{nome} · {quantidade(n, singular, plural)} · semente {semente}"


def cabecalho_comparacao(n: int) -> tuple[str, ...]:
    """As colunas da tabela Original × Gerado da tela 6."""
    return ("Medida", "Original", f"Gerado ({formatar_inteiro(n)})", "Diferença")


def selo_correlacao(forca: str, sentido: str) -> str:
    """Como o selo da tela Bivariada: "Correlação positiva forte", "Correlação fraca"."""
    if forca == "fraca" or sentido == "nula":
        return "Correlação fraca"
    return f"Correlação {sentido} {forca}"


# Spec 16: ícone + palavra (a cor vem do CSS; o selo não depende só dela).
SELOS_SEVERIDADE = {
    "alta": "⛔ Suspeita alta",
    "atencao": "⚠️ Atenção",
    "info": "ℹ️ Informativo",
}
ROTULOS_DETALHES = {
    "medida": "Medida",
    "valor": "Valor",
    "limiar": "Limiar",
    "teste": "Teste",
    "p_valor": "p-valor",
    "formula": "Fórmula",
}


def contadores_severidade(alta: int, atencao: int, info: int) -> str:
    """Ex.: "2 suspeitas altas · 2 de atenção · 1 informativo" (os contadores da tela 7)."""
    partes = (
        quantidade(alta, "suspeita alta", "suspeitas altas"),
        f"{formatar_inteiro(atencao)} de atenção",
        quantidade(info, "informativo", "informativos"),
    )
    return " · ".join(partes)


def titulo_aviso(regra: str, titulo: str) -> str:
    """Ex.: "R4 · Muitos valores redondos em peso_kg"."""
    return f"{regra} · {titulo}"


def nome_formula_regra(regra: str, nome_regra: str) -> str:
    """Ex.: "R4 · Valores redondos" (a fórmula da regra no apêndice)."""
    return f"{regra} · {nome_regra}"


def onde_formula(colunas: list[str]) -> str | None:
    """Ex.: "em peso_kg e idade"; sem colunas (R5), nada."""
    return f"em {juntar_lista(colunas)}" if colunas else None


def contagem_coluna(n: int, faltantes: int) -> str:
    """Nota da seção da coluna: "227 valores válidos · 3 faltantes" (sem faltantes, só válidos)."""
    validos = quantidade(n, "valor válido", "valores válidos")
    return f"{validos} · {quantidade(faltantes, 'faltante', 'faltantes')}" if faltantes else validos
