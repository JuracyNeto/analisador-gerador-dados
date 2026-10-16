"""Regra base do detector (Template Method, D118).

`executar` pega os alvos do seletor e faz, para cada um: requisito (aplicável?) → medir →
dispara? → aviso. Seletor e requisito são objetos compostos (reaproveitados entre regras);
medir, dispara e o conteúdo do aviso são os passos de cada regra. Textos vêm de `textos.py`.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass, replace
from itertools import combinations
from typing import Protocol

import numpy as np

from app.compartilhado.tipos import TIPOS_NUMERICOS, Severidade, TipoVariavel
from app.dominios.detector import digitos, tempo, textos
from app.dominios.detector.exemplos import exemplo_do_trecho
from app.dominios.detector.resultados import (
    Aviso,
    DetalhesAviso,
    ExemploAviso,
    Grafico,
    RegraNaoAplicada,
    TextosAviso,
)
from app.dominios.detector.tabela import ColunaDetector, FormaColuna, TabelaDetector

LIMIAR_P = 0.01
"""Nível de significância das regras do detector (spec 12)."""
PROPORCAO_MUITOS_ZEROS = 0.25
"""Com um quarto dos valores em zero, o 1º quartil já é zero (R6, R7; D143, D144)."""


class Alvo(Protocol):
    """O que a regra examina: uma coluna, um par ou o arquivo todo."""

    @property
    def rotulo(self) -> str | None: ...


@dataclass(frozen=True, slots=True, eq=False)
class AlvoColuna:
    """Uma coluna numérica: números das linhas e valores válidos, na ordem do arquivo."""

    nome: str
    tipo: TipoVariavel
    linhas: np.ndarray
    valores: np.ndarray
    forma: FormaColuna | None = None
    zeros: int = 0
    """Zeros tirados da coluna (R4 e R9; D134)."""
    linha_do_tempo: str | None = None
    """Coluna de data que as linhas seguem (R11; D137)."""

    @property
    def rotulo(self) -> str:
        return self.nome

    @property
    def n(self) -> int:
        return len(self.valores)


@dataclass(frozen=True, slots=True, eq=False)
class AlvoPar:
    """Duas colunas numéricas: números das linhas com os dois valores e os valores, em ordem."""

    x: str
    y: str
    linhas: np.ndarray
    valores_x: np.ndarray
    valores_y: np.ndarray
    linha_do_tempo: str | None = None
    """Coluna de data que as linhas seguem (R2; D137)."""

    @property
    def rotulo(self) -> str:
        return f"{self.x} e {self.y}"

    @property
    def n(self) -> int:
        return len(self.linhas)


# Seletores (passo "alvos") ------------------------------------------------------------------


class SeletorAlvos[A](Protocol):
    """Escolhe na tabela o que a regra examina e diz o motivo quando não há nada."""

    @property
    def motivo_sem_alvos(self) -> str: ...

    def __call__(self, tabela: TabelaDetector) -> tuple[A, ...]: ...


@dataclass(frozen=True, slots=True)
class ColunasDoTipo:
    """Cada coluna numérica dos tipos dados vira um alvo, com os valores válidos."""

    tipos: Collection[TipoVariavel]
    motivo_sem_alvos: str

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoColuna, ...]:
        return tuple(
            AlvoColuna(coluna.nome, coluna.tipo, *tabela.valores_validos(coluna), coluna.forma)
            for coluna in tabela.do_tipo(self.tipos)
        )


COLUNAS_NUMERICAS = ColunasDoTipo(TIPOS_NUMERICOS, textos.SEM_NUMERICAS)
COLUNAS_CONTINUAS = ColunasDoTipo(frozenset({TipoVariavel.CONTINUA}), textos.SEM_CONTINUAS)


def muitos_zeros(valores: np.ndarray) -> bool:
    """Sem negativos e com 25% ou mais de zeros: os quartis medem quantas vezes houve medida.

    Na chuva por dia (72% de zeros), Q1 = 0 e Q3 = 0,2 mm. Com negativos (saldo), zero é um
    valor do meio como os outros (D143).
    """
    if len(valores) == 0 or bool(np.any(valores < 0)):
        return False
    return bool(np.mean(valores == 0) >= PROPORCAO_MUITOS_ZEROS)


def sempre(_valores: np.ndarray) -> bool:
    return True


def _sem_zeros(alvo: AlvoColuna) -> AlvoColuna:
    manter = alvo.valores != 0
    zeros = int(alvo.n - manter.sum())
    return replace(alvo, linhas=alvo.linhas[manter], valores=alvo.valores[manter], zeros=zeros)


@dataclass(frozen=True, slots=True)
class SemZeros:
    """As colunas do seletor sem os zeros, quando `quando` vale para os valores (D134, D143).

    Zero é "nada medido" (vento calmo, dia sem chuva), não um valor arredondado: R4 e R9 tiram
    sempre; R7, só quando são muitos (um 0 no meio de alturas continua distante).
    """

    seletor: ColunasDoTipo
    quando: Callable[[np.ndarray], bool] = sempre

    @property
    def motivo_sem_alvos(self) -> str:
        return self.seletor.motivo_sem_alvos

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoColuna, ...]:
        return tuple(
            _sem_zeros(alvo) if self.quando(alvo.valores) else alvo for alvo in self.seletor(tabela)
        )


NUMERICAS_SEM_ZEROS = SemZeros(COLUNAS_NUMERICAS)
NUMERICAS_SEM_MUITOS_ZEROS = SemZeros(COLUNAS_NUMERICAS, muitos_zeros)


def _par(tabela: TabelaDetector, x: ColunaDetector, y: ColunaDetector) -> AlvoPar:
    """O par só com as linhas em que as duas colunas têm valor."""
    numeros_x, numeros_y = tabela.numeros(x), tabela.numeros(y)
    validos = ~(np.isnan(numeros_x) | np.isnan(numeros_y))
    return AlvoPar(x.nome, y.nome, tabela.linhas[validos], numeros_x[validos], numeros_y[validos])


@dataclass(frozen=True, slots=True)
class ParesNumericos:
    """Cada par de colunas numéricas (na ordem do arquivo) vira um alvo."""

    motivo_sem_alvos: str = textos.SEM_PAR_NUMERICO

    def __call__(self, tabela: TabelaDetector) -> tuple[AlvoPar, ...]:
        return tuple(_par(tabela, x, y) for x, y in combinations(tabela.numericas(), 2))


PARES_NUMERICOS = ParesNumericos()


@dataclass(frozen=True, slots=True)
class NaLinhaDoTempo[A: (AlvoColuna, AlvoPar)]:
    """Os alvos do seletor com a coluna de data que as linhas seguem, se houver (D137).

    Numa série no tempo, valores vizinhos são parecidos e a relação entre colunas muda com as
    estações: a R11 fica informativa e a R2 cai para atenção.
    """

    seletor: SeletorAlvos[A]

    @property
    def motivo_sem_alvos(self) -> str:
        return self.seletor.motivo_sem_alvos

    def __call__(self, tabela: TabelaDetector) -> tuple[A, ...]:
        alvos = self.seletor(tabela)
        nome = tempo.coluna_do_tempo(tabela) if alvos else None
        return tuple(replace(alvo, linha_do_tempo=nome) for alvo in alvos)


# Requisitos (passo "aplicável?") ------------------------------------------------------------


class Requisito[A](Protocol):
    """Por que a regra não se aplica ao alvo, ou None se ela se aplica."""

    def __call__(self, alvo: A) -> str | None: ...


class AlvoContado(Alvo, Protocol):
    @property
    def n(self) -> int: ...


@dataclass(frozen=True, slots=True)
class MinimoDeValores:
    minimo: int

    def __call__(self, alvo: AlvoContado) -> str | None:
        return textos.poucos_valores(self.minimo, alvo.n) if alvo.n < self.minimo else None


def valores_variam(alvo: AlvoColuna) -> str | None:
    """A coluna precisa ter valores diferentes entre si (depois do mínimo de valores)."""
    return textos.VALORES_IGUAIS if np.ptp(alvo.valores) == 0 else None


@dataclass(frozen=True, slots=True)
class DigitoFinalTestavel:
    """n mínimo, último dígito variável e valores que variam o bastante (R4, R9; D119)."""

    minimo: int

    def __call__(self, alvo: AlvoColuna) -> str | None:
        return digitos.motivo_digito_final(alvo.valores, self.minimo)


class AlvoSemZeros(Alvo, Protocol):
    @property
    def zeros(self) -> int: ...


@dataclass(frozen=True, slots=True)
class ForaOsZeros[A: AlvoSemZeros]:
    """O motivo do requisito termina em ", fora os zeros" quando eles saíram do alvo (D134)."""

    requisito: Requisito[A]

    def __call__(self, alvo: A) -> str | None:
        motivo = self.requisito(alvo)
        return textos.fora_os_zeros(motivo) if motivo and alvo.zeros else motivo


@dataclass(frozen=True, slots=True)
class Todos[A]:
    """Os requisitos em ordem; vale o motivo do primeiro que falhar."""

    requisitos: tuple[Requisito[A], ...]

    def __call__(self, alvo: A) -> str | None:
        return next((m for requisito in self.requisitos if (m := requisito(alvo))), None)


# Aviso --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConteudoAviso:
    """O que cada regra decide no aviso; código e nome vêm da regra."""

    severidade: Severidade
    colunas: tuple[str, ...]
    textos: TextosAviso
    exemplo: ExemploAviso | None
    detalhes: DetalhesAviso
    grafico: Grafico | None = None


def conteudo_da_coluna(
    alvo: AlvoColuna,
    escrito: TextosAviso,
    detalhes: DetalhesAviso,
    marcas: np.ndarray,
    severidade: Severidade = Severidade.ATENCAO,
) -> ConteudoAviso:
    """Aviso de uma coluna com o exemplo no trecho onde as marcas se concentram."""
    exemplo = exemplo_do_trecho(alvo.linhas, alvo.valores, marcas)
    return ConteudoAviso(severidade, (alvo.nome,), escrito, exemplo, detalhes)


@dataclass(frozen=True, slots=True)
class ResultadoRegra:
    avisos: tuple[Aviso, ...]
    nao_aplicadas: tuple[RegraNaoAplicada, ...]
    verificada: bool
    """A regra se aplicou a pelo menos um alvo."""


class Regra(Protocol):
    """Contrato que o registro e o serviço usam (spec 12)."""

    codigo: str
    nome: str

    def executar(self, tabela: TabelaDetector) -> ResultadoRegra: ...


def executar_em_partes(partes: Sequence[Regra], tabela: TabelaDetector) -> ResultadoRegra:
    """Uma regra feita de partes com alvos diferentes (mesmo código e nome, ex.: R6).

    O motivo repetido por todas as partes (ex.: "sem coluna de data") aparece uma vez só.
    """
    resultados = [parte.executar(tabela) for parte in partes]
    return ResultadoRegra(
        avisos=tuple(aviso for r in resultados for aviso in r.avisos),
        nao_aplicadas=tuple(dict.fromkeys(item for r in resultados for item in r.nao_aplicadas)),
        verificada=any(r.verificada for r in resultados),
    )


@dataclass(frozen=True, slots=True)
class _Exame:
    aviso: Aviso | None = None
    nao_aplicadas: tuple[RegraNaoAplicada, ...] = ()
    aplicavel: bool = True


class RegraBase[A: Alvo, M](ABC):
    """Fluxo comum às regras; cada subclasse define código, nome, seletor, requisito e passos."""

    codigo: str
    nome: str
    seletor: SeletorAlvos[A]
    requisito: Requisito[A]

    def executar(self, tabela: TabelaDetector) -> ResultadoRegra:
        """Examina cada alvo e junta avisos e regras não aplicadas."""
        alvos = self.seletor(tabela)
        if not alvos:
            sem_alvos = self.nao_aplicada(None, self.seletor.motivo_sem_alvos)
            return ResultadoRegra((), (sem_alvos,), verificada=False)
        exames = [self._examinar(alvo) for alvo in alvos]
        return ResultadoRegra(
            avisos=tuple(exame.aviso for exame in exames if exame.aviso is not None),
            nao_aplicadas=tuple(item for exame in exames for item in exame.nao_aplicadas),
            verificada=any(exame.aplicavel for exame in exames),
        )

    def _examinar(self, alvo: A) -> _Exame:
        motivo = self.requisito(alvo)
        if motivo is not None:
            return _Exame(nao_aplicadas=(self.nao_aplicada(alvo.rotulo, motivo),), aplicavel=False)
        medicao = self.medir(alvo)
        aviso = self._aviso(self.conteudo_aviso(alvo, medicao)) if self.dispara(medicao) else None
        return _Exame(aviso)

    def _aviso(self, conteudo: ConteudoAviso) -> Aviso:
        escrito = conteudo.textos
        return Aviso(
            regra=self.codigo,
            nome_regra=self.nome,
            severidade=conteudo.severidade,
            colunas=conteudo.colunas,
            titulo=escrito.titulo,
            resumo=escrito.resumo,
            por_que=escrito.por_que,
            exemplo=conteudo.exemplo,
            pode_ser_normal=escrito.pode_ser_normal,
            o_que_fazer=escrito.o_que_fazer,
            detalhes=conteudo.detalhes,
            grafico=conteudo.grafico,
        )

    def nao_aplicada(
        self, rotulo: str | None, motivo: str, frase: str | None = None
    ) -> RegraNaoAplicada:
        """Regra não verificada num alvo; a frase padrão é a da spec 16."""
        texto = frase or textos.frase_nao_aplicada(self.nome, rotulo, motivo)
        return RegraNaoAplicada(self.codigo, self.nome, rotulo, motivo, texto)

    @abstractmethod
    def medir(self, alvo: A) -> M:
        """Calcula a medida da regra no alvo."""

    @abstractmethod
    def dispara(self, medicao: M) -> bool:
        """A medida passa do limiar da spec 12?"""

    @abstractmethod
    def conteudo_aviso(self, alvo: A, medicao: M) -> ConteudoAviso:
        """Severidade, colunas, textos, exemplo e detalhes do aviso."""
