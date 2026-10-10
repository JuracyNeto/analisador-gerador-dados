"""Frases do relatório (spec 13 e 16)."""

from app.compartilhado.numeros import formatar_inteiro
from app.compartilhado.textos import juntar_lista, pluralizar
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
    "identificador": "Identificador (ignorada)",
    "data": "Data ou hora (ignorada)",
}
SEM_LIMPEZA = "Nenhuma ação de limpeza foi aplicada."
TITULOS_SECOES = {
    "leitura": "Leitura do arquivo",
    "tipos": "Tipos de variável",
    "limpeza": "Limpeza",
    "bivariada": "Bivariada",
}


def _quantidade(n: int, singular: str, plural: str) -> str:
    return f"{formatar_inteiro(n)} {pluralizar(n, singular, plural)}"


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
    linhas = _quantidade(dados.n_linhas, "linha", "linhas")
    colunas = _quantidade(dados.n_colunas, "coluna", "colunas")
    return f"{descricao} Foram lidas {linhas} e {colunas}."


def subtitulo(nome_arquivo: str, n_linhas: int, n_linhas_original: int, n_colunas: int) -> str:
    """Ex.: "pesquisa_saude.txt · 227 linhas após limpeza × 8 colunas"."""
    linhas = _quantidade(n_linhas, "linha", "linhas")
    if n_linhas != n_linhas_original:
        linhas += " após limpeza"
    return f"{nome_arquivo} · {linhas} × {_quantidade(n_colunas, 'coluna', 'colunas')}"


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


def selo_correlacao(forca: str, sentido: str) -> str:
    """Como o selo da tela Bivariada: "Positiva forte", "Fraca"."""
    if forca == "fraca" or sentido == "nula":
        return "Fraca"
    return f"{sentido.capitalize()} {forca}"
