"""Regra base do detector (Template Method, D118).

`executar` pega os alvos do seletor e faz, para cada um: requisito (aplicável?) → medir →
dispara? → aviso. Seletor e requisito são objetos compostos (reaproveitados entre regras);
medir, dispara e o conteúdo do aviso são os passos de cada regra. Textos vêm de `textos.py`.
"""

from abc import ABC, abstractmethod
from collections.abc import Collection
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from app.compartilhado.tipos import TIPOS_NUMERICOS, Severidade, TipoVariavel
from app.dominios.detector import digitos, textos
from app.dominios.detector.exemplos import exemplo_do_trecho
from app.dominios.detector.resultados import (
    Aviso,
    DetalhesAviso,
    ExemploAviso,
    RegraNaoAplicada,
    TextosAviso,
)
from app.dominios.detector.tabela import TabelaDetector

LIMIAR_P = 0.01
"""Nível de significância das regras do detector (spec 12)."""


class Alvo(Protocol):
    """O que a regra examina: uma coluna, um par (M3.3) ou o arquivo todo."""

    @property
    def rotulo(self) -> str | None: ...


@dataclass(frozen=True, slots=True, eq=False)
class AlvoColuna:
    """Uma coluna numérica: números das linhas e valores válidos, na ordem do arquivo."""

    nome: str
    tipo: TipoVariavel
    linhas: np.ndarray
    valores: np.ndarray

    @property
    def rotulo(self) -> str:
        return self.nome

    @property
    def n(self) -> int:
        return len(self.valores)


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
            AlvoColuna(coluna.nome, coluna.tipo, *tabela.valores_validos(coluna))
            for coluna in tabela.do_tipo(self.tipos)
        )


COLUNAS_NUMERICAS = ColunasDoTipo(TIPOS_NUMERICOS, textos.SEM_NUMERICAS)
COLUNAS_CONTINUAS = ColunasDoTipo(frozenset({TipoVariavel.CONTINUA}), textos.SEM_CONTINUAS)


# Requisitos (passo "aplicável?") ------------------------------------------------------------


class Requisito[A](Protocol):
    """Por que a regra não se aplica ao alvo, ou None se ela se aplica."""

    def __call__(self, alvo: A) -> str | None: ...


@dataclass(frozen=True, slots=True)
class MinimoDeValores:
    minimo: int

    def __call__(self, alvo: AlvoColuna) -> str | None:
        return textos.poucos_valores(self.minimo, alvo.n) if alvo.n < self.minimo else None


@dataclass(frozen=True, slots=True)
class DigitoFinalTestavel:
    """n mínimo, último dígito variável e valores que variam o bastante (R4, R9; D119)."""

    minimo: int

    def __call__(self, alvo: AlvoColuna) -> str | None:
        return digitos.motivo_digito_final(alvo.valores, self.minimo)


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
