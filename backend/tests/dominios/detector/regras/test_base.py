"""Ordem dos passos do Template Method com uma regra de teste."""

from dataclasses import dataclass, field

import pandas as pd

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.base import (
    AlvoColuna,
    ConteudoAviso,
    RegraBase,
    alvos_por_tipo,
)
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso
from app.dominios.detector.tabela import TabelaDetector
from tests.dominios.detector.apoio import tabela_de, tabela_numerica

MINIMO = 3
LIMITE = 10.0


@dataclass
class RegraDeTeste(RegraBase[AlvoColuna, float]):
    """Dispara quando a média passa de 10; precisa de 3 valores."""

    codigo = "R0"
    nome = "Regra de teste"
    motivo_sem_alvos = "o arquivo não tem colunas numéricas"
    medidas: list[str] = field(default_factory=list)

    def alvos(self, tabela: TabelaDetector) -> tuple[AlvoColuna, ...]:
        return alvos_por_tipo(tabela, {TipoVariavel.CONTINUA})

    def motivo_nao_aplicavel(self, alvo: AlvoColuna) -> str | None:
        return "poucos valores" if alvo.n < MINIMO else None

    def medir(self, alvo: AlvoColuna) -> float:
        self.medidas.append(alvo.nome)
        return float(alvo.valores.mean())

    def dispara(self, medicao: float) -> bool:
        return medicao > LIMITE

    def conteudo_aviso(self, alvo: AlvoColuna, medicao: float) -> ConteudoAviso:
        textos = TextosAviso(f"Média alta em {alvo.nome}", f"{medicao}", "a", "…b", "c")
        return ConteudoAviso(
            Severidade.INFO, (alvo.nome,), textos, None, DetalhesAviso("m", "v", "l")
        )


def test_regra_que_dispara_monta_o_aviso_com_codigo_e_nome() -> None:
    resultado = RegraDeTeste().executar(tabela_numerica([20, 30, 40]))

    assert resultado.verificada
    assert resultado.nao_aplicadas == ()
    (aviso,) = resultado.avisos
    assert (aviso.regra, aviso.nome_regra) == ("R0", "Regra de teste")
    assert aviso.titulo == "Média alta em x"
    assert aviso.colunas == ("x",)
    assert aviso.severidade == Severidade.INFO


def test_regra_que_nao_dispara_nao_gera_aviso() -> None:
    resultado = RegraDeTeste().executar(tabela_numerica([1, 2, 3]))

    assert resultado.avisos == ()
    assert resultado.verificada


def test_alvo_nao_aplicavel_nao_e_medido() -> None:
    regra = RegraDeTeste()
    tabela = tabela_de(
        pd.DataFrame({"a": [50.0, None, None], "b": [20.0, 30.0, 40.0]}),
        {"a": TipoVariavel.CONTINUA, "b": TipoVariavel.CONTINUA},
    )

    resultado = regra.executar(tabela)

    assert regra.medidas == ["b"]
    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.coluna == "a"
    assert nao_aplicada.motivo == "poucos valores"
    assert nao_aplicada.frase == "Regra de teste não verificada em a: poucos valores."
    assert resultado.verificada


def test_sem_nenhum_alvo_aplicavel_a_regra_nao_e_verificada() -> None:
    resultado = RegraDeTeste().executar(tabela_numerica([1.0]))

    assert not resultado.verificada


def test_sem_alvos_a_regra_diz_o_motivo_sem_coluna() -> None:
    tabela = tabela_de(pd.DataFrame({"s": ["a", "b"]}), {"s": TipoVariavel.NOMINAL})

    resultado = RegraDeTeste().executar(tabela)

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.coluna is None
    assert (
        nao_aplicada.frase == "Regra de teste não verificada: o arquivo não tem colunas numéricas."
    )
    assert not resultado.verificada
