import numpy as np
import pandas as pd

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r05_duplicatas import RegraDuplicatas
from app.dominios.detector.tabela import TabelaDetector
from tests.dominios.detector.apoio import tabela_de

TIPOS = {
    "id": TipoVariavel.IDENTIFICADOR,
    "peso": TipoVariavel.CONTINUA,
    "sexo": TipoVariavel.BINARIA,
}


def _tabela(peso: list[float], sexo: list[str] | None = None) -> TabelaDetector:
    sexo = sexo or ["F", "M"] * (len(peso) // 2)
    dados = pd.DataFrame({"id": range(1, len(peso) + 1), "peso": peso, "sexo": sexo})
    return tabela_de(dados, TIPOS)


def _pesos(n: int = 40) -> list[float]:
    return [50.0 + 0.7 * i for i in range(n)]


def test_tres_linhas_iguais_seguidas_disparam_suspeita_alta() -> None:
    peso, sexo = _pesos(), ["F", "M"] * 20
    for i in (11, 12, 13):
        peso[i], sexo[i] = peso[10], sexo[10]

    resultado = RegraDuplicatas().executar(_tabela(peso, sexo))

    (aviso,) = resultado.avisos
    assert aviso.regra == "R5"
    assert aviso.severidade == Severidade.ALTA
    assert aviso.colunas == ()
    assert aviso.titulo == "Linhas iguais em sequência"
    assert aviso.resumo == (
        "Encontramos 3 linhas iguais a outras do arquivo; as linhas 11 a 14 são iguais e seguidas."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (11, 12, 13, 14)
    assert aviso.exemplo.texto == "Linhas 11 a 14: 57.0 · F"


def test_duas_linhas_iguais_distantes_disparam_atencao() -> None:
    peso = _pesos()
    peso[30] = peso[4]

    (aviso,) = RegraDuplicatas().executar(_tabela(peso)).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Linhas repetidas no arquivo"
    assert aviso.resumo == "Encontramos 1 linha igual a outra do arquivo."
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (5, 31)


def test_linhas_quase_iguais_tambem_disparam() -> None:
    peso = _pesos()
    peso[30] = peso[4] + 0.001

    (aviso,) = RegraDuplicatas().executar(_tabela(peso)).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.resumo == "Encontramos 1 linha igual ou quase igual a outra do arquivo."
    assert aviso.exemplo is not None
    assert aviso.exemplo.texto == "Linhas 5 e 31 (quase iguais): 52.8 · F"


def test_sem_repeticoes_nao_dispara() -> None:
    resultado = RegraDuplicatas().executar(_tabela(_pesos()))

    assert resultado.avisos == ()
    assert resultado.nao_aplicadas == ()
    assert resultado.verificada


def test_acima_de_5000_linhas_so_verifica_as_identicas() -> None:
    peso = [10.0 + 0.01 * i for i in range(6000)]
    peso[100] = peso[50]
    peso[300] = peso[200] + 0.0001

    resultado = RegraDuplicatas().executar(_tabela(peso))

    (aviso,) = resultado.avisos
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (51, 101)
    (ressalva,) = resultado.nao_aplicadas
    assert ressalva.regra == "R5"
    assert ressalva.coluna is None
    assert ressalva.frase == (
        "Quase duplicatas não verificadas: o arquivo tem 6.000 linhas e o limite é 5.000."
    )
    assert resultado.verificada


def test_uma_coluna_so_nao_se_aplica() -> None:
    tabela = tabela_de(pd.DataFrame({"peso": np.arange(10.0)}), {"peso": TipoVariavel.CONTINUA})

    (nao_aplicada,) = RegraDuplicatas().executar(tabela).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 2 colunas ou mais (fora os identificadores)"
    assert nao_aplicada.frase == (
        "Duplicatas não verificada: precisa de 2 colunas ou mais (fora os identificadores)."
    )


def test_so_identificadores_nao_tem_o_que_comparar() -> None:
    tabela = tabela_de(pd.DataFrame({"id": [1, 2]}), {"id": TipoVariavel.IDENTIFICADOR})

    resultado = RegraDuplicatas().executar(tabela)

    (nao_aplicada,) = resultado.nao_aplicadas
    assert nao_aplicada.motivo == "o arquivo só tem identificadores"
    assert not resultado.verificada
