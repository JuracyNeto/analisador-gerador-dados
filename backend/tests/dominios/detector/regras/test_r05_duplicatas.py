import numpy as np
import pandas as pd
import pytest

from app.compartilhado.tipos import Severidade, TipoVariavel
from app.dominios.detector.regras.r05_duplicatas import RegraDuplicatas
from app.dominios.detector.tabela import TabelaDetector
from tests.dominios.detector.apoio import tabela_de

TIPOS = {
    "id": TipoVariavel.IDENTIFICADOR,
    "peso": TipoVariavel.CONTINUA,
    "altura": TipoVariavel.CONTINUA,
    "sexo": TipoVariavel.BINARIA,
}
COMPARADAS = ["peso", "altura", "sexo"]


def _dados(n: int = 100) -> pd.DataFrame:
    """Linhas todas diferentes: pesos de 0,7 em 0,7 kg e alturas de 1,1 em 1,1 mm."""
    return pd.DataFrame(
        {
            "id": range(1, n + 1),
            "peso": [round(50.0 + 0.7 * i, 1) for i in range(n)],
            "altura": [round(1.5 + 0.0011 * i, 4) for i in range(n)],
            "sexo": ["F", "M"] * (n // 2),
        }
    )


def _copiar(dados: pd.DataFrame, de: int, *para: int) -> pd.DataFrame:
    """Repete a linha `de` (menos o id) nas posições `para`."""
    copia = dados.copy()
    copia.loc[list(para), COMPARADAS] = copia.loc[de, COMPARADAS].to_numpy()
    return copia


def _tabela(dados: pd.DataFrame) -> TabelaDetector:
    return tabela_de(dados, {nome: TIPOS[nome] for nome in dados.columns})


def test_tres_linhas_iguais_seguidas_disparam_suspeita_alta() -> None:
    (aviso,) = RegraDuplicatas().executar(_tabela(_copiar(_dados(), 10, 11, 12, 13))).avisos

    assert aviso.regra == "R5"
    assert aviso.severidade == Severidade.ALTA
    assert aviso.colunas == ()
    assert aviso.titulo == "Linhas iguais em sequência"
    assert aviso.resumo == (
        "Encontramos 3 linhas iguais a outras do arquivo; as linhas 11 a 14 são iguais e seguidas."
    )
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (11, 12, 13, 14)
    assert aviso.exemplo.texto == "Linhas 11 a 14: peso 57.0 · altura 1.511 · sexo F"
    assert aviso.detalhes.teste == "Poisson: pares de linhas iguais × acaso (densidade local)"


def test_duas_linhas_iguais_distantes_disparam_atencao() -> None:
    (aviso,) = RegraDuplicatas().executar(_tabela(_copiar(_dados(), 4, 30))).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.titulo == "Linhas repetidas no arquivo"
    assert aviso.resumo == "Encontramos 1 linha igual a outra do arquivo."
    assert aviso.exemplo is not None
    assert aviso.exemplo.linhas == (5, 31)
    assert aviso.detalhes.valor.startswith("1 cópia em 1 grupo · 1 par igual (o acaso daria 0,0")
    assert aviso.detalhes.p_valor is not None
    assert aviso.detalhes.p_valor < 0.01


def test_linhas_quase_iguais_tambem_disparam() -> None:
    dados = _copiar(_dados(), 4, 30)
    dados.loc[30, "peso"] += 0.001

    (aviso,) = RegraDuplicatas().executar(_tabela(dados)).avisos

    assert aviso.severidade == Severidade.ATENCAO
    assert aviso.resumo == "Encontramos 1 linha igual ou quase igual a outra do arquivo."
    assert aviso.exemplo is not None
    assert aviso.exemplo.texto == "Linhas 5 e 31 (quase iguais): peso 52.8 · altura 1.5044 · sexo F"
    assert aviso.detalhes.teste == "Poisson: pares quase iguais × acaso (densidade local)"
    assert aviso.detalhes.p_valor is not None
    assert aviso.detalhes.p_valor < 0.01


def test_linhas_parecidas_por_acaso_nao_disparam() -> None:
    """Duas colunas aleatórias: pares a distância < 0,01·√2 surgem sozinhos (n = 500)."""
    rng = np.random.default_rng(5)
    dados = pd.DataFrame(
        {
            "peso": np.round(rng.normal(70, 10, 500), 2),
            "altura": np.round(rng.normal(1.7, 0.09, 500), 2),
        }
    )
    tipos = {"peso": TipoVariavel.CONTINUA, "altura": TipoVariavel.CONTINUA}

    assert RegraDuplicatas().executar(tabela_de(dados, tipos)).avisos == ()


def test_copias_seguidas_aparecem_mesmo_com_muitas_iguais_por_acaso() -> None:
    """Altura em cm e peso em kg: centenas de pares iguais por acaso; 3 cópias seguidas não."""
    rng = np.random.default_rng(1)
    dados = pd.DataFrame(
        {
            "peso": np.round(rng.normal(70, 10, 1000)),
            "altura": np.round(rng.normal(1.7, 0.09, 1000), 2),
            "sexo": ["F"] * 1000,
        }
    )
    dados = _copiar(dados, 500, 501, 502, 503)

    (aviso,) = RegraDuplicatas().executar(_tabela(dados)).avisos

    assert aviso.severidade == Severidade.ALTA
    assert aviso.resumo.endswith("as linhas 501 a 504 são iguais e seguidas.")
    assert aviso.detalhes.teste == "Poisson: linhas iguais seguidas × acaso (ordem aleatória)"


def test_arquivo_de_uma_linha_nao_se_aplica() -> None:
    (nao_aplicada,) = RegraDuplicatas().executar(_tabela(_dados(2).iloc[:1])).nao_aplicadas

    assert nao_aplicada.motivo == "precisa de 2 linhas ou mais; o arquivo tem 1"


def test_sem_repeticoes_nao_dispara() -> None:
    resultado = RegraDuplicatas().executar(_tabela(_dados()))

    assert resultado.avisos == ()
    assert resultado.nao_aplicadas == ()
    assert resultado.verificada


def test_acima_de_5000_linhas_so_verifica_as_identicas() -> None:
    dados = _copiar(_copiar(_dados(6000), 50, 100), 200, 300)
    dados.loc[300, "peso"] += 0.0001

    resultado = RegraDuplicatas().executar(_tabela(dados))

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


def test_linhas_sem_nenhuma_medida_nao_contam_como_iguais() -> None:
    dados = _dados()
    dados.loc[20:30, ["peso", "altura"]] = np.nan

    assert RegraDuplicatas().executar(_tabela(dados)).avisos == ()


@pytest.mark.parametrize("semente", [2, 3])
def test_linhas_anexadas_com_uma_coluna_se_comparam_so_nela(semente: int) -> None:
    """ "Anexar ao arquivo atual" preenche só a coluna gerada (achado D-b do M4.3). Pesos com 1
    casa coincidem por acaso, e o acaso tem de sair dessa coluna só, não das 3 comparadas."""
    rng = np.random.default_rng(semente)
    anexadas = pd.DataFrame({"peso": np.round(rng.normal(70, 12, 30), 1)})

    tabela = _tabela(pd.concat([_dados(200), anexadas], ignore_index=True))

    assert RegraDuplicatas().executar(tabela).avisos == ()


def test_celulas_vazias_ao_acaso_nao_viram_duplicatas() -> None:
    """Com 30% das células vazias, linhas com uma ou duas colunas preenchidas coincidem nelas."""
    rng = np.random.default_rng(2)
    dados = pd.DataFrame({f"c{j}": np.round(rng.normal(50, 10, 300), 2) for j in range(4)})
    dados["g"] = rng.choice(["a", "b", "c"], 300)
    tipos = {f"c{j}": TipoVariavel.CONTINUA for j in range(4)} | {"g": TipoVariavel.NOMINAL}

    tabela = tabela_de(dados.mask(rng.random(dados.shape) < 0.3), tipos)

    assert RegraDuplicatas().executar(tabela).avisos == ()


def test_copias_com_celulas_vazias_continuam_disparando() -> None:
    dados = _dados()
    dados["altura"] = dados["altura"].astype("float64")
    dados.loc[10, "altura"] = np.nan

    (aviso,) = RegraDuplicatas().executar(_tabela(_copiar(dados, 10, 11, 12, 13))).avisos

    assert aviso.severidade == Severidade.ALTA
    assert aviso.exemplo is not None
    assert aviso.exemplo.texto == "Linhas 11 a 14: peso 57.0 · sexo F (altura vazia)"
