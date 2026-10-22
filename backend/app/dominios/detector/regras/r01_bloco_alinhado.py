"""R1 — Bloco alinhado: trecho com média e DP quase iguais aos do restante (spec 12, D122, D142).

Dois tipos de trecho, cada um contra o restante das linhas (fora ele): as janelas de k linhas
seguidas e o fim da coluna, de 10 a n/2 linhas (D148: dados anexados, de qualquer tamanho). O
candidato de cada tipo é o mais parecido com o restante; como é o melhor de centenas, a
referência é o melhor trecho do mesmo tipo em cada embaralhamento da coluna (1.000, semente
fixa): só um bloco mais alinhado do que o acaso consegue vira alerta. Comparar com o restante, e
não com o conjunto todo, é o que pega um bloco gerado com a média e o DP da coluna e anexado a
ela: ele bate exatamente com o restante, mas fica a ~1/(2n) do conjunto (o DP do conjunto cai ao
anexar), onde os embaralhamentos também chegam.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np

from app.compartilhado.tipos import Severidade
from app.dominios.detector import blocos, textos_blocos
from app.dominios.detector.exemplos import exemplo_do_bloco
from app.dominios.detector.regras import base
from app.dominios.detector.resultados import ExemploAviso, GraficoBlocos

MINIMO_VALORES = 60
MENOR_BLOCO = 10
PARTES_DO_TAMANHO = 20
"""k = max(10, ⌊n/20⌋)."""
LIMIAR_DISTANCIA = 0.01
EMBARALHAMENTOS = 1_000
SEMENTE = 2026
EMPATE = 1e-9
"""Distâncias (em DP) que diferem menos que isso empatam com a candidata (D142).

As somas acumuladas arredondam diferente conforme a posição da janela (~10⁻¹⁶): com poucos
valores distintos, janelas com os mesmos valores da candidata ficavam "um pouco mais longe".
"""
ALGARISMOS_MEDIDAS = 10
"""Média e DP guardados sem o ruído das contas: a mesma média no bloco e no restante sai igual."""

type Medidor = Callable[[np.ndarray], np.ndarray]
"""max(dᵤ, dₛ) de cada trecho de um tipo, em cada linha da matriz (um embaralhamento por linha)."""


@dataclass(frozen=True, slots=True)
class MedicaoBloco:
    """O trecho mais parecido com o restante e a chance de achar um assim ao acaso."""

    k: int
    """Linhas de cada janela (e de cada bloco da figura)."""
    inicio: int
    tamanho: int
    """Linhas do trecho: k numa janela; de 10 a n/2 no fim da coluna."""
    geral: tuple[float, float]
    """(média, DP) do conjunto (figura)."""
    bloco: tuple[float, float]
    """(média, DP) do trecho."""
    resto: tuple[float, float]
    """(média, DP) das linhas fora do trecho."""
    proporcao: float | None
    """Embaralhamentos com um trecho tão parecido; None se o trecho nem passa do limiar."""

    @property
    def distancias(self) -> tuple[float, float]:
        """(dᵤ, dₛ) em desvios padrão do restante."""
        media, desvio = self.resto
        return abs(self.bloco[0] - media) / desvio, abs(self.bloco[1] - desvio) / desvio

    @property
    def posicoes(self) -> slice:
        return slice(self.inicio, self.inicio + self.tamanho)


@dataclass(frozen=True, slots=True)
class _Candidato:
    inicio: int
    tamanho: int
    distancia: float
    proporcao: float | None

    @property
    def prioridade(self) -> tuple[float, float]:
        """O menos provável ao acaso; sem simulação, o mais perto do restante."""
        return (math.inf if self.proporcao is None else self.proporcao, self.distancia)


def tamanho_do_bloco(n: int) -> int:
    return max(MENOR_BLOCO, n // PARTES_DO_TAMANHO)


def maior_fim(n: int) -> int:
    """O fim vai até metade da coluna: além disso, o bloco seria o próprio resto."""
    return n // 2


def afastamentos_do_fim(matriz: np.ndarray) -> np.ndarray:
    """max(dᵤ, dₛ) dos últimos 10 a n/2 valores de cada linha, nessa ordem de tamanho."""
    return blocos.afastamentos_do_fim(matriz, MENOR_BLOCO, maior_fim(matriz.shape[1]))


def proporcao_ao_acaso(valores: np.ndarray, medir: Medidor, alvo: float) -> float:
    """Fração dos embaralhamentos cujo melhor trecho (do mesmo tipo) fica a até `alvo`.

    Empates (diferença < `EMPATE`) contam como tão parecidos. Para assim que 1% dos 1.000
    embaralhamentos já foi atingido: a regra não dispara.
    """
    rng = np.random.default_rng(SEMENTE)
    limite = round(base.LIMIAR_P * EMBARALHAMENTOS)
    tao_parecidos = feitos = 0
    for lote in blocos.embaralhados(valores, EMBARALHAMENTOS, rng):
        melhores = medir(lote).min(axis=1)
        tao_parecidos += int(np.count_nonzero(melhores <= alvo + EMPATE))
        feitos += len(lote)
        if tao_parecidos >= limite:
            break
    return tao_parecidos / feitos


def _candidato(
    valores: np.ndarray, medir: Medidor, trecho: Callable[[int], tuple[int, int]]
) -> _Candidato:
    distancias = medir(valores[np.newaxis, :])[0]
    indice = int(np.argmin(distancias))
    melhor = float(distancias[indice])
    proporcao = proporcao_ao_acaso(valores, medir, melhor) if melhor < LIMIAR_DISTANCIA else None
    return _Candidato(*trecho(indice), melhor, proporcao)


def melhor_trecho(valores: np.ndarray) -> tuple[int, _Candidato]:
    """(k, candidato): a melhor janela de k linhas ou o melhor fim, o menos provável ao acaso."""
    n, k = len(valores), tamanho_do_bloco(len(valores))
    janela = _candidato(valores, lambda m: blocos.afastamentos_do_resto(m, k), lambda i: (i, k))
    fim = _candidato(valores, afastamentos_do_fim, lambda i: (n - MENOR_BLOCO - i, MENOR_BLOCO + i))
    return k, min((janela, fim), key=lambda candidato: candidato.prioridade)


class RegraBlocoAlinhado(base.RegraBase[base.AlvoColuna, MedicaoBloco]):
    """dᵤ e dₛ < 0,01 contra o restante e em menos de 1% dos embaralhamentos → alta."""

    codigo = "R1"
    nome = "Bloco alinhado"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.Todos((base.MinimoDeValores(MINIMO_VALORES), base.valores_variam))

    def medir(self, alvo: base.AlvoColuna) -> MedicaoBloco:
        valores = alvo.valores
        k, candidato = melhor_trecho(valores)
        trecho = np.arange(candidato.inicio, candidato.inicio + candidato.tamanho)
        return MedicaoBloco(
            k=k,
            inicio=candidato.inicio,
            tamanho=candidato.tamanho,
            geral=_media_e_desvio(valores),
            bloco=_media_e_desvio(valores[trecho]),
            resto=_media_e_desvio(np.delete(valores, trecho)),
            proporcao=candidato.proporcao,
        )

    def dispara(self, medicao: MedicaoBloco) -> bool:
        return medicao.proporcao is not None and medicao.proporcao < base.LIMIAR_P

    def conteudo_aviso(self, alvo: base.AlvoColuna, medicao: MedicaoBloco) -> base.ConteudoAviso:
        linhas = alvo.linhas[medicao.posicoes]
        return base.ConteudoAviso(
            severidade=Severidade.ALTA,
            colunas=(alvo.nome,),
            textos=textos_blocos.r01_textos(
                alvo.nome,
                medicao.tamanho,
                (int(linhas[0]), int(linhas[-1])),
                max(medicao.distancias),
            ),
            exemplo=_exemplo(alvo, medicao),
            detalhes=textos_blocos.r01_detalhes(
                (medicao.k, MENOR_BLOCO, maior_fim(alvo.n)),
                medicao.distancias,
                EMBARALHAMENTOS,
                medicao.proporcao or 0.0,
            ),
            grafico=_grafico(alvo, medicao),
        )


def _sem_ruido(medida: float) -> float:
    """1,70150000000001 e 1,70149999999999 viram o mesmo número (e o mesmo texto)."""
    return float(f"{medida:.{ALGARISMOS_MEDIDAS}g}")


def _media_e_desvio(valores: np.ndarray) -> tuple[float, float]:
    return _sem_ruido(float(valores.mean())), _sem_ruido(float(valores.std(ddof=1)))


def _exemplo(alvo: base.AlvoColuna, medicao: MedicaoBloco) -> ExemploAviso:
    """O bloco inteiro (até 194 linhas, D172), com a média e o DP dele e os do restante."""
    linhas = alvo.linhas[medicao.posicoes]
    exemplo = exemplo_do_bloco(linhas, alvo.valores[medicao.posicoes])
    texto = textos_blocos.r01_texto_exemplo(
        (int(linhas[0]), int(linhas[-1])), medicao.bloco, medicao.resto
    )
    return replace(exemplo, texto=texto)


def _grafico(alvo: base.AlvoColuna, medicao: MedicaoBloco) -> GraficoBlocos:
    """Média de cada bloco de k linhas seguidas (sem sobrepor) e o bloco alinhado (D123)."""
    k = medicao.k
    usados = alvo.n // k * k
    medias = alvo.valores[:usados].reshape(-1, k).mean(axis=1)
    linhas = alvo.linhas[:usados].reshape(-1, k)
    alinhadas = alvo.linhas[medicao.posicoes]
    return GraficoBlocos(
        coluna=alvo.nome,
        tamanho=k,
        linhas_do_meio=tuple(float(meio) for meio in (linhas[:, 0] + linhas[:, -1]) / 2),
        medias=tuple(float(media) for media in medias),
        geral=medicao.geral,
        alinhado=(int(alinhadas[0]), int(alinhadas[-1]), medicao.bloco[0]),
    )
