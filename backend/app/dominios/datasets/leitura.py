"""Leitura de TXT/CSV/TSV/XLSX/JSON para DataFrame + metadados (spec 01)."""

import csv
import io
import json
import math
import re
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field

import pandas as pd

from app.dominios.datasets import erros
from app.dominios.datasets.deteccao import (
    SEM_SEPARADOR,
    SEPARADOR_ESPACOS,
    Deteccao,
    decodificar,
    detectar_decimal,
    detectar_formato,
    detectar_linha_cabecalho,
    detectar_separador,
    linhas_numeradas,
    quebrar,
)
from app.dominios.datasets.modelos import (
    Aviso,
    LinhaArquivo,
    MetadadosLeitura,
    OpcoesLeitura,
    ResultadoLeitura,
)

VALORES_FALTANTES = ("", "NA", "N/A", "NaN", "null", "None", "-", "?", "—")
SEPARADORES_SUSPEITOS = (";", ",", "\t")
NAO_SE_APLICA = "Não se aplica a este formato."
ESCOLHIDO = "Escolhido por você."
LINHAS_INICIAIS = 12  # primeiras linhas mostradas para escolher o cabeçalho
LINHAS_DETECCAO_PLANILHA = 60
_ESPACOS = re.compile(r"\s+")


@dataclass(frozen=True, slots=True, eq=False)
class _LeituraBruta:
    dados: pd.DataFrame
    codificacao: str | None = None
    separador: str | None = None
    decimal: str | None = None
    linha_cabecalho: int | None = None
    abas: tuple[str, ...] = ()
    motivos: dict[str, str] = field(default_factory=dict)
    amostra: tuple[str, ...] = ()
    linhas_iniciais: tuple[LinhaArquivo, ...] = ()


type Leitor = Callable[[bytes, str, OpcoesLeitura], _LeituraBruta]


def _ou_detectar[T](escolhido: T | None, detectar: Callable[[], Deteccao[T]]) -> Deteccao[T]:
    return detectar() if escolhido is None else Deteccao(escolhido, ESCOLHIDO)


def padronizar_nomes(nomes: list[object]) -> list[str]:
    """strip, espaços múltiplos → um, vazios → col_N e duplicados com sufixo _2, _3…"""
    resultado: list[str] = []
    for posicao, nome in enumerate(nomes, start=1):
        base = _ESPACOS.sub(" ", str(nome)).strip() if nome is not None else ""
        base = base if base and base.lower() != "nan" else f"col_{posicao}"
        candidato, sufixo = base, 2
        while candidato in resultado:
            candidato, sufixo = f"{base}_{sufixo}", sufixo + 1
        resultado.append(candidato)
    return resultado


def _celulas(linha: str, separador: str | None) -> list[str]:
    """Células de uma linha respeitando aspas (para os nomes e a prévia das linhas)."""
    if separador == SEPARADOR_ESPACOS:
        return re.split(SEPARADOR_ESPACOS, linha.strip())
    return next(csv.reader([linha], delimiter=separador or SEM_SEPARADOR), [])


def _nomes_do_cabecalho(texto: str, separador: str | None, linha: int) -> list[object]:
    linhas = texto.splitlines()
    if linha > len(linhas) or not linhas[linha - 1].strip():
        raise erros.linha_cabecalho_invalida(linha)
    return list(_celulas(linhas[linha - 1], separador))


def _nomes_das_colunas(
    texto: str, separador: str | None, linha_cabecalho: int, amostra: list[str]
) -> list[str]:
    """Nomes do cabeçalho; sem cabeçalho, col_1…col_n na largura da linha mais larga.

    A largura explícita evita que um título de uma célula só defina a tabela inteira.
    """
    if linha_cabecalho:
        return padronizar_nomes(_nomes_do_cabecalho(texto, separador, linha_cabecalho))
    largura = max((len(_celulas(linha, separador)) for linha in amostra), default=1)
    return padronizar_nomes([None] * largura)


def _ler_csv(
    texto: str, separador: str | None, decimal: str, nomes: list[str], linha_cabecalho: int
) -> pd.DataFrame:
    """Lê a tabela com os nomes dados; a linha do cabeçalho e as de cima ficam de fora."""
    try:
        return pd.read_csv(
            io.StringIO(texto),
            sep=separador or SEM_SEPARADOR,
            engine="python" if separador == SEPARADOR_ESPACOS else "c",
            decimal=decimal,
            thousands="." if decimal == "," else None,
            header=None,
            skiprows=linha_cabecalho,
            names=nomes,
            index_col=False,
            na_values=list(VALORES_FALTANTES),
            keep_default_na=False,
            skipinitialspace=True,
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as erro:
        raise erros.arquivo_ilegivel() from erro


def _linhas_iniciais_texto(texto: str, separador: str | None) -> tuple[LinhaArquivo, ...]:
    primeiras = texto.splitlines()[:LINHAS_INICIAIS]
    return tuple(
        LinhaArquivo(n, tuple(_celulas(linha, separador)) if linha.strip() else ())
        for n, linha in enumerate(primeiras, start=1)
    )


def _separador(opcoes: OpcoesLeitura, formato: str, amostra: list[str]) -> Deteccao[str | None]:
    if opcoes.separador is not None:
        return Deteccao(opcoes.separador, ESCOLHIDO)
    if formato == "tsv":
        return Deteccao("\t", "Arquivos TSV usam tabulação.")
    return detectar_separador(amostra)


def _ler_texto(conteudo: bytes, formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    texto, codificacao = decodificar(conteudo, opcoes.codificacao)
    numeradas = linhas_numeradas(texto)
    # Com a linha do cabeçalho escolhida, o título acima dela não entra nas detecções.
    escolhida = opcoes.linha_cabecalho or 0
    separador = _separador(opcoes, formato, [linha for n, linha in numeradas if n >= escolhida])
    grade = [(n, [c.strip() for c in quebrar(linha, separador.valor)]) for n, linha in numeradas]
    cabecalho = _ou_detectar(opcoes.linha_cabecalho, lambda: detectar_linha_cabecalho(grade))
    tabela = [linha for n, linha in numeradas if n >= cabecalho.valor]
    decimal = _ou_detectar(opcoes.decimal, lambda: detectar_decimal(tabela, separador.valor))
    linhas = [linha for _, linha in numeradas]
    nomes = _nomes_das_colunas(texto, separador.valor, cabecalho.valor, linhas)
    dados = _ler_csv(texto, separador.valor, decimal.valor, nomes, cabecalho.valor)
    return _LeituraBruta(
        dados=dados,
        codificacao=codificacao.valor,
        separador=separador.valor,
        decimal=decimal.valor,
        linha_cabecalho=cabecalho.valor,
        motivos={
            "codificacao": codificacao.motivo,
            "separador": separador.motivo,
            "decimal": decimal.motivo,
            "cabecalho": cabecalho.motivo,
        },
        amostra=tuple(tabela),
        linhas_iniciais=_linhas_iniciais_texto(texto, separador.valor),
    )


def _texto_da_celula(valor: object) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def _celulas_planilha(linha: pd.Series) -> tuple[str, ...]:
    celulas = tuple(_texto_da_celula(valor) for valor in linha)
    return celulas if any(celulas) else ()


def _grade_planilha(bruto: pd.DataFrame) -> list[tuple[int, list[str]]]:
    linhas = ((n, _celulas_planilha(linha)) for n, (_, linha) in enumerate(bruto.iterrows(), 1))
    return [(n, list(celulas)) for n, celulas in linhas if celulas][:LINHAS_DETECCAO_PLANILHA]


def _abrir_aba(conteudo: bytes, aba_escolhida: str | None) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Aba inteira sem cabeçalho; linha N da planilha = posição N-1. Colunas vazias saem."""
    try:
        planilha = pd.ExcelFile(io.BytesIO(conteudo), engine="openpyxl")
        abas = tuple(str(nome) for nome in planilha.sheet_names)
        bruto = planilha.parse(aba_escolhida or abas[0], header=None)
    except (ValueError, KeyError, zipfile.BadZipFile, OSError) as erro:
        raise erros.arquivo_ilegivel() from erro
    bruto = bruto.dropna(axis="columns", how="all")
    if bruto.empty:
        raise erros.arquivo_vazio()
    return bruto, abas


def _linha_valida(bruto: pd.DataFrame, linha: int) -> bool:
    return linha == 0 or (linha <= len(bruto) and bool(_celulas_planilha(bruto.iloc[linha - 1])))


def _ler_xlsx(conteudo: bytes, _formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    bruto, abas = _abrir_aba(conteudo, opcoes.aba)
    cabecalho = _ou_detectar(
        opcoes.linha_cabecalho, lambda: detectar_linha_cabecalho(_grade_planilha(bruto))
    )
    linha = cabecalho.valor
    if not _linha_valida(bruto, linha):
        raise erros.linha_cabecalho_invalida(linha)
    nomes = list(bruto.iloc[linha - 1]) if linha else [None] * bruto.shape[1]
    dados = bruto.iloc[linha:].set_axis(padronizar_nomes(nomes), axis="columns").infer_objects()
    iniciais = enumerate(bruto.head(LINHAS_INICIAIS).iterrows(), start=1)
    return _LeituraBruta(
        dados=dados,
        linha_cabecalho=linha,
        abas=abas,
        motivos={"cabecalho": cabecalho.motivo},
        linhas_iniciais=tuple(LinhaArquivo(n, _celulas_planilha(v)) for n, (_, v) in iniciais),
    )


def _tabela_json(dados: object) -> pd.DataFrame:
    if isinstance(dados, list) and dados and all(isinstance(r, dict) for r in dados):
        return pd.json_normalize(dados)
    if isinstance(dados, dict) and dados and all(isinstance(v, list) for v in dados.values()):
        try:
            return pd.DataFrame(dados)
        except ValueError as erro:
            raise erros.json_invalido() from erro
    raise erros.json_invalido()


def _ler_json(conteudo: bytes, _formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    texto, codificacao = decodificar(conteudo, opcoes.codificacao)
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise erros.json_invalido() from erro
    tabela = _tabela_json(dados)
    tabela.columns = pd.Index(padronizar_nomes(list(tabela.columns)))
    return _LeituraBruta(
        dados=tabela,
        codificacao=codificacao.valor,
        motivos={"codificacao": codificacao.motivo},
    )


LEITORES: dict[str, Leitor] = {
    "txt": _ler_texto,
    "csv": _ler_texto,
    "tsv": _ler_texto,
    "xlsx": _ler_xlsx,
    "json": _ler_json,
}


def _limpar_textos(serie: pd.Series) -> pd.Series:
    """Tira espaços das pontas e troca marcadores de faltante (NA, -, ?, …) por NaN."""
    if pd.api.types.is_numeric_dtype(serie) or pd.api.types.is_bool_dtype(serie):
        return serie
    aparada = serie.map(lambda valor: valor.strip() if isinstance(valor, str) else valor)
    return aparada.mask(aparada.isin(VALORES_FALTANTES))


def padronizar_dados(dados: pd.DataFrame) -> pd.DataFrame:
    """Faltantes padronizados, linhas vazias fora e índice = nº da linha (1…n, D49)."""
    limpos = dados.apply(_limpar_textos).infer_objects().dropna(how="all")
    return limpos.set_axis(pd.RangeIndex(1, len(limpos) + 1), axis="index")


def _avisos(bruta: _LeituraBruta, n_colunas: int) -> tuple[Aviso, ...]:
    suspeita = any(s in linha for linha in bruta.amostra for s in SEPARADORES_SUSPEITOS)
    if n_colunas == 1 and suspeita:
        mensagem = (
            "Encontramos só uma coluna. O separador pode estar errado — tente escolher outro."
        )
        return (Aviso("UMA_COLUNA", mensagem),)
    return ()


def _metadados(
    formato: Deteccao[str], bruta: _LeituraBruta, dados: pd.DataFrame
) -> MetadadosLeitura:
    motivos = {
        "formato": formato.motivo,
        "codificacao": NAO_SE_APLICA,
        "separador": NAO_SE_APLICA,
        "decimal": NAO_SE_APLICA,
    }
    return MetadadosLeitura(
        formato=formato.valor,
        codificacao=bruta.codificacao,
        separador=bruta.separador,
        decimal=bruta.decimal,
        linha_cabecalho=bruta.linha_cabecalho,
        n_linhas=len(dados),
        n_colunas=dados.shape[1],
        abas=bruta.abas,
        avisos=_avisos(bruta, dados.shape[1]),
        motivos=motivos | bruta.motivos,
        linhas_iniciais=bruta.linhas_iniciais,
    )


def ler_arquivo(conteudo: bytes, nome_arquivo: str, opcoes: OpcoesLeitura) -> ResultadoLeitura:
    """Lê o arquivo detectando formato, codificação, separador, decimal e cabeçalho."""
    formato = detectar_formato(nome_arquivo)
    if not conteudo.strip():
        raise erros.arquivo_vazio()
    bruta = LEITORES[formato.valor](conteudo, formato.valor, opcoes)
    dados = padronizar_dados(bruta.dados)
    if dados.empty:
        raise erros.arquivo_vazio()
    return ResultadoLeitura(dados=dados, metadados=_metadados(formato, bruta, dados))
