"""R2 — Correlação por blocos: r geral × r de 5 blocos seguidos e r sem cada bloco (spec 12).

As comparações são em módulo (D122): vale para correlações negativas, e um r geral mais fraco
que o dos blocos (valores digitados errado derrubam r) não vira alerta.
"""

from dataclasses import dataclass

import numpy as np

from app.compartilhado.tipos import Severidade
from app.dominios.detector import blocos, textos, textos_blocos
from app.dominios.detector.exemplos import exemplo_de_textos
from app.dominios.detector.regras import base
from app.dominios.detector.resultados import ExemploAviso

MINIMO_PARES = 60
LIMIAR = 0.3


def _somas(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """n, Σx, Σy, Σx², Σy² e Σxy: r de qualquer união de blocos sai das somas."""
    return np.array([len(x), x.sum(), y.sum(), (x * x).sum(), (y * y).sum(), (x * y).sum()])


def correlacao(somas: np.ndarray) -> float:
    """r = Sxy / √(Sxx · Syy), com Sxy = Σxy − ΣxΣy/n (e assim por diante)."""
    n, sx, sy, sxx, syy, sxy = somas
    return float((sxy - sx * sy / n) / np.sqrt((sxx - sx * sx / n) * (syy - sy * sy / n)))


@dataclass(frozen=True, slots=True)
class MedicaoBlocos:
    """r geral, r de cada bloco e r sem cada bloco."""

    r: float
    por_bloco: tuple[float, ...]
    sem_bloco: tuple[float, ...]
    partes: tuple[slice, ...]

    @property
    def acima_da_media(self) -> float:
        """|r| − |média dos r dos blocos|."""
        return abs(self.r) - abs(float(np.mean(self.por_bloco)))

    @property
    def efeitos(self) -> np.ndarray:
        """Quanto |r| cai quando cada bloco sai."""
        return np.asarray(abs(self.r) - np.abs(self.sem_bloco), dtype="float64")

    @property
    def destaque(self) -> int:
        """O bloco que mais muda a correlação."""
        return int(np.argmax(self.efeitos))

    @property
    def puxada_pela_media(self) -> bool:
        return self.acima_da_media > LIMIAR

    @property
    def puxada_por_bloco(self) -> bool:
        return float(self.efeitos.max()) > LIMIAR


def _pares_suficientes(alvo: base.AlvoPar) -> str | None:
    return textos_blocos.poucos_pares(MINIMO_PARES, alvo.n) if alvo.n < MINIMO_PARES else None


def _blocos_variam(alvo: base.AlvoPar) -> str | None:
    """r de um bloco não existe se X ou Y ficam constantes nele."""
    constantes = (
        np.ptp(alvo.valores_x[parte]) == 0 or np.ptp(alvo.valores_y[parte]) == 0
        for parte in blocos.dividir_em_blocos(alvo.n)
    )
    return textos_blocos.BLOCO_SEM_VARIACAO if any(constantes) else None


def _exemplo(alvo: base.AlvoPar, parte: slice) -> ExemploAviso:
    """As linhas do bloco, cada uma como "x · y"."""
    pares = zip(alvo.valores_x[parte], alvo.valores_y[parte], strict=True)
    valores = [f"{textos.valor(float(x))} · {textos.valor(float(y))}" for x, y in pares]
    return exemplo_de_textos(alvo.linhas[parte], valores)


class RegraCorrelacaoBlocos(base.RegraBase[base.AlvoPar, MedicaoBlocos]):
    """|r| − |média dos blocos| > 0,3 ou tirar um bloco baixa |r| em mais de 0,3 → alta.

    Numa série no tempo, os blocos são épocas diferentes: atenção (D137).
    """

    codigo = "R2"
    nome = "Correlação por blocos"
    seletor = base.NaLinhaDoTempo(base.PARES_NUMERICOS)
    requisito = base.Todos((_pares_suficientes, _blocos_variam))

    def medir(self, alvo: base.AlvoPar) -> MedicaoBlocos:
        # Centrar nas médias gerais evita perder precisão nas somas dos quadrados.
        x = alvo.valores_x - alvo.valores_x.mean()
        y = alvo.valores_y - alvo.valores_y.mean()
        partes = blocos.dividir_em_blocos(alvo.n)
        total = _somas(x, y)
        por_bloco = [_somas(x[parte], y[parte]) for parte in partes]
        return MedicaoBlocos(
            r=correlacao(total),
            por_bloco=tuple(correlacao(somas) for somas in por_bloco),
            sem_bloco=tuple(correlacao(total - somas) for somas in por_bloco),
            partes=partes,
        )

    def dispara(self, medicao: MedicaoBlocos) -> bool:
        return medicao.puxada_pela_media or medicao.puxada_por_bloco

    def conteudo_aviso(self, alvo: base.AlvoPar, medicao: MedicaoBlocos) -> base.ConteudoAviso:
        parte = medicao.partes[medicao.destaque]
        linhas = alvo.linhas[parte]
        sem = (int(linhas[0]), int(linhas[-1]), medicao.sem_bloco[medicao.destaque])
        media = float(np.mean(medicao.por_bloco))
        no_tempo = alvo.linha_do_tempo
        return base.ConteudoAviso(
            severidade=Severidade.ALTA if no_tempo is None else Severidade.ATENCAO,
            colunas=(alvo.x, alvo.y),
            textos=textos_blocos.r02_textos(
                (alvo.x, alvo.y),
                (medicao.r, media),
                None if medicao.puxada_pela_media else sem,
                no_tempo,
            ),
            exemplo=_exemplo(alvo, parte),
            detalhes=textos_blocos.r02_detalhes(medicao.r, medicao.por_bloco, sem),
        )
