"""Linhas iguais e quase iguais (R5, spec 12, D120).

Iguais: as mesmas células em todas as colunas comparadas. Quase iguais: numéricas padronizadas
a distância euclidiana < 0,01·√p, as demais colunas (e os faltantes) iguais, sem serem idênticas.
As numéricas vazias nas duas linhas ficam de fora: p, a grade e o acaso são os das preenchidas.

Com poucas colunas ou valores de pouca precisão, pares assim aparecem por acaso. O acaso vem da
densidade local: na grade da precisão de cada coluna (passos de 0,01 com 2 casas…), dados reais
têm tantos pares numa posição vizinha quanto na mesma posição. Conta-se quantos pares cabem, em
média, em cada posição de uma caixa de vizinhança, e daí os iguais e os quase iguais esperados.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from app.compartilhado import estatistica
from app.compartilhado.series import casas_decimais
from app.dominios.detector.tabela import ColunaDetector

FATOR_DISTANCIA = 0.01
VIZINHANCA = 3
"""A caixa de referência vai a 3 raios das quase iguais em cada coluna (e a 1 passo, no mínimo)."""
MAX_POSICOES_CONTADAS = 200_000
FOLGA = 1e-6
AMOSTRA_ACASO = 20_000
"""Acima disso, o acaso das iguais vem de uma amostra (contar vizinhos cresce com n)."""
AMOSTRA_REFERENCIA = 1_000
"""Padrões com vazias: a densidade por par sai de até 1.000 linhas com as mesmas preenchidas."""
SEMENTE_AMOSTRA = 0
SEM_PARES = np.empty((0, 2), dtype="int64")
TRINCA = 3
"""3 linhas iguais seguidas ou mais: o padrão de "copiar e colar" (suspeita alta)."""
MINIMO_PREENCHIDAS = 2


@dataclass(frozen=True, slots=True, eq=False)
class ColunasComparaveis:
    """Chaves das linhas: números (n × p, NaN nos faltantes) e códigos das demais colunas."""

    numeros: np.ndarray
    codigos: np.ndarray
    """n × q: cada texto vira um código; faltante = −1."""
    grupos: np.ndarray
    """O mesmo número para linhas com os mesmos códigos (agrupadas uma vez só)."""

    @property
    def n(self) -> int:
        return len(self.numeros)

    @property
    def p(self) -> int:
        return int(self.numeros.shape[1])

    def recorte(self, linhas: np.ndarray, numericas: np.ndarray) -> "ColunasComparaveis":
        """Só as linhas e as numéricas dadas; as demais colunas ficam todas."""
        numeros = self.numeros[np.ix_(linhas, numericas)]
        return ColunasComparaveis(numeros, self.codigos[linhas], self.grupos[linhas])


@dataclass(frozen=True, slots=True)
class ContraOAcaso:
    """Quantos casos foram vistos e quantos o acaso produziria (média de uma Poisson)."""

    observados: int
    esperados: float

    @property
    def p_valor(self) -> float:
        """P(X ≥ observados), X ~ Poisson(esperados)."""
        return estatistica.teste_poisson_unilateral(self.observados, self.esperados)


@dataclass(frozen=True, slots=True)
class AcasoDasRepeticoes:
    iguais: ContraOAcaso
    quase: ContraOAcaso


@dataclass(frozen=True, slots=True, eq=False)
class GrupoRepetido:
    """Posições (crescentes) de linhas iguais ou quase iguais entre si."""

    posicoes: np.ndarray
    exato: bool
    sequencia: tuple[int, int]
    """(primeira posição, tamanho) do maior trecho de linhas seguidas do grupo."""

    @property
    def copias(self) -> int:
        return len(self.posicoes) - 1

    @property
    def maior_sequencia(self) -> np.ndarray:
        inicio, tamanho = self.sequencia
        return np.arange(inicio, inicio + tamanho)


def chaves_das_colunas(colunas: Sequence[ColunaDetector]) -> ColunasComparaveis:
    """Separa as numéricas (para a distância) das demais (comparadas pelo texto)."""
    n = len(colunas[0].textos)
    numericas = [coluna.numeros for coluna in colunas if coluna.numeros is not None]
    codigos = [
        pd.factorize(pd.Series(coluna.textos, dtype=object))[0]
        for coluna in colunas
        if coluna.numeros is None
    ]
    return ColunasComparaveis(
        numeros=np.column_stack(numericas) if numericas else np.empty((n, 0)),
        codigos=np.column_stack(codigos) if codigos else np.empty((n, 0), dtype="int64"),
        grupos=_ids(np.column_stack(codigos)) if codigos else np.zeros(n, dtype="int64"),
    )


def linhas_com_numero(colunas: Sequence[ColunaDetector]) -> np.ndarray:
    """Linhas com algum valor nas numéricas; sem numéricas, todas (R5, R6; D138).

    Uma linha só com textos fixos (a hora de uma estação desligada) não é cópia de outra.
    """
    numericas = [coluna.numeros for coluna in colunas if coluna.numeros is not None]
    if not numericas:
        return np.ones(len(colunas[0].textos), dtype=bool)
    return np.asarray(~np.isnan(np.column_stack(numericas)).all(axis=1), dtype=bool)


def _preenchida(coluna: ColunaDetector) -> np.ndarray:
    if coluna.numeros is not None:
        return np.asarray(~np.isnan(coluna.numeros), dtype=bool)
    return np.array([texto is not None for texto in coluna.textos], dtype=bool)


def linhas_comparaveis(colunas: Sequence[ColunaDetector]) -> np.ndarray:
    """Linhas com algum número e 2 células preenchidas ou mais (R5; D138, D171).

    "Anexar ao arquivo atual" (Gerador) preenche só a coluna gerada: um valor só não faz de
    uma linha a cópia de outra.
    """
    preenchidas = np.sum([_preenchida(coluna) for coluna in colunas], axis=0)
    return linhas_com_numero(colunas) & (preenchidas >= MINIMO_PREENCHIDAS)


# Grupos -------------------------------------------------------------------------------------


def _ids(linhas: np.ndarray) -> np.ndarray:
    """Mesmo número para linhas iguais da matriz (agrupamento por hash, rápido em n grande)."""
    tabela = pd.DataFrame(linhas)
    return tabela.groupby(list(tabela.columns), sort=False).ngroup().to_numpy(dtype="int64")


def ids_exatos(chaves: ColunasComparaveis) -> np.ndarray:
    """O mesmo número para linhas iguais em todas as colunas comparadas (faltante = faltante)."""
    numeros = chaves.numeros
    return _ids(np.column_stack([chaves.codigos, np.nan_to_num(numeros), np.isnan(numeros)]))


def _ids_sem_numeros(chaves: ColunasComparaveis) -> np.ndarray:
    """Mesmo número para linhas com as mesmas não numéricas e os mesmos faltantes."""
    return _ids(np.column_stack([chaves.grupos, np.isnan(chaves.numeros)]))


def _pares_de_mesmo_id(ids: np.ndarray) -> np.ndarray:
    """Liga cada linha à próxima com o mesmo id (basta para formar as componentes)."""
    ordem = np.argsort(ids, kind="stable")
    mesmos = ids[ordem][1:] == ids[ordem][:-1]
    return np.column_stack((ordem[:-1][mesmos], ordem[1:][mesmos]))


def _grupos_por_id(ids: np.ndarray) -> list[np.ndarray]:
    """Posições de cada id com 2 linhas ou mais."""
    ordem = np.argsort(ids, kind="stable")
    fronteiras = np.flatnonzero(np.diff(ids[ordem])) + 1
    return [grupo for grupo in np.split(ordem, fronteiras) if len(grupo) > 1]


def _componentes(pares: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(posições, rótulo do grupo) das linhas ligadas pelos pares, por grupo e posição."""
    if len(pares) == 0:
        return np.empty(0, dtype="int64"), np.empty(0, dtype="int64")
    nos, locais = np.unique(pares, return_inverse=True)
    locais = locais.reshape(pares.shape)
    grafo = coo_matrix((np.ones(len(pares)), (locais[:, 0], locais[:, 1])), (len(nos),) * 2)
    _, rotulos = connected_components(grafo, directed=False)
    ordem = np.lexsort((nos, rotulos))
    return nos[ordem], np.asarray(rotulos[ordem], dtype="int64")


def _maiores_sequencias(
    posicoes: np.ndarray, rotulos: np.ndarray, inicios: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Primeira posição e tamanho do maior trecho de linhas seguidas de cada grupo."""
    quebra = np.r_[True, (np.diff(posicoes) != 1) | (np.diff(rotulos) != 0)]
    trechos = np.flatnonzero(quebra)
    tamanhos = np.diff(np.r_[trechos, len(posicoes)])
    grupo = np.searchsorted(inicios, trechos, side="right") - 1
    ordem = np.lexsort((-tamanhos, grupo))
    melhores = ordem[np.r_[True, np.diff(grupo[ordem]) != 0]]
    return posicoes[trechos[melhores]], tamanhos[melhores]


def repetidos(chaves: ColunasComparaveis, quase: np.ndarray) -> tuple[GrupoRepetido, ...]:
    """Grupos de linhas idênticas, ligados também pelos pares quase iguais dados."""
    ids = ids_exatos(chaves)
    posicoes, rotulos = _componentes(np.concatenate([_pares_de_mesmo_id(ids), quase]))
    if len(posicoes) == 0:
        return ()
    inicios = np.flatnonzero(np.r_[True, np.diff(rotulos) != 0])
    ids_dos_grupos = ids[posicoes]
    exatos = np.minimum.reduceat(ids_dos_grupos, inicios) == np.maximum.reduceat(
        ids_dos_grupos, inicios
    )
    comecos, tamanhos = _maiores_sequencias(posicoes, rotulos, inicios)
    grupos = [
        GrupoRepetido(parte, bool(exato), (int(comeco), int(tamanho)))
        for parte, exato, comeco, tamanho in zip(
            np.split(posicoes, inicios[1:]), exatos, comecos, tamanhos, strict=True
        )
    ]
    return tuple(sorted(grupos, key=lambda grupo: int(grupo.posicoes[0])))


# Quase iguais -------------------------------------------------------------------------------


def _desvios(numeros: np.ndarray) -> np.ndarray:
    desvios = np.nanstd(numeros, axis=0, ddof=1)
    return np.where(np.isfinite(desvios) & (desvios > 0), desvios, 1.0)


def _padronizados(numeros: np.ndarray) -> np.ndarray:
    """z por coluna, com 0 nos faltantes (o padrão de faltantes já separa as linhas)."""
    z = (numeros - np.nanmean(numeros, axis=0)) / _desvios(numeros)
    return np.asarray(np.nan_to_num(z), dtype="float64")


def _raio(p: int) -> float:
    return FATOR_DISTANCIA * math.sqrt(p)


def _preenchidas(chaves: ColunasComparaveis, posicao: int) -> np.ndarray:
    """Numéricas com valor na linha (todas as linhas de um grupo têm os mesmos faltantes)."""
    return np.asarray(~np.isnan(chaves.numeros[posicao]), dtype=bool)


def pares_quase_iguais(chaves: ColunasComparaveis) -> np.ndarray:
    """Pares não idênticos com as demais colunas iguais e distância padronizada < 0,01·√p.

    p conta só as numéricas preenchidas nas duas linhas: as vazias ficam de fora (D171).
    """
    pontos = _padronizados(chaves.numeros)
    pares = [SEM_PARES]
    for posicoes in _grupos_por_id(_ids_sem_numeros(chaves)):
        raio = float(np.nextafter(_raio(int(_preenchidas(chaves, posicoes[0]).sum())), 0))
        locais = cKDTree(pontos[posicoes]).query_pairs(raio, output_type="ndarray")
        pares.append(posicoes[locais])
    juntos = np.concatenate(pares)
    exatos = ids_exatos(chaves)
    return np.asarray(juntos[exatos[juntos[:, 0]] != exatos[juntos[:, 1]]], dtype="int64")


# Acaso --------------------------------------------------------------------------------------


def _passos(numeros: np.ndarray) -> np.ndarray:
    """Passo da precisão de cada coluna, na unidade dela (0,01 com 2 casas)."""
    casas = [casas_decimais(pd.Series(coluna)) for coluna in numeros.T]
    return np.array([10.0**-c for c in casas], dtype="float64")


def _posicoes_no_raio(passos: np.ndarray, raio: float) -> float:
    """Posições da grade (fora a origem) a distância < raio: as dos pares quase iguais."""
    alcance = np.floor(raio / passos).astype("int64")
    if np.prod(2.0 * alcance + 1) > MAX_POSICOES_CONTADAS:
        bola = math.pi ** (len(passos) / 2) / math.gamma(len(passos) / 2 + 1) * raio ** len(passos)
        return float(bola / np.prod(passos))
    grade = np.stack(np.meshgrid(*(np.arange(-a, a + 1) for a in alcance)), -1)
    distancias = np.sqrt(np.sum((grade * passos) ** 2, axis=-1))
    return float(np.count_nonzero(distancias < raio) - 1)


def _pares_na_caixa(chaves: ColunasComparaveis, meia_caixa: np.ndarray) -> int:
    """Pares com as demais colunas iguais e cada número a até `meia_caixa` (na unidade dele).

    As linhas não têm vazias nas numéricas dadas (um padrão de vazias por vez).
    """
    pontos = chaves.numeros / meia_caixa
    total = 0
    for posicoes in _grupos_por_id(chaves.grupos):
        arvore = cKDTree(pontos[posicoes])
        total += (int(arvore.count_neighbors(arvore, 1 + FOLGA, p=np.inf)) - len(posicoes)) // 2
    return total


def _pares_identicos(chaves: ColunasComparaveis) -> int:
    _, contagens = np.unique(ids_exatos(chaves), return_counts=True)
    return int(np.sum(contagens * (contagens - 1) // 2))


def _sorteadas(n: int, tamanho: int) -> np.ndarray:
    """Posições sorteadas com semente fixa (todas, se não passam de `tamanho`)."""
    if n <= tamanho:
        return np.arange(n)
    return np.sort(np.random.default_rng(SEMENTE_AMOSTRA).choice(n, tamanho, replace=False))


def _amostra(chaves: ColunasComparaveis) -> ColunasComparaveis:
    """Linhas sorteadas com semente fixa: o acaso de arquivos grandes sai delas."""
    escolhidas = _sorteadas(chaves.n, AMOSTRA_ACASO)
    return ColunasComparaveis(
        chaves.numeros[escolhidas], chaves.codigos[escolhidas], chaves.grupos[escolhidas]
    )


@dataclass(frozen=True, slots=True)
class _Caixa:
    """Vizinhança de referência: até 3 raios (ou 1 passo) em cada numérica."""

    meia: np.ndarray
    posicoes: float
    """Todas as posições da grade na caixa, com a origem."""
    no_raio: float
    """Posições a distância < raio da origem (fora ela): as dos pares quase iguais."""

    @property
    def em_volta(self) -> float:
        """Posições da caixa fora a origem e o raio das quase iguais."""
        return self.posicoes - 1 - self.no_raio


@dataclass(frozen=True, slots=True)
class _Grade:
    """Passo da precisão e desvio padrão de cada numérica (na unidade dela)."""

    passos: np.ndarray
    desvios: np.ndarray

    def caixa(self, colunas: np.ndarray) -> _Caixa:
        """Caixa nas numéricas dadas, com o raio 0,01·√p de p = quantas são."""
        passos = self.passos[colunas]
        passos_z = passos / self.desvios[colunas]
        raio = _raio(len(passos))
        alcance = np.maximum(np.ceil(VIZINHANCA * raio / passos_z), 1)
        no_raio = _posicoes_no_raio(passos_z, raio)
        return _Caixa(alcance * passos, float(np.prod(2 * alcance + 1)), no_raio)


def _por_posicao(chaves: ColunasComparaveis, caixa: _Caixa, ja_contados: int) -> float:
    """Pares por posição da grade, contados na caixa fora os iguais e quase iguais."""
    return max(_pares_na_caixa(chaves, caixa.meia) - ja_contados, 0) / caixa.em_volta


def _por_posicao_no_arquivo(chaves: ColunasComparaveis, caixa: _Caixa, ja_contados: int) -> float:
    """Até 20.000 linhas, conta tudo; acima, conta na amostra e escala por n(n−1)/(m(m−1))."""
    if chaves.n <= AMOSTRA_ACASO:
        return _por_posicao(chaves, caixa, ja_contados)
    amostra = _amostra(chaves)
    escala = chaves.n * (chaves.n - 1) / (amostra.n * (amostra.n - 1))
    return _por_posicao(amostra, caixa, _pares_identicos(amostra)) * escala


def _coincidencia(coluna: np.ndarray) -> float:
    """Chance de duas linhas sorteadas (sem reposição) terem o mesmo valor na coluna."""
    _, contagens = np.unique(coluna, return_counts=True)
    n = len(coluna)
    return float(np.sum(contagens * (contagens - 1)) / (n * (n - 1)))


def _iguais_independentes(chaves: ColunasComparaveis) -> float:
    """C(n,2) · Π P(coincidir na coluna j): o acaso se as colunas fossem independentes."""
    colunas = [*chaves.numeros.T, *chaves.codigos.T]
    return chaves.n * (chaves.n - 1) / 2 * math.prod(_coincidencia(c) for c in colunas)


def _pares_possiveis(chaves: ColunasComparaveis) -> int:
    """Pares de linhas com as demais colunas iguais: só eles podem ser iguais ou quase iguais."""
    _, contagens = np.unique(chaves.grupos, return_counts=True)
    return int(np.sum(contagens * (contagens - 1) // 2))


def _por_par_e_posicao(referencia: ColunasComparaveis, caixa: _Caixa) -> float:
    """Pares na caixa inteira por par possível e por posição da grade."""
    possiveis = _pares_possiveis(referencia)
    if possiveis == 0:
        return 0.0
    return _pares_na_caixa(referencia, caixa.meia) / (possiveis * caixa.posicoes)


def _acaso_do_padrao(
    chaves: ColunasComparaveis, posicoes: np.ndarray, grade: _Grade, ja_contados: int
) -> tuple[float, float]:
    """(iguais, quase iguais) esperados entre as linhas com as mesmas numéricas vazias.

    Sem vazias, como sempre: os pares em volta das linhas do arquivo (D120). Com vazias, as
    linhas se comparam só nas preenchidas, e os grupos costumam ser pequenos (a caixa ficava
    vazia, e o acaso, zero): a densidade sai de todas as linhas com essas colunas preenchidas,
    na caixa inteira, por par possível. O piso das colunas independentes também fica nas
    preenchidas: no arquivo todo, "as duas vazias" contava como coincidência (D171).
    """
    preenchidas = _preenchidas(chaves, posicoes[0])
    caixa = grade.caixa(preenchidas)
    proprias = chaves.recorte(posicoes, preenchidas)
    if preenchidas.all():
        por_posicao = _por_posicao_no_arquivo(proprias, caixa, ja_contados)
    else:
        # A taxa é por par: numa amostra das linhas de referência, não precisa de escala.
        com_elas = np.flatnonzero(~np.isnan(chaves.numeros[:, preenchidas]).any(axis=1))
        sorteadas = com_elas[_sorteadas(len(com_elas), AMOSTRA_REFERENCIA)]
        referencia = chaves.recorte(sorteadas, preenchidas)
        por_posicao = _pares_possiveis(proprias) * _por_par_e_posicao(referencia, caixa)
    return max(por_posicao, _iguais_independentes(proprias)), por_posicao * caixa.no_raio


def _pares_por_padrao(
    padroes: np.ndarray, identicos: Sequence[GrupoRepetido], quase: np.ndarray
) -> np.ndarray:
    """Pares iguais e quase iguais de cada padrão de faltantes (as duas linhas têm o mesmo)."""
    contados = np.zeros(int(padroes.max()) + 1)
    tamanhos = np.array([len(g.posicoes) for g in identicos], dtype="float64")
    primeiras = np.array([g.posicoes[0] for g in identicos], dtype="int64")
    np.add.at(contados, padroes[primeiras], tamanhos * (tamanhos - 1) / 2)
    np.add.at(contados, padroes[quase[:, 0]], 1)
    return contados


def acaso_das_repeticoes(
    chaves: ColunasComparaveis, identicos: Sequence[GrupoRepetido], quase: np.ndarray
) -> AcasoDasRepeticoes:
    """Iguais e quase iguais observados × esperados pela densidade local (Poisson).

    Cada padrão de vazias nas numéricas tem a sua grade, só com as colunas preenchidas (D171).
    """
    iguais = sum(len(g.posicoes) * (len(g.posicoes) - 1) // 2 for g in identicos)
    if chaves.p == 0:
        independentes = _iguais_independentes(chaves)
        return AcasoDasRepeticoes(ContraOAcaso(iguais, independentes), ContraOAcaso(0, 0.0))
    grade = _Grade(_passos(chaves.numeros), _desvios(chaves.numeros))
    padroes = _ids(np.isnan(chaves.numeros))
    contados = _pares_por_padrao(padroes, identicos, quase)
    esperados = np.zeros(2)
    for posicoes in _grupos_por_id(padroes):
        ja_contados = int(contados[padroes[posicoes[0]]])
        esperados += _acaso_do_padrao(chaves, posicoes, grade, ja_contados)
    return AcasoDasRepeticoes(
        ContraOAcaso(iguais, float(esperados[0])), ContraOAcaso(len(quase), float(esperados[1]))
    )


def seguidas_contra_o_acaso(grupos: Sequence[GrupoRepetido], n: int) -> ContraOAcaso:
    """Grupos com 3 linhas seguidas × trincas esperadas com as linhas em ordem aleatória."""
    seguidas = sum(len(g.maior_sequencia) >= TRINCA for g in grupos)
    tamanhos = np.array([len(g.posicoes) for g in grupos], dtype="float64")
    esperadas = float(np.sum(tamanhos * (tamanhos - 1) * (tamanhos - 2)) / (n * (n - 1)))
    return ContraOAcaso(seguidas, esperadas)
