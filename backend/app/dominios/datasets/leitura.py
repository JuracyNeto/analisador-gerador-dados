"""Leitura de TXT/CSV/TSV/XLSX/JSON para DataFrame + metadados (spec 01)."""

import csv
import io
import json
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
    detectar_cabecalho,
    detectar_decimal,
    detectar_formato,
    detectar_separador,
    linhas_amostra,
)
from app.dominios.datasets.modelos import Aviso, MetadadosLeitura, OpcoesLeitura, ResultadoLeitura

VALORES_FALTANTES = ("", "NA", "N/A", "NaN", "null", "None", "-", "?", "—")
SEPARADORES_SUSPEITOS = (";", ",", "\t")
NAO_SE_APLICA = "Não se aplica a este formato."
ESCOLHIDO = "Escolhido por você."
_ESPACOS = re.compile(r"\s+")


@dataclass(frozen=True, slots=True, eq=False)
class _LeituraBruta:
    dados: pd.DataFrame
    codificacao: str | None = None
    separador: str | None = None
    decimal: str | None = None
    tem_cabecalho: bool | None = None
    abas: tuple[str, ...] = ()
    motivos: dict[str, str] = field(default_factory=dict)
    amostra: tuple[str, ...] = ()


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


def _nomes_do_cabecalho(texto: str, separador: str | None) -> list[object]:
    primeira = next(linha for linha in texto.splitlines() if linha.strip())
    if separador == SEPARADOR_ESPACOS:
        return list(re.split(SEPARADOR_ESPACOS, primeira.strip()))
    return list(next(csv.reader([primeira], delimiter=separador or SEM_SEPARADOR)))


def _ler_csv(texto: str, separador: str | None, decimal: str, tem_cabecalho: bool) -> pd.DataFrame:
    nomes = padronizar_nomes(_nomes_do_cabecalho(texto, separador)) if tem_cabecalho else None
    try:
        dados = pd.read_csv(
            io.StringIO(texto),
            sep=separador or SEM_SEPARADOR,
            engine="python" if separador == SEPARADOR_ESPACOS else "c",
            decimal=decimal,
            thousands="." if decimal == "," else None,
            header=None,
            skiprows=1 if tem_cabecalho else 0,
            names=nomes,
            index_col=False,
            na_values=list(VALORES_FALTANTES),
            keep_default_na=False,
            skipinitialspace=True,
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as erro:
        raise erros.arquivo_ilegivel() from erro
    if nomes is None:
        dados.columns = pd.Index(padronizar_nomes([None] * dados.shape[1]))
    return dados


def _separador(opcoes: OpcoesLeitura, formato: str, amostra: list[str]) -> Deteccao[str | None]:
    if opcoes.separador is not None:
        return Deteccao(opcoes.separador, ESCOLHIDO)
    if formato == "tsv":
        return Deteccao("\t", "Arquivos TSV usam tabulação.")
    return detectar_separador(amostra)


def _ler_texto(conteudo: bytes, formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    texto, codificacao = decodificar(conteudo, opcoes.codificacao)
    amostra = linhas_amostra(texto)
    separador = _separador(opcoes, formato, amostra)
    decimal = _ou_detectar(opcoes.decimal, lambda: detectar_decimal(amostra, separador.valor))
    cabecalho = _ou_detectar(
        opcoes.tem_cabecalho, lambda: detectar_cabecalho(amostra, separador.valor)
    )
    dados = _ler_csv(texto, separador.valor, decimal.valor, cabecalho.valor)
    return _LeituraBruta(
        dados=dados,
        codificacao=codificacao.valor,
        separador=separador.valor,
        decimal=decimal.valor,
        tem_cabecalho=cabecalho.valor,
        motivos={
            "codificacao": codificacao.motivo,
            "separador": separador.motivo,
            "decimal": decimal.motivo,
            "cabecalho": cabecalho.motivo,
        },
        amostra=tuple(amostra),
    )


def _ler_xlsx(conteudo: bytes, _formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    try:
        planilha = pd.ExcelFile(io.BytesIO(conteudo), engine="openpyxl")
        abas = tuple(str(nome) for nome in planilha.sheet_names)
        aba = opcoes.aba or abas[0]
        bruto = planilha.parse(aba, header=None)
    except (ValueError, KeyError, zipfile.BadZipFile, OSError) as erro:
        raise erros.arquivo_ilegivel() from erro
    tem_cabecalho = opcoes.tem_cabecalho is not False
    dados = bruto.iloc[1:] if tem_cabecalho else bruto
    nomes = list(bruto.iloc[0]) if tem_cabecalho else [None] * bruto.shape[1]
    dados = dados.set_axis(padronizar_nomes(nomes), axis="columns").infer_objects()
    motivo_cabecalho = ESCOLHIDO if opcoes.tem_cabecalho is not None else f"1ª linha da aba {aba}."
    return _LeituraBruta(
        dados=dados,
        tem_cabecalho=tem_cabecalho,
        abas=abas,
        motivos={"cabecalho": motivo_cabecalho},
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
        tem_cabecalho=True,
        motivos={"codificacao": codificacao.motivo, "cabecalho": "Nomes vêm das chaves do JSON."},
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
        tem_cabecalho=bruta.tem_cabecalho,
        n_linhas=len(dados),
        n_colunas=dados.shape[1],
        abas=bruta.abas,
        avisos=_avisos(bruta, dados.shape[1]),
        motivos=motivos | bruta.motivos,
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
