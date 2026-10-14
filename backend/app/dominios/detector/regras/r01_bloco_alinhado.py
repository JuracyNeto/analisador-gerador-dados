"""R1 — Bloco alinhado: janela com média e DP quase iguais aos do restante (spec 12, D122, D142).

A janela candidata é a mais parecida com o restante das linhas (fora ela) entre todas as de k
linhas seguidas. Como ela é a melhor de centenas, a referência é a melhor janela de cada
embaralhamento da coluna (1.000, semente fixa): só um bloco mais alinhado do que o acaso consegue
vira alerta. Comparar com o restante, e não com o conjunto todo, é o que pega um bloco gerado com
a média e o DP da coluna e anexado a ela: ele bate exatamente com o restante, mas fica a ~1/(2n)
do conjunto (o DP do conjunto cai ao anexar), onde os embaralhamentos também chegam.
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
ALGARISMOS_MEDIDAS = 10
"""Média e DP guardados sem o ruído das contas: a mesma média no bloco e no restante sai igual."""


@dataclass(frozen=True, slots=True)
class MedicaoBloco:
    """A janela mais parecida com o restante e a chance de achar uma assim ao acaso."""

    k: int
    inicio: int
    geral: tuple[float, float]
    """(média, DP) do conjunto (figura)."""
    bloco: tuple[float, float]
    """(média, DP) da janela."""
    resto: tuple[float, float]
    """(média, DP) das linhas fora da janela."""
    proporcao: float | None
    """Embaralhamentos com uma janela tão parecida; None se a janela nem passa do limiar."""

    @property
    def distancias(self) -> tuple[float, float]:
        """(dᵤ, dₛ) em desvios padrão do restante."""
        media, desvio = self.resto
        return abs(self.bloco[0] - media) / desvio, abs(self.bloco[1] - desvio) / desvio

    @property
    def posicoes(self) -> slice:
        return slice(self.inicio, self.inicio + self.k)


def tamanho_do_bloco(n: int) -> int:
    return max(MENOR_BLOCO, n // PARTES_DO_TAMANHO)


def proporcao_ao_acaso(valores: np.ndarray, k: int, alvo: float) -> float:
    """Fração dos embaralhamentos cuja melhor janela fica a até `alvo` do restante dela.

    Para assim que 1% dos 1.000 embaralhamentos já foi atingido: a regra não dispara.
    """
    rng = np.random.default_rng(SEMENTE)
    limite = round(base.LIMIAR_P * EMBARALHAMENTOS)
    tao_parecidos = feitos = 0
    for lote in blocos.embaralhados(valores, EMBARALHAMENTOS, rng):
        melhores = blocos.afastamentos_do_resto(lote, k).min(axis=1)
        tao_parecidos += int(np.count_nonzero(melhores <= alvo))
        feitos += len(lote)
        if tao_parecidos >= limite:
            break
    return tao_parecidos / feitos


class RegraBlocoAlinhado(base.RegraBase[base.AlvoColuna, MedicaoBloco]):
    """dᵤ e dₛ < 0,01 contra o restante e em menos de 1% dos embaralhamentos → alta."""

    codigo = "R1"
    nome = "Bloco alinhado"
    seletor = base.COLUNAS_NUMERICAS
    requisito = base.Todos((base.MinimoDeValores(MINIMO_VALORES), base.valores_variam))

    def medir(self, alvo: base.AlvoColuna) -> MedicaoBloco:
        valores = alvo.valores
        k = tamanho_do_bloco(alvo.n)
        afastamentos = blocos.afastamentos_do_resto(valores[np.newaxis, :], k)[0]
        inicio = int(np.argmin(afastamentos))
        melhor = float(afastamentos[inicio])
        proporcao = proporcao_ao_acaso(valores, k, melhor) if melhor < LIMIAR_DISTANCIA else None
        janela = np.arange(inicio, inicio + k)
        return MedicaoBloco(
            k=k,
            inicio=inicio,
            geral=_media_e_desvio(valores),
            bloco=_media_e_desvio(valores[janela]),
            resto=_media_e_desvio(np.delete(valores, janela)),
            proporcao=proporcao,
        )

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


def _sem_ruido(medida: float) -> float:
    """1,70150000000001 e 1,70149999999999 viram o mesmo número (e o mesmo texto)."""
    return float(f"{medida:.{ALGARISMOS_MEDIDAS}g}")


def _media_e_desvio(valores: np.ndarray) -> tuple[float, float]:
    return _sem_ruido(float(valores.mean())), _sem_ruido(float(valores.std(ddof=1)))


def _exemplo(alvo: base.AlvoColuna, medicao: MedicaoBloco) -> ExemploAviso:
    """Até 20 linhas do bloco; o texto cita o bloco inteiro, com a média e o DP do restante."""
    linhas = alvo.linhas[medicao.posicoes]
    exemplo = exemplo_de_valores(linhas, alvo.valores[medicao.posicoes])
    texto = textos_blocos.r01_texto_exemplo(
        (int(linhas[0]), int(linhas[-1])), medicao.bloco, medicao.resto
    )
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
