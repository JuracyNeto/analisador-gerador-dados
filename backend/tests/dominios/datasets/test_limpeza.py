import math
from datetime import datetime

import pandas as pd
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.classificacao import Limiares, classificar_tabela
from app.dominios.datasets.diagnostico import Limites
from app.dominios.datasets.limpeza import AcaoLimpeza, ResultadoAcoes, aplicar_acoes

QUANDO = datetime(2026, 10, 3, 10, 0)


def _dados() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "sexo": ["F", "M", "F", "F", "M", "F"],
            "cidade": ["Goiânia", "Goiania", "Goiânia", "Goiânia", None, "Goiânia"],
            "idade": [30.0, None, 30.0, 30.0, 40.0, 230.0],
            "nota": ["7", "8", "7", "7", "doze", "9"],
        },
        index=pd.RangeIndex(1, 7),
    )


def _aplicar(*acoes: AcaoLimpeza, dados: pd.DataFrame | None = None) -> ResultadoAcoes:
    tabela = _dados() if dados is None else dados
    tipos = classificar_tabela(tabela, ".", Limiares(numerico=0.8))
    return aplicar_acoes(tabela, tipos, ".", list(acoes), QUANDO)


def test_remover_duplicados_mantem_a_primeira() -> None:
    resultado = _aplicar(AcaoLimpeza("duplicados", "remover"))

    assert resultado.dados.index.tolist() == [1, 2, 5, 6]
    [entrada] = resultado.log
    assert entrada.frase == "Removemos 2 linhas duplicadas."
    assert entrada.linhas_afetadas == (3, 4)
    assert (entrada.antes_exemplo, entrada.depois_exemplo) == ("6 linhas", "4 linhas")
    assert entrada.quando == QUANDO


def test_preencher_com_a_mediana() -> None:
    resultado = _aplicar(AcaoLimpeza("faltantes", "preencher_mediana", "idade"))

    assert resultado.dados.loc[2, "idade"] == 30.0
    assert resultado.log[0].frase == "Preenchemos 1 valor faltante de idade com a mediana (30)."


def test_preencher_com_a_media_e_com_a_moda() -> None:
    resultado = _aplicar(
        AcaoLimpeza("faltantes", "preencher_media", "idade"),
        AcaoLimpeza("faltantes", "preencher_moda", "cidade"),
    )

    assert resultado.dados.loc[2, "idade"] == pytest.approx(72.0)
    assert resultado.dados.loc[5, "cidade"] == "Goiânia"


def test_preencher_com_valor_informado() -> None:
    resultado = _aplicar(AcaoLimpeza("faltantes", "preencher_valor", "cidade", valor="Trindade"))

    assert resultado.dados.loc[5, "cidade"] == "Trindade"
    assert resultado.log[0].frase == "Preenchemos 1 valor faltante de cidade com o valor Trindade."


def test_media_nao_serve_para_texto() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        _aplicar(AcaoLimpeza("faltantes", "preencher_media", "cidade"))

    assert erro.value.codigo == "ACAO_INCOMPATIVEL"


def test_valor_de_coluna_numerica_precisa_ser_numero() -> None:
    with pytest.raises(EntradaInvalida):
        _aplicar(AcaoLimpeza("faltantes", "preencher_valor", "idade", valor="muitos"))


def test_remover_linhas_sem_valor() -> None:
    resultado = _aplicar(AcaoLimpeza("faltantes", "remover_linhas", "idade"))

    assert 2 not in resultado.dados.index
    assert resultado.log[0].frase == "Removemos 1 linha sem valor em idade."


def test_fora_de_faixa_limitar_marcar_e_remover() -> None:
    limites = Limites(min=1, max=110)

    limitar = _aplicar(AcaoLimpeza("fora_de_faixa", "limitar", "idade", limites=limites))
    marcar = _aplicar(AcaoLimpeza("fora_de_faixa", "marcar_faltante", "idade", limites=limites))
    remover = _aplicar(AcaoLimpeza("fora_de_faixa", "remover_linhas", "idade", limites=limites))

    assert limitar.dados.loc[6, "idade"] == 110
    assert limitar.log[0].frase == "Limitamos 1 valor de idade à faixa de 1 a 110."
    assert (limitar.log[0].antes_exemplo, limitar.log[0].depois_exemplo) == ("230", "110")
    assert math.isnan(marcar.dados.loc[6, "idade"])
    assert 6 not in remover.dados.index


def test_unificar_grafias() -> None:
    resultado = _aplicar(AcaoLimpeza("inconsistencia", "unificar", "cidade"))

    assert resultado.dados["cidade"].tolist()[:2] == ["Goiânia", "Goiânia"]
    assert resultado.log[0].frase == "Unificamos 1 grafia de cidade."
    assert resultado.log[0].antes_exemplo == "Goiania"


def test_unificar_so_o_grupo_escolhido() -> None:
    resultado = _aplicar(AcaoLimpeza("inconsistencia", "unificar", "cidade", grupo="Outro"))

    assert resultado.log == ()


def test_tipo_misto_vira_faltante_e_coluna_vira_numero() -> None:
    resultado = _aplicar(AcaoLimpeza("tipo_misto", "marcar_faltante", "nota"))

    assert pd.api.types.is_numeric_dtype(resultado.dados["nota"])
    assert math.isnan(resultado.dados.loc[5, "nota"])
    assert resultado.log[0].frase == "Marcamos 1 texto de nota como faltantes."


def test_preencher_coluna_numerica_que_ainda_tem_texto_mantem_o_formato() -> None:
    # "doze" foi mantido (tipo misto): a coluna guarda texto e o valor entra como texto.
    dados = _dados().assign(nota=["7", None, "8", "6", "doze", "9"])

    resultado = _aplicar(AcaoLimpeza("faltantes", "preencher_mediana", "nota"), dados=dados)

    assert resultado.dados.loc[2, "nota"] == "7.5"


def test_ordem_da_spec_inconsistencia_antes_de_duplicados() -> None:
    # O log segue a ordem da spec 03, não a ordem do pedido.
    resultado = _aplicar(
        AcaoLimpeza("duplicados", "remover"),
        AcaoLimpeza("inconsistencia", "unificar", "cidade"),
    )

    assert [e.problema for e in resultado.log] == ["inconsistencia", "duplicados"]


def test_manter_nao_gera_log() -> None:
    assert _aplicar(AcaoLimpeza("faltantes", "manter", "idade")).log == ()


def test_combinacao_desconhecida_e_recusada_antes_de_mudar_qualquer_coisa() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        _aplicar(AcaoLimpeza("duplicados", "remover"), AcaoLimpeza("duplicados", "limitar"))

    assert erro.value.codigo == "ACAO_INCOMPATIVEL"


def test_coluna_inexistente() -> None:
    with pytest.raises(EntradaInvalida):
        _aplicar(AcaoLimpeza("faltantes", "remover_linhas", "altura"))


def test_colunas_alteradas() -> None:
    so_cidade = _aplicar(AcaoLimpeza("faltantes", "preencher_moda", "cidade"))
    removendo = _aplicar(AcaoLimpeza("duplicados", "remover"))

    assert so_cidade.colunas_alteradas == frozenset({"cidade"})
    assert removendo.colunas_alteradas == frozenset({"id", "sexo", "cidade", "idade", "nota"})
