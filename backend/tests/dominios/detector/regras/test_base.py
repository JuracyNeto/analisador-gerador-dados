"""Ordem dos passos do Template Method com uma regra de teste."""

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.base import (
    COLUNAS_CONTINUAS,
    COLUNAS_NUMERICAS,
    NUMERICAS_SEM_MUITOS_ZEROS,
    AlvoColuna,
    ConteudoAviso,
    ForaOsZeros,
    MinimoDeValores,
    RegraBase,
    Todos,
    muitos_zeros,
)
from app.dominios.detector.resultados import DetalhesAviso, TextosAviso
from tests.dominios.detector.apoio import tabela_de, tabela_numerica

MINIMO = 3
LIMITE = 10.0


@dataclass
class RegraDeTeste(RegraBase[AlvoColuna, float]):
    """Dispara quando a média passa de 10; precisa de 3 valores."""

    codigo = "R0"
    nome = "Regra de teste"
    seletor = COLUNAS_CONTINUAS
    requisito = MinimoDeValores(MINIMO)
    medidas: list[str] = field(default_factory=list)

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
    assert nao_aplicada.motivo == "precisa de 3 valores ou mais; a coluna tem 1"
    assert nao_aplicada.frase == (
        "Regra de teste não verificada em a: precisa de 3 valores ou mais; a coluna tem 1."
    )
    assert resultado.verificada


def test_sem_nenhum_alvo_aplicavel_a_regra_nao_e_verificada() -> None:
    resultado = RegraDeTeste().executar(tabela_numerica([1.0]))

    assert not resultado.verificada


def test_sem_alvos_a_regra_diz_o_motivo_sem_coluna() -> None:
    tabela = tabela_de(pd.DataFrame({"s": ["a", "b"]}), {"s": TipoVariavel.NOMINAL})

    resultado = RegraDeTeste().executar(tabela)

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.coluna is None
    assert nao_aplicada.frase == (
        "Regra de teste não verificada: o arquivo não tem colunas contínuas."
    )
    assert not resultado.verificada


def _sempre(motivo: str | None) -> Callable[[AlvoColuna], str | None]:
    return lambda _alvo: motivo


def test_todos_devolve_o_motivo_do_primeiro_requisito_que_falha() -> None:
    (alvo,) = COLUNAS_CONTINUAS(tabela_numerica([1.0, 2.0]))

    requisito = Todos((_sempre(None), _sempre("primeiro"), _sempre("segundo")))

    assert requisito(alvo) == "primeiro"
    assert Todos((_sempre(None),))(alvo) is None


@pytest.mark.parametrize(
    ("valores", "esperado"),
    [
        ([0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], True),
        ([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], False),
        ([0.0, 0.0, 0.0, -1.0, 2.0, 3.0], False),
        ([], False),
    ],
)
def test_muitos_zeros_e_um_quarto_ou_mais_sem_negativos(
    valores: list[float], esperado: bool
) -> None:
    """Com 25% de zeros o Q1 é zero; com negativos, zero é um valor como os outros (D143)."""
    assert muitos_zeros(np.array(valores)) is esperado


def test_sem_muitos_zeros_tira_os_zeros_so_das_colunas_com_muitos() -> None:
    dados = pd.DataFrame({"chuva": [0.0] * 6 + [1.0, 2.0], "altura": [0.0] + [1.7] * 7})
    tipos = {"chuva": TipoVariavel.CONTINUA, "altura": TipoVariavel.CONTINUA}

    chuva, altura = NUMERICAS_SEM_MUITOS_ZEROS(tabela_de(dados, tipos))

    assert chuva.valores.tolist() == [1.0, 2.0]
    assert chuva.linhas.tolist() == [7, 8]
    assert chuva.zeros == 6
    assert (altura.n, altura.zeros) == (8, 0)


def test_fora_os_zeros_completa_o_motivo_quando_os_zeros_sairam() -> None:
    requisito = ForaOsZeros(MinimoDeValores(10))
    (sem_os_zeros,) = NUMERICAS_SEM_MUITOS_ZEROS(tabela_numerica([0.0] * 6 + [1.0, 2.0]))
    (com_todos,) = COLUNAS_NUMERICAS(tabela_numerica([1.0, 2.0]))

    assert requisito(sem_os_zeros) == (
        "precisa de 10 valores ou mais; a coluna tem 2, fora os zeros"
    )
    assert requisito(com_todos) == "precisa de 10 valores ou mais; a coluna tem 2"
