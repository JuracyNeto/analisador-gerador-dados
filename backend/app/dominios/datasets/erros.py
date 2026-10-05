"""Erros do domínio datasets com textos da spec 01/02/17 (formato da spec 16)."""

from app.core.erros import ArquivoGrande, EntradaInvalida, NaoEncontrado


def arquivo_vazio() -> EntradaInvalida:
    return EntradaInvalida(
        "ARQUIVO_VAZIO", "O arquivo está vazio.", "Confira se escolheu o arquivo certo."
    )


def formato_nao_suportado(nome_arquivo: str) -> EntradaInvalida:
    return EntradaInvalida(
        "FORMATO_NAO_SUPORTADO",
        f"Não conseguimos ler este arquivo: {nome_arquivo}. "
        "Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.",
        "Abra o arquivo na planilha de origem e salve como CSV ou XLSX, depois envie de novo.",
    )


def arquivo_grande(limite_mb: int) -> ArquivoGrande:
    return ArquivoGrande(
        "ARQUIVO_GRANDE",
        f"O arquivo passa de {limite_mb} MB.",
        "Envie só as colunas e linhas que vai analisar.",
    )


def json_invalido() -> EntradaInvalida:
    return EntradaInvalida(
        "JSON_INVALIDO",
        "Não conseguimos ler este JSON. Verifique se é uma lista de registros.",
        'Use o formato [{"coluna": valor}, …] ou {"coluna": [valores]}.',
    )


def arquivo_ilegivel() -> EntradaInvalida:
    return EntradaInvalida(
        "ARQUIVO_ILEGIVEL",
        "Não conseguimos ler este arquivo como tabela.",
        "Escolha outro separador ou confira se todas as linhas têm o mesmo número de colunas.",
    )


def dataset_nao_encontrado() -> NaoEncontrado:
    return NaoEncontrado(
        "DATASET_NAO_ENCONTRADO", "Sua sessão expirou.", "Envie o arquivo novamente."
    )


def coluna_nao_encontrada(coluna: str) -> NaoEncontrado:
    return NaoEncontrado(
        "COLUNA_NAO_ENCONTRADA",
        f"Não encontramos a coluna {coluna}.",
        "Ela pode ter sido renomeada — recarregue a página.",
    )


def tipo_incompativel(mensagem: str) -> EntradaInvalida:
    return EntradaInvalida("TIPO_INCOMPATIVEL", mensagem, "Escolha outro tipo para esta coluna.")


def categorias_incompletas(faltando: list[str]) -> EntradaInvalida:
    return EntradaInvalida(
        "CATEGORIAS_INCOMPLETAS",
        f"Faltam categorias na ordem: {', '.join(faltando)}.",
        "Inclua todas as categorias da coluna na ordem.",
    )
