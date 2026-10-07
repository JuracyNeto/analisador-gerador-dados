"""Detecção automática de formato, codificação, separador, decimal e cabeçalho (spec 01)."""

import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import PurePath

from app.dominios.datasets import erros

FORMATOS = {".txt": "txt", ".csv": "csv", ".tsv": "tsv", ".xlsx": "xlsx", ".json": "json"}
CODIFICACOES = ("utf-8", "cp1252")
CODIFICACAO_FINAL = "latin-1"  # decodifica qualquer byte; é o último recurso
BOM_UTF8 = b"\xef\xbb\xbf"
LINHAS_AMOSTRA = 50
MIN_LINHAS_CABECALHO = 2
MAX_LINHAS_TITULO = 10  # o cabeçalho é procurado entre as 10 primeiras linhas não vazias
FRACAO_LINHAS_CONSTANTE = 0.9
FRACAO_DECIMAL_VIRGULA = 0.8
SEM_SEPARADOR = "\x1f"  # caractere que não aparece em texto: a linha inteira vira uma célula
SEPARADOR_ESPACOS = r"\s{2,}"
CANDIDATOS_SEPARADOR = (";", ",", "\t", "|", SEPARADOR_ESPACOS)
_NUMERO = re.compile(r"^-?[\d.,]*\d[\d.,]*$")
_NUMERO_VIRGULA = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+,\d+$")
_PALAVRA = re.compile(r"\w+")

type LinhaNumerada = tuple[int, list[str]]
"""Nº da linha no arquivo (1, 2, …; linhas vazias contam) e as células já quebradas."""


@dataclass(frozen=True, slots=True)
class Deteccao[T]:
    """Valor detectado (ou escolhido) e o motivo mostrado na tela 1a (D53)."""

    valor: T
    motivo: str


def detectar_formato(nome_arquivo: str) -> Deteccao[str]:
    """Formato pela extensão do arquivo."""
    formato = FORMATOS.get(PurePath(nome_arquivo).suffix.lower())
    if formato is None:
        raise erros.formato_nao_suportado()
    return Deteccao(formato, "Pela extensão do arquivo.")


def _motivo_codificacao(texto: str) -> str:
    acentuada = next((p for p in _PALAVRA.findall(texto) if not p.isascii()), None)
    if acentuada is None:
        return "O texto não tem acentos."
    return f"Acentos lidos sem erro ({acentuada})."


def decodificar(conteudo: bytes, codificacao: str | None) -> tuple[str, Deteccao[str]]:
    """Texto e codificação; tenta utf-8-sig → utf-8 → cp1252 → latin-1."""
    if codificacao:
        texto = conteudo.decode(codificacao, errors="replace")
        return texto, Deteccao(codificacao, "Escolhida por você.")
    if conteudo.startswith(BOM_UTF8):
        texto = conteudo.decode("utf-8-sig", errors="replace")
        return texto, Deteccao("utf-8-sig", "O arquivo começa com a marca do UTF-8.")
    for candidata in CODIFICACOES:
        try:
            texto = conteudo.decode(candidata)
        except UnicodeDecodeError:
            continue
        return texto, Deteccao(candidata, _motivo_codificacao(texto))
    texto = conteudo.decode(CODIFICACAO_FINAL)
    return texto, Deteccao(CODIFICACAO_FINAL, _motivo_codificacao(texto))


def linhas_numeradas(texto: str) -> list[tuple[int, str]]:
    """Primeiras linhas não vazias com o nº da linha no arquivo (as vazias contam)."""
    numeradas = enumerate(texto.splitlines(), start=1)
    return [(n, linha) for n, linha in numeradas if linha.strip()][:LINHAS_AMOSTRA]


def linhas_amostra(texto: str) -> list[str]:
    """Primeiras linhas não vazias, usadas nas detecções."""
    return [linha for _, linha in linhas_numeradas(texto)]


def quebrar(linha: str, separador: str | None) -> list[str]:
    """Células de uma linha (sem tratar aspas; serve só para as detecções)."""
    if separador == SEPARADOR_ESPACOS:
        return re.split(SEPARADOR_ESPACOS, linha.strip())
    return linha.split(separador or SEM_SEPARADOR)


def _contagem_constante(linhas: list[str], separador: str) -> int:
    """Nº de separadores por linha se ele se repete em ≥ 90% das linhas; senão 0."""
    contagens = Counter(len(quebrar(linha, separador)) - 1 for linha in linhas)
    contagem, vezes = contagens.most_common(1)[0]
    return contagem if vezes >= FRACAO_LINHAS_CONSTANTE * len(linhas) else 0


def _separador_constante(linhas: list[str]) -> Deteccao[str | None]:
    contagens = {c: _contagem_constante(linhas, c) for c in CANDIDATOS_SEPARADOR}
    melhor = max(CANDIDATOS_SEPARADOR, key=lambda c: contagens[c])
    if contagens[melhor] == 0:
        return Deteccao(None, "Não encontramos um separador; lemos uma coluna só.")
    return Deteccao(melhor, f"Aparece {contagens[melhor]} vezes em todas as linhas.")


def detectar_separador(linhas: list[str]) -> Deteccao[str | None]:
    """O candidato que aparece o mesmo número de vezes nas linhas e gera mais colunas.

    Linhas de título acima da tabela não seguem a contagem: se não houver separador
    constante, tenta de novo a partir da 2ª, 3ª… linha (até MAX_LINHAS_TITULO).
    """
    if not linhas:
        return Deteccao(None, "Não há linhas para analisar.")
    inicios = range(max(1, min(MAX_LINHAS_TITULO, len(linhas) - 1)))
    deteccoes = (_separador_constante(linhas[inicio:]) for inicio in inicios)
    return next((d for d in deteccoes if d.valor is not None), _separador_constante(linhas))


def _tokens_decimais(linhas: list[str], separador: str | None) -> list[str]:
    celulas = (c.strip() for linha in linhas for c in quebrar(linha, separador))
    return [c for c in celulas if _NUMERO.match(c) and ("," in c or "." in c)]


def detectar_decimal(linhas: list[str], separador: str | None) -> Deteccao[str]:
    """Vírgula se ≥ 80% dos números com separador seguem o padrão 1.234,5; senão ponto."""
    tokens = _tokens_decimais(linhas, separador)
    if not tokens:
        decimal = "," if separador == ";" else "."
        return Deteccao(decimal, "Não há números com casas decimais.")
    com_virgula = [t for t in tokens if _NUMERO_VIRGULA.match(t)]
    decimal = "," if len(com_virgula) >= FRACAO_DECIMAL_VIRGULA * len(tokens) else "."
    exemplos = [t for t in tokens if decimal in t][:2] or tokens[:2]
    return Deteccao(decimal, f"Valores como {' e '.join(exemplos)}.")


def _eh_numero(celula: str) -> bool:
    return bool(_NUMERO.match(celula.strip()))


def _so_nomes_unicos(celulas: list[str]) -> bool:
    return all(c and not _eh_numero(c) for c in celulas) and len(set(celulas)) == len(celulas)


def _nome_se_repete(nomes: list[str], resto: list[list[str]]) -> bool:
    """Algum nome da 1ª linha aparece como valor na própria coluna (então é dado)."""
    return any(
        nome in {linha[i] for linha in resto if i < len(linha)} for i, nome in enumerate(nomes)
    )


def _sem_colunas_vazias(linhas: Sequence[LinhaNumerada]) -> list[LinhaNumerada]:
    """Tira as colunas vazias em todas as linhas (ex.: ";" sobrando no fim de cada linha)."""
    largura = max(len(celulas) for _, celulas in linhas)
    usadas = [i for i in range(largura) if any(i < len(c) and c[i] for _, c in linhas)]
    return [(n, [celulas[i] for i in usadas if i < len(celulas)]) for n, celulas in linhas]


def _largura_da_tabela(linhas: Sequence[LinhaNumerada]) -> int:
    return Counter(len(celulas) for _, celulas in linhas).most_common(1)[0][0]


def _linha_cheia(celulas: list[str], largura: int) -> bool:
    return len(celulas) == largura and all(celulas)


def _eh_cabecalho(celulas: list[str], largura: int, abaixo: list[list[str]]) -> bool:
    return (
        len(celulas) == largura
        and _so_nomes_unicos(celulas)
        and not _nome_se_repete(celulas, abaixo)
    )


def _motivo_cabecalho(numero: int, posicao: int) -> str:
    if posicao == 0:
        return "A 1ª linha tem só nomes, sem números."
    return f"A linha {numero} é a primeira só com nomes; as linhas acima ficam de fora."


def detectar_linha_cabecalho(linhas: Sequence[LinhaNumerada]) -> Deteccao[int]:
    """Nº da linha do cabeçalho (0 = sem cabeçalho).

    É a 1ª linha, entre as MAX_LINHAS_TITULO primeiras, com só nomes únicos na largura da
    tabela que não se repetem na própria coluna; títulos e linhas incompletas acima dela
    ficam de fora. Uma linha completa que não é cabeçalho já é dado: sem cabeçalho.
    """
    if len(linhas) < MIN_LINHAS_CABECALHO:
        return Deteccao(linhas[0][0] if linhas else 1, "O arquivo só tem uma linha.")
    tabela = _sem_colunas_vazias(linhas)
    largura = _largura_da_tabela(tabela)
    for posicao, (numero, celulas) in enumerate(tabela[:MAX_LINHAS_TITULO]):
        abaixo = [c for _, c in tabela[posicao + 1 :]]
        if _eh_cabecalho(celulas, largura, abaixo):
            return Deteccao(numero, _motivo_cabecalho(numero, posicao))
        if _linha_cheia(celulas, largura):
            break
    return Deteccao(0, "A 1ª linha parece ser de dados; criamos os nomes col_1, col_2…")
