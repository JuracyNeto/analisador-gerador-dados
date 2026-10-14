"""R1 — Bloco alinhado: janela com média e DP quase iguais aos do conjunto (spec 12, D122).

A janela candidata é a mais parecida com o conjunto entre todas as de k linhas seguidas. Como
ela é a melhor de centenas, a referência é a melhor janela de cada embaralhamento da coluna
(1.000, semente fixa): só um bloco mais alinhado do que o acaso consegue vira alerta.
"""

from dataclasses import dataclass

import numpy as np

from app.compartilhado.tipos import Severidade
from app.dominios.detector import blocos, textos_blocos
from app.dominios.detector.exemplos import exemplo_de_valores
from app.dominios.detector.regras import base
from app.dominios.detector.resultados import ExemploAviso, GraficoBlocos

MINIMO_VALORES = 60
MENOR_BLOCO = 10
PARTES_DO_TAMANHO = 20
"""k = max(10, ⌊n/20⌋)."""
LIMIAR_DISTANCIA = 0.01
EMBARALHAMENTOS = 1_000
SEMENTE = 2026


@dataclass(frozen=True, slots=True)
class MedicaoBloco:
    """A janela mais parecida com o conjunto e a chance de achar uma assim ao acaso."""

    k: int
    inicio: int
    geral: tuple[float, float]
    """(média, DP) do conjunto."""
    bloco: tuple[float, float]
    """(média, DP) da janela."""
    proporcao: float | None
    """Embaralhamentos com uma janela tão parecida; None se a janela nem passa do limiar."""

    @property
    def distancias(self) -> tuple[float, float]:
        """(dᵤ, dₛ) em desvios padrão do conjunto."""
        media, desvio = self.geral
        return abs(self.bloco[0] - media) / desvio, abs(self.bloco[1] - desvio) / desvio

    @property
    def posicoes(self) -> slice:
        return slice(self.inicio, self.inicio + self.k)


def tamanho_do_bloco(n: int) -> int:
    return max(MENOR_BLOCO, n // PARTES_DO_TAMANHO)


def proporcao_ao_acaso(valores: np.ndarray, k: int, alvo: float) -> float:
    """Fração dos embaralhamentos cuja melhor janela fica a até `alvo` do conjunto.

    Para assim que 1% dos 1.000 embaralhamentos já foi atingido: a regra não dispara.
    """
    media, desvio = float(valores.mean()), float(valores.std(ddof=1))
    rng = np.random.default_rng(SEMENTE)
    limite = round(base.LIMIAR_P * EMBARALHAMENTOS)
    tao_parecidos = feitos = 0
    for lote in blocos.embaralhados(valores, EMBARALHAMENTOS, rng):
        tao_parecidos += int(
            np.count_nonzero(blocos.menor_afastamento(lote, k, media, desvio) <= alvo)
        )
        feitos += len(lote)
        if tao_parecidos >= limite:
            break
    return tao_parecidos / feitos


class RegraBlocoAlinhado(base.RegraBase[base.AlvoColuna, MedicaoBloco]):
    """dᵤ e dₛ < 0,01 na melhor janela e em menos de 1% dos embaralhamentos → alta."""

    codigo = "R1"
    nome = "Bloco alinhado"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.Todos((base.MinimoDeValores(MINIMO_VALORES), base.valores_variam))

    def medir(self, alvo: base.AlvoColuna) -> MedicaoBloco:
        valores = alvo.valores
        k = tamanho_do_bloco(alvo.n)
        geral = (float(valores.mean()), float(valores.std(ddof=1)))
        medias, desvios = blocos.janelas(valores, k)
        afastamentos = blocos.afastamento(medias, desvios, *geral)
        inicio = int(np.argmin(afastamentos))
        melhor = float(afastamentos[inicio])
        proporcao = proporcao_ao_acaso(valores, k, melhor) if melhor < LIMIAR_DISTANCIA else None
        bloco = (float(medias[inicio]), float(desvios[inicio]))
        return MedicaoBloco(k, inicio, geral, bloco, proporcao)

    def dispara(self, medicao: MedicaoBloco) -> bool:
        return medicao.proporcao is not None and medicao.proporcao < base.LIMIAR_P

    def conteudo_aviso(self, alvo: base.AlvoColuna, medicao: MedicaoBloco) -> base.ConteudoAviso:
        linhas = alvo.linhas[medicao.posicoes]
        return base.ConteudoAviso(
            severidade=Severidade.ALTA,
            colunas=(alvo.nome,),
            textos=textos_blocos.r01_textos(
                alvo.nome, medicao.k, (int(linhas[0]), int(linhas[-1])), max(medicao.distancias)
            ),
            exemplo=_exemplo(alvo, medicao),
            detalhes=textos_blocos.r01_detalhes(
                medicao.k, medicao.distancias, EMBARALHAMENTOS, medicao.proporcao or 0.0
            ),
            grafico=_grafico(alvo, medicao),
        )


def _exemplo(alvo: base.AlvoColuna, medicao: MedicaoBloco) -> ExemploAviso:
    """As linhas do bloco, com a média e o DP dele ao lado dos do conjunto."""
    exemplo = exemplo_de_valores(alvo.linhas[medicao.posicoes], alvo.valores[medicao.posicoes])
    texto = textos_blocos.r01_texto_exemplo(exemplo.linhas, medicao.bloco, medicao.geral)
    return ExemploAviso(exemplo.linhas, exemplo.valores, texto)


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
