# M1.3 — Datasets: limpeza — plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, `docs/specs/03-limpeza.md` e os contratos em `docs/plans/2026-10-03-m1-visao-geral.md`.

**Objetivo:** diagnosticar faltantes, duplicados, valores fora de faixa, grafias diferentes e tipo misto sem alterar nada; aplicar as ações escolhidas sobre a versão `atual` na ordem da spec 03, registrar cada uma em frase; "Desfazer tudo"; reclassificar os tipos que mudaram.

**Arquitetura:** dois módulos puros no domínio `datasets`: `diagnostico.py` (só lê) e `limpeza.py` (tabela de despacho `(problema, acao) → manipulador`, cada manipulador devolve um efeito com as linhas afetadas e a frase). As frases ficam em `frases_limpeza.py`. A fachada `ServicoDatasets` ganha `diagnosticar`, `limpar` e `desfazer_limpeza`; o router ganha 3 rotas.

**Stack:** Python 3.12, pandas 3, FastAPI, Pydantic 2, pytest.

**Branch:** `feat/datasets-limpeza` (sai de `develop` **depois do merge do M1.2**) → PR para `develop`.

**Prazo sugerido:** 15/10/2026. **Depende de:** M1.2. Pode andar junto com o M1.4.

**Código validado:** rodado num rascunho sobre o código do M1.2 com ruff, mypy, complexipy, jscpd e pytest (212 testes, 99% de cobertura).

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Diagnóstico | `datasets/diagnostico.py`, `datasets/erros.py` |
| 2 | Frases do log e ações de limpeza | `datasets/frases_limpeza.py`, `datasets/limpeza.py` |
| 3 | Casos de uso no `ServicoDatasets` | `datasets/servico.py` |
| 4 | Schemas e rotas | `datasets/schemas.py`, `datasets/router.py` |
| 5 | Tipos do frontend, decisão D50, specs e CHANGELOG | `schema.d.ts`, `docs/**` |
| 6 | Verificação final, teste manual e PR | — |

Comandos em `backend/` com o venv ativo.

### Regras que o código implementa (spec 03 + decisões)
- **Duplicados** comparam todas as colunas **menos as `identificador`** (D50; no design 3a a linha 45 é "igual à 44, exceto id"). Mantém a primeira ocorrência.
- **Fora de faixa:** só colunas discretas/contínuas. Faixa padrão = cercas de Tukey `[Q1 − 1,5·IQR, Q3 + 1,5·IQR]`; o usuário pode informar `min` e/ou `max` (o lado não informado continua pelo IQR). `min ≥ max` → `LIMITES_INVALIDOS`.
- **Grafias diferentes:** só colunas categóricas de texto; agrupa por `normalizar_texto` e a grafia mais frequente é a preferida.
- **Tipo misto:** em colunas numéricas, os valores que não viram número.
- **Ordem de aplicação:** inconsistência → tipo misto → duplicados → fora de faixa → faltantes, qualquer que seja a ordem do pedido. `manter` não faz nada e não entra no log. Combinação desconhecida é recusada **antes** de mexer nos dados.
- **Preencher:** média e mediana só para numéricas; moda para qualquer tipo; valor informado (convertido para número em colunas numéricas). Se a coluna numérica ainda guarda texto (o usuário manteve o tipo misto), o valor entra como texto no formato do arquivo, para não misturar tipos.
- **Reclassificação:** depois da limpeza, as colunas que mudaram (todas, se alguma linha saiu) são reclassificadas; tipos `manual` são mantidos se continuarem válidos e só têm as contagens atualizadas.
- **Log:** `{problema, acao, coluna, linhas_afetadas, antes_exemplo, depois_exemplo, quando, frase}`, acumulado em `Dataset.log_limpeza` até o "Desfazer tudo".

---

### Tarefa 1: diagnóstico

**Arquivos:**
- Criar: `backend/app/dominios/datasets/diagnostico.py`
- Modificar: `backend/app/dominios/datasets/erros.py`
- Teste: `backend/tests/dominios/datasets/test_diagnostico.py`

**Passo 1: escrever os testes (falham)**
```python
import pandas as pd
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.classificacao import Limiares, classificar_tabela
from app.dominios.datasets.diagnostico import (
    Grafia,
    GrupoDuplicado,
    Limites,
    diagnosticar,
    faixa_da_coluna,
    faixa_iqr,
    grupos_de_grafias,
)
from app.dominios.datasets.modelos import TipoColuna

DADOS = pd.DataFrame(
    {
        "id": [1, 2, 3, 4, 5, 6, 7, 8],
        "cidade": [
            "Goiânia",
            "Goiania",
            "goiânia",
            "Anápolis",
            "Anapolis",
            None,
            "Goiânia",
            "Goiânia",
        ],
        "idade": [30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 230.0, 30.0],
        "nota": ["7", "8", "doze", "6", "7", "8", "9", "7"],
    },
    index=pd.RangeIndex(1, 9),
)


def _tipos(dados: pd.DataFrame) -> dict[str, TipoColuna]:
    return classificar_tabela(dados, ".", Limiares(numerico=0.8))


def test_faltantes_com_linhas_e_valores_sugeridos() -> None:
    diagnostico = diagnosticar(DADOS, _tipos(DADOS), ".", {})

    [cidade] = diagnostico.faltantes
    assert (cidade.coluna, cidade.n, cidade.linhas) == ("cidade", 1, (6,))
    assert cidade.sugeridos.moda == "Goiânia"
    assert cidade.sugeridos.media is None


def test_sugeridos_de_coluna_numerica() -> None:
    dados = pd.DataFrame({"peso": [10.0, 20.0, None, 30.0, 20.0]}, index=pd.RangeIndex(1, 6))

    [peso] = diagnosticar(dados, _tipos(dados), ".", {}).faltantes

    assert (peso.sugeridos.media, peso.sugeridos.mediana, peso.sugeridos.moda) == (20.0, 20.0, 20.0)


def test_duplicados_ignoram_identificador() -> None:
    dados = pd.DataFrame(
        {"id": [1, 2, 3, 4], "sexo": ["F", "M", "F", "F"], "peso": [58.2, 79.6, 58.2, 58.2]},
        index=pd.RangeIndex(1, 5),
    )

    diagnostico = diagnosticar(dados, _tipos(dados), ".", {})

    assert diagnostico.duplicados == (GrupoDuplicado(1, (3, 4)),)


def test_fora_de_faixa_pelo_iqr() -> None:
    [idade] = diagnosticar(DADOS, _tipos(DADOS), ".", {}).fora_de_faixa

    assert idade.origem == "iqr"
    assert [o.linha for o in idade.ocorrencias] == [7]
    assert idade.ocorrencias[0].valor == 230.0


def test_fora_de_faixa_pelos_limites_do_usuario() -> None:
    limites = {"idade": Limites(min=31, max=None)}

    [idade] = diagnosticar(DADOS, _tipos(DADOS), ".", limites).fora_de_faixa

    assert idade.origem == "usuario"
    assert idade.limite_inferior == 31
    assert [o.linha for o in idade.ocorrencias] == [1, 7, 8]


def test_limites_invertidos_sao_recusados() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        faixa_da_coluna(pd.Series([1.0, 2.0]), Limites(min=110, max=1))

    assert erro.value.codigo == "LIMITES_INVALIDOS"
    assert erro.value.mensagem == "O mínimo precisa ser menor que o máximo (1)."


def test_faixa_iqr_usa_as_cercas_de_tukey() -> None:
    assert faixa_iqr(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])) == (-1.0, 7.0)


def test_grupos_de_grafias_preferem_a_mais_frequente() -> None:
    serie = pd.Series(["Goiânia", "Goiania", "Goiânia", "goiânia", "Rio Verde"])

    [grupo] = grupos_de_grafias(serie)

    assert grupo.forma_preferida == "Goiânia"
    assert grupo.variacoes == (Grafia("Goiania", 1), Grafia("goiânia", 1))


def test_inconsistencias_por_coluna() -> None:
    [cidade] = diagnosticar(DADOS, _tipos(DADOS), ".", {}).inconsistencias

    assert cidade.coluna == "cidade"
    assert [g.forma_preferida for g in cidade.grupos] == ["Goiânia", "Anápolis"]


def test_tipo_misto_aponta_os_textos() -> None:
    [nota] = diagnosticar(DADOS, _tipos(DADOS), ".", {}).tipo_misto

    assert nota.coluna == "nota"
    assert [(o.linha, o.valor) for o in nota.ocorrencias] == [(3, "doze")]
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_diagnostico.py --no-cov` → FAIL (`ModuleNotFoundError`)

**Passo 3: erros novos** — em `app/dominios/datasets/erros.py`, acrescentar `from app.compartilhado.numeros import formatar_numero` aos imports e, no fim do arquivo:
```python
def limites_invalidos(maximo: float) -> EntradaInvalida:
    return EntradaInvalida(
        "LIMITES_INVALIDOS",
        f"O mínimo precisa ser menor que o máximo ({formatar_numero(maximo)}).",
        "Ajuste um dos dois.",
    )


def acao_incompativel(coluna: str | None, motivo: str) -> EntradaInvalida:
    alvo = f"a coluna {coluna}" if coluna else "este problema"
    return EntradaInvalida(
        "ACAO_INCOMPATIVEL", f"Esta ação não serve para {alvo}: {motivo}", "Escolha outra ação."
    )
```

**Passo 4: implementar `app/dominios/datasets/diagnostico.py`**
```python
"""Diagnóstico de problemas comuns, sem alterar os dados (spec 03)."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

import pandas as pd

from app.compartilhado.series import converter_para_numero
from app.compartilhado.textos import normalizar_texto
from app.compartilhado.tipos import TIPOS_CATEGORICOS, TIPOS_NUMERICOS, TipoVariavel
from app.dominios.datasets import erros
from app.dominios.datasets.modelos import Celula, TipoColuna
from app.dominios.datasets.tabela import celula

FATOR_IQR = 1.5
QUARTIS = (0.25, 0.75)


@dataclass(frozen=True, slots=True)
class Limites:
    """Faixa aceita para uma coluna numérica; None = sem limite daquele lado."""

    min: float | None = None
    max: float | None = None


@dataclass(frozen=True, slots=True)
class ValoresSugeridos:
    media: float | None
    mediana: float | None
    moda: Celula


@dataclass(frozen=True, slots=True)
class FaltantesColuna:
    coluna: str
    n: int
    linhas: tuple[int, ...]
    sugeridos: ValoresSugeridos


@dataclass(frozen=True, slots=True)
class GrupoDuplicado:
    linha_original: int
    copias: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Ocorrencia:
    linha: int
    valor: Celula


@dataclass(frozen=True, slots=True)
class ForaDeFaixaColuna:
    coluna: str
    limite_inferior: float
    limite_superior: float
    origem: Literal["iqr", "usuario"]
    ocorrencias: tuple[Ocorrencia, ...]


@dataclass(frozen=True, slots=True)
class Grafia:
    texto: str
    n: int


@dataclass(frozen=True, slots=True)
class GrupoGrafias:
    forma_preferida: str
    variacoes: tuple[Grafia, ...]


@dataclass(frozen=True, slots=True)
class InconsistenciaColuna:
    coluna: str
    grupos: tuple[GrupoGrafias, ...]


@dataclass(frozen=True, slots=True)
class TipoMistoColuna:
    coluna: str
    ocorrencias: tuple[Ocorrencia, ...]


@dataclass(frozen=True, slots=True)
class Diagnostico:
    n_linhas: int
    faltantes: tuple[FaltantesColuna, ...]
    duplicados: tuple[GrupoDuplicado, ...]
    fora_de_faixa: tuple[ForaDeFaixaColuna, ...]
    inconsistencias: tuple[InconsistenciaColuna, ...]
    tipo_misto: tuple[TipoMistoColuna, ...]


def _linhas(mascara: pd.Series) -> tuple[int, ...]:
    return tuple(int(i) for i in mascara[mascara].index.tolist())


def _ocorrencias(serie: pd.Series, mascara: pd.Series) -> tuple[Ocorrencia, ...]:
    marcados = serie[mascara]
    return tuple(
        Ocorrencia(int(linha), celula(valor))
        for linha, valor in zip(marcados.index.tolist(), marcados.tolist(), strict=True)
    )


def _sugeridos(serie: pd.Series, numeros: pd.Series | None) -> ValoresSugeridos:
    modas = serie.dropna().mode()
    moda = celula(modas.iloc[0]) if not modas.empty else None
    if numeros is None or numeros.dropna().empty:
        return ValoresSugeridos(None, None, moda)
    return ValoresSugeridos(float(numeros.mean()), float(numeros.median()), moda)


def faltantes(
    dados: pd.DataFrame, numericas: Mapping[str, pd.Series]
) -> tuple[FaltantesColuna, ...]:
    """Colunas com células vazias, as linhas afetadas e os valores sugeridos para preencher."""
    resultado = []
    for nome in dados.columns:
        vazias = dados[nome].isna()
        if vazias.any():
            sugeridos = _sugeridos(dados[nome], numericas.get(nome))
            resultado.append(FaltantesColuna(nome, int(vazias.sum()), _linhas(vazias), sugeridos))
    return tuple(resultado)


def colunas_comparaveis(tipos: Mapping[str, TipoColuna]) -> list[str]:
    """Colunas usadas para achar duplicados: todas menos identificadores (D50)."""
    return [nome for nome, tipo in tipos.items() if tipo.tipo != TipoVariavel.IDENTIFICADOR]


def duplicados(dados: pd.DataFrame, colunas: list[str]) -> tuple[GrupoDuplicado, ...]:
    """Linhas iguais à primeira ocorrência (keep="first") nas colunas comparáveis."""
    if not colunas:
        return ()
    grupos = dados.groupby(colunas, dropna=False, sort=False).indices
    repetidos = (sorted(dados.index[posicoes]) for posicoes in grupos.values() if len(posicoes) > 1)
    return tuple(
        GrupoDuplicado(int(linhas[0]), tuple(int(i) for i in linhas[1:]))
        for linhas in sorted(repetidos)
    )


def faixa_iqr(numeros: pd.Series) -> tuple[float, float]:
    """Cercas de Tukey: [Q1 − 1,5·IQR, Q3 + 1,5·IQR]."""
    q1, q3 = (float(q) for q in numeros.quantile(list(QUARTIS)))
    iqr = q3 - q1
    return q1 - FATOR_IQR * iqr, q3 + FATOR_IQR * iqr


def faixa_da_coluna(numeros: pd.Series, limites: Limites | None) -> tuple[float, float, bool]:
    """Faixa aceita: a do usuário onde houver limite, senão a do IQR."""
    inferior, superior = faixa_iqr(numeros)
    if limites is None:
        return inferior, superior, False
    if limites.min is not None and limites.max is not None and limites.min >= limites.max:
        raise erros.limites_invalidos(limites.max)
    inferior = limites.min if limites.min is not None else inferior
    superior = limites.max if limites.max is not None else superior
    return inferior, superior, True


def fora_de_faixa(
    dados: pd.DataFrame, numericas: Mapping[str, pd.Series], limites: Mapping[str, Limites]
) -> tuple[ForaDeFaixaColuna, ...]:
    """Valores numéricos fora da faixa aceita, por coluna."""
    resultado = []
    for nome, numeros in numericas.items():
        if numeros.dropna().empty:
            continue
        inferior, superior, do_usuario = faixa_da_coluna(numeros, limites.get(nome))
        fora = (numeros < inferior) | (numeros > superior)
        if fora.any():
            origem: Literal["iqr", "usuario"] = "usuario" if do_usuario else "iqr"
            ocorrencias = _ocorrencias(dados[nome], fora)
            resultado.append(ForaDeFaixaColuna(nome, inferior, superior, origem, ocorrencias))
    return tuple(resultado)


def grupos_de_grafias(serie: pd.Series) -> tuple[GrupoGrafias, ...]:
    """Grafias que viram o mesmo texto ao normalizar; a mais frequente é a preferida."""
    contagens = serie.dropna().astype(str).value_counts()
    por_forma: dict[str, list[Grafia]] = {}
    for texto, n in contagens.items():
        por_forma.setdefault(normalizar_texto(str(texto)), []).append(Grafia(str(texto), int(n)))
    return tuple(
        GrupoGrafias(grafias[0].texto, tuple(grafias[1:]))
        for grafias in por_forma.values()
        if len(grafias) > 1
    )


def inconsistencias(
    dados: pd.DataFrame, tipos: Mapping[str, TipoColuna], numericas: Mapping[str, pd.Series]
) -> tuple[InconsistenciaColuna, ...]:
    """Categorias de texto escritas de jeitos diferentes ("SP", "sp ", "Sp")."""
    resultado = []
    for nome, tipo in tipos.items():
        if tipo.tipo not in TIPOS_CATEGORICOS or nome in numericas:
            continue
        grupos = grupos_de_grafias(dados[nome])
        if grupos:
            resultado.append(InconsistenciaColuna(nome, grupos))
    return tuple(resultado)


def tipo_misto(
    dados: pd.DataFrame, numericas: Mapping[str, pd.Series]
) -> tuple[TipoMistoColuna, ...]:
    """Textos que não viram número em colunas numéricas (ex.: "doze")."""
    resultado = []
    for nome, numeros in numericas.items():
        textos = dados[nome].notna() & numeros.isna()
        if textos.any():
            resultado.append(TipoMistoColuna(nome, _ocorrencias(dados[nome], textos)))
    return tuple(resultado)


def series_numericas(
    dados: pd.DataFrame, tipos: Mapping[str, TipoColuna], decimal: str | None
) -> dict[str, pd.Series]:
    """Colunas discretas/contínuas convertidas para número (texto que não converte vira NaN)."""
    return {
        nome: converter_para_numero(dados[nome], decimal)
        for nome, tipo in tipos.items()
        if tipo.tipo in TIPOS_NUMERICOS
    }


def diagnosticar(
    dados: pd.DataFrame,
    tipos: Mapping[str, TipoColuna],
    decimal: str | None,
    limites: Mapping[str, Limites],
) -> Diagnostico:
    """Levanta faltantes, duplicados, fora de faixa, grafias diferentes e tipo misto."""
    numericas = series_numericas(dados, tipos, decimal)
    return Diagnostico(
        n_linhas=len(dados),
        faltantes=faltantes(dados, numericas),
        duplicados=duplicados(dados, colunas_comparaveis(tipos)),
        fora_de_faixa=fora_de_faixa(dados, numericas, limites),
        inconsistencias=inconsistencias(dados, tipos, numericas),
        tipo_misto=tipo_misto(dados, numericas),
    )
```

**Passo 5: rodar e ver passar** — `pytest tests/dominios/datasets/test_diagnostico.py -v --no-cov`

**Passo 6: commit**
```bash
git add app/dominios/datasets/diagnostico.py app/dominios/datasets/erros.py tests/dominios/datasets/test_diagnostico.py
git commit -m "feat(datasets): diagnostica faltantes, duplicados, fora de faixa, grafias e tipo misto"
```

---

### Tarefa 2: frases do log e ações de limpeza

**Arquivos:**
- Criar: `backend/app/dominios/datasets/frases_limpeza.py`, `backend/app/dominios/datasets/limpeza.py`
- Teste: `backend/tests/dominios/datasets/test_limpeza.py`

**Passo 1: escrever os testes (falham)**
```python
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
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_limpeza.py --no-cov` → FAIL

**Passo 3: implementar**

`app/dominios/datasets/frases_limpeza.py` (textos da spec 16: 1ª pessoa do plural, verbo no passado + quantidade)
```python
"""Frases do log de limpeza: 1ª pessoa do plural, verbo no passado + quantidade (spec 16)."""

from app.compartilhado.textos import pluralizar


def _linhas(n: int) -> str:
    return f"{n} {pluralizar(n, 'linha', 'linhas')}"


def _valores(n: int) -> str:
    return f"{n} {pluralizar(n, 'valor', 'valores')}"


def duplicadas_removidas(n: int) -> str:
    return f"Removemos {_linhas(n)} {pluralizar(n, 'duplicada', 'duplicadas')}."


def vazias_removidas(n: int, coluna: str) -> str:
    return f"Removemos {_linhas(n)} sem valor em {coluna}."


def faltantes_preenchidos(n: int, coluna: str, com: str) -> str:
    faltantes = pluralizar(n, "faltante", "faltantes")
    return f"Preenchemos {_valores(n)} {faltantes} de {coluna} com {com}."


def fora_removidas(n: int, coluna: str) -> str:
    return f"Removemos {_linhas(n)} com {coluna} fora da faixa."


def fora_limitados(n: int, coluna: str, inferior: str, superior: str) -> str:
    return f"Limitamos {_valores(n)} de {coluna} à faixa de {inferior} a {superior}."


def fora_marcados(n: int, coluna: str) -> str:
    return f"Marcamos {_valores(n)} de {coluna} como faltantes por estarem fora da faixa."


def grafias_unificadas(n: int, coluna: str) -> str:
    return f"Unificamos {n} {pluralizar(n, 'grafia', 'grafias')} de {coluna}."


def textos_marcados(n: int, coluna: str) -> str:
    return f"Marcamos {n} {pluralizar(n, 'texto', 'textos')} de {coluna} como faltantes."
```

`app/dominios/datasets/limpeza.py`
```python
"""Ações de limpeza sobre a versão atual, na ordem da spec 03, com log em frases."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.series import converter_para_numero
from app.compartilhado.tipos import TIPOS_NUMERICOS
from app.dominios.datasets import erros
from app.dominios.datasets import frases_limpeza as frases
from app.dominios.datasets.diagnostico import (
    Limites,
    colunas_comparaveis,
    faixa_da_coluna,
    grupos_de_grafias,
)
from app.dominios.datasets.modelos import Celula, EntradaLog, TipoColuna
from app.dominios.datasets.tabela import celula

ORDEM_PROBLEMAS = ("inconsistencia", "tipo_misto", "duplicados", "fora_de_faixa", "faltantes")
MANTER = "manter"
VAZIO = "vazio"


@dataclass(frozen=True, slots=True)
class AcaoLimpeza:
    """O que fazer com um problema; `coluna`, `valor`, `limites` e `grupo` conforme a ação."""

    problema: str
    acao: str
    coluna: str | None = None
    valor: Celula = None
    limites: Limites | None = None
    grupo: str | None = None


@dataclass(frozen=True, slots=True, eq=False)
class _Contexto:
    dados: pd.DataFrame
    tipos: Mapping[str, TipoColuna]
    decimal: str | None


@dataclass(frozen=True, slots=True, eq=False)
class _Efeito:
    dados: pd.DataFrame
    linhas: tuple[int, ...]
    antes: str
    depois: str
    frase: str


@dataclass(frozen=True, slots=True, eq=False)
class ResultadoAcoes:
    dados: pd.DataFrame
    log: tuple[EntradaLog, ...]
    colunas_alteradas: frozenset[str]


type _Manipulador = Callable[[_Contexto, AcaoLimpeza], _Efeito]


def _linhas(mascara: pd.Series) -> tuple[int, ...]:
    return tuple(int(i) for i in mascara[mascara].index.tolist())


def _coluna(ctx: _Contexto, acao: AcaoLimpeza) -> str:
    if acao.coluna is None or acao.coluna not in ctx.dados.columns:
        raise erros.acao_incompativel(acao.coluna, "informe uma coluna que exista.")
    return acao.coluna


def _numeros(ctx: _Contexto, coluna: str) -> pd.Series:
    if ctx.tipos[coluna].tipo not in TIPOS_NUMERICOS:
        raise erros.acao_incompativel(coluna, "ela só vale para colunas numéricas.")
    return converter_para_numero(ctx.dados[coluna], ctx.decimal)


def _no_formato_do_arquivo(valor: Celula, decimal: str | None) -> Celula:
    """Número como texto no formato do arquivo, para colunas que ainda guardam texto."""
    if not isinstance(valor, float | int) or isinstance(valor, bool):
        return valor
    texto = str(int(valor)) if float(valor).is_integer() else repr(float(valor))
    return texto.replace(".", ",") if decimal == "," else texto


def _substituir(
    serie: pd.Series, mascara: pd.Series, novos: object, decimal: str | None
) -> pd.Series:
    """Troca os valores marcados mantendo o tipo da coluna (número ou texto)."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie.mask(mascara, novos)
    if isinstance(novos, pd.Series):
        return serie.mask(mascara, novos.map(lambda v: _no_formato_do_arquivo(v, decimal)))
    return serie.mask(mascara, _no_formato_do_arquivo(celula(novos), decimal))


def _com_coluna(ctx: _Contexto, coluna: str, serie: pd.Series) -> pd.DataFrame:
    dados = ctx.dados.copy()
    dados[coluna] = serie
    return dados


def _remocao(ctx: _Contexto, mascara: pd.Series, frase: str) -> _Efeito:
    restantes = ctx.dados[~mascara]
    antes, depois = f"{len(ctx.dados)} linhas", f"{len(restantes)} linhas"
    return _Efeito(restantes, _linhas(mascara), antes, depois, frase)


def _texto(valor: Celula) -> str:
    if isinstance(valor, float | int) and not isinstance(valor, bool):
        return formatar_numero(float(valor))
    return str(valor)


# Faltantes ---------------------------------------------------------------------------------


def _remover_vazias(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    vazias = ctx.dados[coluna].isna()
    return _remocao(ctx, vazias, frases.vazias_removidas(int(vazias.sum()), coluna))


def _preencher(ctx: _Contexto, coluna: str, valor: Celula, descricao: str) -> _Efeito:
    serie = ctx.dados[coluna]
    vazias = serie.isna()
    novo = _substituir(serie, vazias, valor, ctx.decimal)
    frase = frases.faltantes_preenchidos(int(vazias.sum()), coluna, descricao)
    return _Efeito(_com_coluna(ctx, coluna, novo), _linhas(vazias), VAZIO, _texto(valor), frase)


def _preencher_media(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    media = float(_numeros(ctx, coluna).mean())
    return _preencher(ctx, coluna, media, f"a média ({formatar_numero(media)})")


def _preencher_mediana(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    mediana = float(_numeros(ctx, coluna).median())
    return _preencher(ctx, coluna, mediana, f"a mediana ({formatar_numero(mediana)})")


def _preencher_moda(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    modas = ctx.dados[coluna].dropna().mode()
    if modas.empty:
        raise erros.acao_incompativel(coluna, "a coluna não tem valores para calcular a moda.")
    moda = celula(modas.iloc[0])
    return _preencher(ctx, coluna, moda, f"a moda ({_texto(moda)})")


def _valor_informado(ctx: _Contexto, coluna: str, valor: Celula) -> Celula:
    if valor is None or valor == "":
        raise erros.acao_incompativel(coluna, "informe o valor para preencher.")
    if ctx.tipos[coluna].tipo not in TIPOS_NUMERICOS:
        return valor
    numero = converter_para_numero(pd.Series([valor]), ctx.decimal).iloc[0]
    if pd.isna(numero):
        raise erros.acao_incompativel(coluna, "o valor precisa ser um número.")
    return float(numero)


def _preencher_valor(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    valor = _valor_informado(ctx, coluna, acao.valor)
    return _preencher(ctx, coluna, valor, f"o valor {_texto(valor)}")


# Duplicados --------------------------------------------------------------------------------


def _remover_duplicados(ctx: _Contexto, _acao: AcaoLimpeza) -> _Efeito:
    colunas = colunas_comparaveis(ctx.tipos)
    if colunas:
        copias = ctx.dados.duplicated(subset=colunas, keep="first")
    else:
        copias = pd.Series(False, index=ctx.dados.index)
    return _remocao(ctx, copias, frases.duplicadas_removidas(int(copias.sum())))


# Fora de faixa -----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class _Faixa:
    coluna: str
    numeros: pd.Series
    fora: pd.Series
    inferior: float
    superior: float


def _faixa(ctx: _Contexto, acao: AcaoLimpeza) -> _Faixa:
    coluna = _coluna(ctx, acao)
    numeros = _numeros(ctx, coluna)
    inferior, superior, _ = faixa_da_coluna(numeros.dropna(), acao.limites)
    fora = (numeros < inferior) | (numeros > superior)
    return _Faixa(coluna, numeros, fora, inferior, superior)


def _remover_fora(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    faixa = _faixa(ctx, acao)
    return _remocao(ctx, faixa.fora, frases.fora_removidas(int(faixa.fora.sum()), faixa.coluna))


def _limitar(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    faixa = _faixa(ctx, acao)
    limitados = faixa.numeros.clip(faixa.inferior, faixa.superior)
    serie = _substituir(ctx.dados[faixa.coluna], faixa.fora, limitados, ctx.decimal)
    linhas = _linhas(faixa.fora)
    antes = _texto(celula(faixa.numeros[faixa.fora].iloc[0])) if linhas else ""
    depois = _texto(celula(limitados[faixa.fora].iloc[0])) if linhas else ""
    inferior, superior = formatar_numero(faixa.inferior), formatar_numero(faixa.superior)
    frase = frases.fora_limitados(len(linhas), faixa.coluna, inferior, superior)
    return _Efeito(_com_coluna(ctx, faixa.coluna, serie), linhas, antes, depois, frase)


def _marcar_fora(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    faixa = _faixa(ctx, acao)
    serie = ctx.dados[faixa.coluna].mask(faixa.fora)
    linhas = _linhas(faixa.fora)
    antes = _texto(celula(faixa.numeros[faixa.fora].iloc[0])) if linhas else ""
    frase = frases.fora_marcados(len(linhas), faixa.coluna)
    return _Efeito(_com_coluna(ctx, faixa.coluna, serie), linhas, antes, VAZIO, frase)


# Grafias e tipo misto ----------------------------------------------------------------------


def _unificar(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    serie = ctx.dados[coluna]
    grupos = [g for g in grupos_de_grafias(serie) if acao.grupo in {None, g.forma_preferida}]
    mapa = {v.texto: g.forma_preferida for g in grupos for v in g.variacoes}
    alvo = serie.isin(list(mapa))
    novo = serie.mask(alvo, serie.map(mapa))
    antes, depois = ", ".join(mapa), ", ".join(dict.fromkeys(mapa.values()))
    frase = frases.grafias_unificadas(int(alvo.sum()), coluna)
    return _Efeito(_com_coluna(ctx, coluna, novo), _linhas(alvo), antes, depois, frase)


def _marcar_textos(ctx: _Contexto, acao: AcaoLimpeza) -> _Efeito:
    coluna = _coluna(ctx, acao)
    numeros = _numeros(ctx, coluna)
    textos = ctx.dados[coluna].notna() & numeros.isna()
    linhas = _linhas(textos)
    antes = str(ctx.dados[coluna][textos].iloc[0]) if linhas else ""
    frase = frases.textos_marcados(len(linhas), coluna)
    return _Efeito(_com_coluna(ctx, coluna, numeros), linhas, antes, VAZIO, frase)


MANIPULADORES: dict[tuple[str, str], _Manipulador] = {
    ("faltantes", "remover_linhas"): _remover_vazias,
    ("faltantes", "preencher_media"): _preencher_media,
    ("faltantes", "preencher_mediana"): _preencher_mediana,
    ("faltantes", "preencher_moda"): _preencher_moda,
    ("faltantes", "preencher_valor"): _preencher_valor,
    ("duplicados", "remover"): _remover_duplicados,
    ("fora_de_faixa", "remover_linhas"): _remover_fora,
    ("fora_de_faixa", "limitar"): _limitar,
    ("fora_de_faixa", "marcar_faltante"): _marcar_fora,
    ("inconsistencia", "unificar"): _unificar,
    ("tipo_misto", "marcar_faltante"): _marcar_textos,
}


def _validar(acoes: list[AcaoLimpeza]) -> list[AcaoLimpeza]:
    """Descarta "manter", recusa combinações desconhecidas e ordena pela spec 03."""
    validas = [a for a in acoes if a.acao != MANTER]
    for acao in validas:
        if (acao.problema, acao.acao) not in MANIPULADORES:
            raise erros.acao_incompativel(acao.coluna, f"não existe a ação {acao.acao}.")
    return sorted(validas, key=lambda a: ORDEM_PROBLEMAS.index(a.problema))


def aplicar_acoes(
    dados: pd.DataFrame,
    tipos: Mapping[str, TipoColuna],
    decimal: str | None,
    acoes: list[AcaoLimpeza],
    quando: datetime,
) -> ResultadoAcoes:
    """Aplica as ações em ordem; cada uma que mexeu em alguma linha vira uma entrada no log."""
    log: list[EntradaLog] = []
    alteradas: set[str] = set()
    for acao in _validar(acoes):
        efeito = MANIPULADORES[(acao.problema, acao.acao)](_Contexto(dados, tipos, decimal), acao)
        if not efeito.linhas:
            continue
        removeu = len(efeito.dados) != len(dados)
        alteradas |= set(map(str, dados.columns)) if removeu else {str(acao.coluna)}
        dados = efeito.dados
        log.append(
            EntradaLog(
                acao.problema,
                acao.acao,
                acao.coluna,
                efeito.linhas,
                efeito.antes,
                efeito.depois,
                quando,
                efeito.frase,
            )
        )
    return ResultadoAcoes(dados, tuple(log), frozenset(alteradas))
```

> `limpeza.py` fica perto de 310 linhas (limite 500). Se crescer no M3, separar os manipuladores por problema em `limpeza_faltantes.py` etc., mantendo a tabela `MANIPULADORES` em `limpeza.py`.

**Passo 4: rodar e ver passar** — `pytest tests/dominios/datasets/test_limpeza.py -v --no-cov`

**Passo 5: commit**
```bash
git add app/dominios/datasets/frases_limpeza.py app/dominios/datasets/limpeza.py tests/dominios/datasets/test_limpeza.py
git commit -m "feat(datasets): aplica ações de limpeza na ordem da spec 03 com log em frases"
```

---

### Tarefa 3: casos de uso no `ServicoDatasets`

**Arquivos:**
- Modificar: `backend/app/dominios/datasets/servico.py`
- Teste: `backend/tests/dominios/datasets/test_servico_limpeza.py`

**Passo 1: escrever os testes (falham)** — usam a fixture `servico_datasets` do `conftest.py` (M1.2) e o `dados-exemplo/pesquisa_saude.txt`:
```python
from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.dominios.datasets.servico import AcaoLimpeza, Limites, ServicoDatasets


def test_diagnostico_do_exemplo_tem_os_problemas_plantados(
    servico_datasets: ServicoDatasets,
) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    limites = {"altura_m": Limites(1.2, 2.2), "idade": Limites(1, 110), "peso_kg": Limites(30, 200)}

    diagnostico = servico_datasets.diagnosticar(dataset_id, limites)

    assert sum(f.n for f in diagnostico.faltantes) == 7
    assert [(d.linha_original, d.copias) for d in diagnostico.duplicados] == [(44, (45, 46, 47))]
    assert sum(len(f.ocorrencias) for f in diagnostico.fora_de_faixa) == 5
    assert [len(i.grupos) for i in diagnostico.inconsistencias] == [2]


def test_limpar_atualiza_atual_log_e_tipos(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id

    resultado = servico_datasets.limpar(
        dataset_id,
        [
            AcaoLimpeza("duplicados", "remover"),
            AcaoLimpeza("inconsistencia", "unificar", "cidade"),
        ],
    )

    assert (resultado.n_linhas, resultado.n_linhas_original) == (227, 230)
    assert [e.frase for e in resultado.log] == [
        "Unificamos 11 grafias de cidade.",
        "Removemos 3 linhas duplicadas.",
    ]
    cidade = next(c for c in resultado.colunas if c.coluna == "cidade")
    assert cidade.motivo == "São categorias sem ordem natural (7 categorias)."
    assert len(servico_datasets.obter(dataset_id).original) == 230


def test_log_acumula_entre_limpezas(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id

    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])
    resultado = servico_datasets.limpar(
        dataset_id, [AcaoLimpeza("faltantes", "preencher_moda", "cidade")]
    )

    assert len(resultado.log) == 2
    assert len(servico_datasets.resumo(dataset_id).log_limpeza) == 2


def test_tipo_manual_e_mantido_depois_da_limpeza(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.alterar_tipo(dataset_id, "idade", TipoVariavel.DISCRETA)

    resultado = servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])

    idade = next(c for c in resultado.colunas if c.coluna == "idade")
    assert (idade.tipo, idade.origem) == (TipoVariavel.DISCRETA, OrigemTipo.MANUAL)


def test_desfazer_tudo_volta_ao_original(servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])

    resultado = servico_datasets.desfazer_limpeza(dataset_id)

    assert (resultado.n_linhas, resultado.log) == (230, ())
    dataset = servico_datasets.obter(dataset_id)
    assert dataset.atual is not dataset.original
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_servico_limpeza.py --no-cov` → FAIL (`ImportError: AcaoLimpeza`)

**Passo 3: implementar** — `app/dominios/datasets/servico.py` completo (o que muda em relação ao M1.2: imports, `__all__`, `ResultadoLimpeza`, os métodos `diagnosticar`, `limpar`, `desfazer_limpeza`, `_reclassificar`, `_resultado_limpeza` e a função `_tipo_atualizado`):
```python
"""Fachada do domínio datasets: casos de uso de importação, consulta e tipos (D54)."""

import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Literal

import pandas as pd

from app.compartilhado.tipos import TIPOS_NUMERICOS, OrigemTipo, TipoVariavel
from app.core.config import Configuracao, obter_configuracao
from app.core.erros import ErroAplicacao
from app.dominios.datasets import erros
from app.dominios.datasets.ajuste_tipo import ajustar_tipo
from app.dominios.datasets.classificacao import (
    ColunaLida,
    Limiares,
    classificar,
    classificar_tabela,
    descrever,
    ler_coluna,
)
from app.dominios.datasets.diagnostico import Diagnostico, Limites, diagnosticar
from app.dominios.datasets.leitura import ler_arquivo
from app.dominios.datasets.limpeza import AcaoLimpeza, aplicar_acoes
from app.dominios.datasets.modelos import (
    Dataset,
    EntradaLog,
    LinhaDados,
    MetadadosLeitura,
    OpcoesLeitura,
    TipoColuna,
)
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.tabela import linhas_dados, paginar

__all__ = [
    "AcaoLimpeza",
    "ColunaAnalise",
    "Diagnostico",
    "Importacao",
    "Limites",
    "OpcoesLeitura",
    "PaginaDataset",
    "ResultadoLimpeza",
    "Resumo",
    "ServicoDatasets",
    "obter_servico_datasets",
]

type Versao = Literal["atual", "original"]


@dataclass(frozen=True, slots=True)
class Importacao:
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    previa: tuple[LinhaDados, ...]
    colunas: tuple[TipoColuna, ...]


@dataclass(frozen=True, slots=True)
class Resumo:
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    n_linhas: int
    n_linhas_original: int
    n_colunas: int
    log_limpeza: tuple[EntradaLog, ...]


@dataclass(frozen=True, slots=True)
class PaginaDataset:
    resumo: Resumo
    versao: Versao
    pagina: int
    tamanho: int
    total_paginas: int
    linhas: tuple[LinhaDados, ...]


@dataclass(frozen=True, slots=True, eq=False)
class ColunaAnalise:
    """O que o domínio analise precisa de uma coluna: tipo, números ou textos e a ordem."""

    nome: str
    tipo: TipoVariavel
    numeros: pd.Series | None
    textos: pd.Series
    categorias_ordem: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ResultadoLimpeza:
    log: tuple[EntradaLog, ...]
    n_linhas: int
    n_linhas_original: int
    colunas: tuple[TipoColuna, ...]


class ServicoDatasets:
    """Casos de uso sobre datasets em memória (ADR 0004)."""

    def __init__(self, repositorio: RepositorioDatasets, config: Configuracao) -> None:
        self._repositorio = repositorio
        self._config = config

    @property
    def limiares(self) -> Limiares:
        return Limiares(
            discreta=self._config.limiar_discreta,
            unicos_identificador=self._config.limiar_unicos_identificador,
            numerico=self._config.limiar_numerico,
        )

    def importar(self, conteudo: bytes, nome_arquivo: str, opcoes: OpcoesLeitura) -> Importacao:
        """Lê o arquivo, classifica as colunas e guarda o dataset."""
        if len(conteudo) > self._config.limite_arquivo_bytes:
            raise erros.arquivo_grande(self._config.limite_arquivo_mb)
        leitura = ler_arquivo(conteudo, nome_arquivo, opcoes)
        tipos = classificar_tabela(leitura.dados, leitura.metadados.decimal, self.limiares)
        dataset = Dataset(
            id=uuid.uuid4().hex,
            nome_arquivo=nome_arquivo,
            metadados=leitura.metadados,
            original=leitura.dados,
            atual=leitura.dados.copy(),
            tipos=tipos,
        )
        self._repositorio.adicionar(dataset)
        previa = linhas_dados(dataset.atual.head(self._config.tamanho_previa))
        return Importacao(
            dataset.id, nome_arquivo, dataset.metadados, previa, tuple(tipos.values())
        )

    def importar_exemplo(self) -> Importacao:
        """Importa o arquivo de demonstração de dados-exemplo/ (D52)."""
        caminho = self._config.pasta_exemplos / self._config.arquivo_exemplo
        return self.importar(caminho.read_bytes(), caminho.name, OpcoesLeitura())

    def obter(self, dataset_id: str) -> Dataset:
        return self._repositorio.obter(dataset_id)

    def remover(self, dataset_id: str) -> None:
        self._repositorio.remover(dataset_id)

    def resumo(self, dataset_id: str) -> Resumo:
        dataset = self.obter(dataset_id)
        return Resumo(
            dataset_id=dataset.id,
            nome_arquivo=dataset.nome_arquivo,
            metadados=dataset.metadados,
            n_linhas=len(dataset.atual),
            n_linhas_original=len(dataset.original),
            n_colunas=dataset.atual.shape[1],
            log_limpeza=tuple(dataset.log_limpeza),
        )

    def pagina(self, dataset_id: str, pagina: int, tamanho: int, versao: Versao) -> PaginaDataset:
        """Linhas paginadas da versão atual (após limpeza) ou original."""
        dataset = self.obter(dataset_id)
        dados = dataset.atual if versao == "atual" else dataset.original
        recorte = paginar(dados, pagina, tamanho)
        return PaginaDataset(
            self.resumo(dataset_id), versao, pagina, tamanho, recorte.total_paginas, recorte.linhas
        )

    def colunas(self, dataset_id: str) -> list[TipoColuna]:
        return list(self.obter(dataset_id).tipos.values())

    def _coluna_lida(self, dataset: Dataset, coluna: str) -> ColunaLida:
        if coluna not in dataset.tipos:
            raise erros.coluna_nao_encontrada(coluna)
        serie = dataset.atual[coluna]
        return ler_coluna(coluna, serie, dataset.metadados.decimal, self.limiares)

    def alterar_tipo(
        self,
        dataset_id: str,
        coluna: str,
        tipo: TipoVariavel,
        categorias_ordem: list[str] | None = None,
    ) -> TipoColuna:
        """Ajuste manual do tipo (spec 02); a escolha vale até o próximo ajuste."""
        dataset = self.obter(dataset_id)
        novo = ajustar_tipo(self._coluna_lida(dataset, coluna), tipo, categorias_ordem)
        dataset.tipos[coluna] = novo
        return novo

    def coluna_para_analise(self, dataset_id: str, coluna: str) -> ColunaAnalise:
        """Dados de uma coluna da versão atual, já convertidos conforme o tipo."""
        dataset = self.obter(dataset_id)
        lida = self._coluna_lida(dataset, coluna)
        tipo = dataset.tipos[coluna]
        numeros = lida.numeros if tipo.tipo in TIPOS_NUMERICOS else None
        return ColunaAnalise(coluna, tipo.tipo, numeros, lida.textos, tipo.categorias_ordem)

    def diagnosticar(self, dataset_id: str, limites: Mapping[str, Limites]) -> Diagnostico:
        """Problemas da versão atual; não altera nada (spec 03)."""
        dataset = self.obter(dataset_id)
        return diagnosticar(dataset.atual, dataset.tipos, dataset.metadados.decimal, limites)

    def limpar(self, dataset_id: str, acoes: list[AcaoLimpeza]) -> ResultadoLimpeza:
        """Aplica as ações sobre a versão atual; o original nunca muda."""
        dataset = self.obter(dataset_id)
        decimal = dataset.metadados.decimal
        resultado = aplicar_acoes(dataset.atual, dataset.tipos, decimal, acoes, datetime.now())
        dataset.atual = resultado.dados
        dataset.log_limpeza.extend(resultado.log)
        self._reclassificar(dataset, resultado.colunas_alteradas)
        return self._resultado_limpeza(dataset)

    def desfazer_limpeza(self, dataset_id: str) -> ResultadoLimpeza:
        """ "Desfazer tudo": a versão atual volta a ser o original e o log é zerado."""
        dataset = self.obter(dataset_id)
        dataset.atual = dataset.original.copy()
        dataset.log_limpeza.clear()
        self._reclassificar(dataset, list(dataset.tipos))
        return self._resultado_limpeza(dataset)

    def _reclassificar(self, dataset: Dataset, colunas: Iterable[str]) -> None:
        for nome in colunas:
            lida = self._coluna_lida(dataset, nome)
            dataset.tipos[nome] = _tipo_atualizado(lida, dataset.tipos[nome])

    @staticmethod
    def _resultado_limpeza(dataset: Dataset) -> ResultadoLimpeza:
        return ResultadoLimpeza(
            log=tuple(dataset.log_limpeza),
            n_linhas=len(dataset.atual),
            n_linhas_original=len(dataset.original),
            colunas=tuple(dataset.tipos.values()),
        )


def _tipo_atualizado(lida: ColunaLida, anterior: TipoColuna) -> TipoColuna:
    """Automáticas são reclassificadas; manuais mantêm o tipo se ainda for válido (spec 03)."""
    if anterior.origem == OrigemTipo.MANUAL:
        try:
            return ajustar_tipo(lida, anterior.tipo, list(anterior.categorias_ordem) or None)
        except ErroAplicacao:
            pass
    return descrever(lida, classificar(lida), OrigemTipo.AUTO)


@lru_cache
def obter_servico_datasets() -> ServicoDatasets:
    """Instância única (repositório em memória compartilhado entre requisições)."""
    config = obter_configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)
```

**Passo 4: rodar e ver passar** — `pytest tests/dominios/datasets -v --no-cov`

**Passo 5: commit**
```bash
git add app/dominios/datasets/servico.py tests/dominios/datasets/test_servico_limpeza.py
git commit -m "feat(datasets): adiciona diagnóstico, limpeza e desfazer à fachada do domínio"
```

---

### Tarefa 4: schemas e rotas

**Arquivos:**
- Modificar: `backend/app/dominios/datasets/schemas.py`, `backend/app/dominios/datasets/router.py`
- Teste: `backend/tests/dominios/datasets/test_router_limpeza.py`

**Passo 1: escrever os testes (falham)**
```python
import json

from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_diagnostico_com_limites(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    limites = json.dumps({"idade": {"min": 1, "max": 110}})

    resposta = cliente.get(f"/api/datasets/{dataset_id}/diagnostico", params={"limites": limites})

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["n_linhas"] == 230
    assert corpo["duplicados"] == [{"linha_original": 44, "copias": [45, 46, 47]}]
    idade = next(f for f in corpo["fora_de_faixa"] if f["coluna"] == "idade")
    assert idade["origem"] == "usuario"


def test_diagnostico_com_limites_invalidos(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    url = f"/api/datasets/{dataset_id}/diagnostico"

    invertidos = cliente.get(url, params={"limites": '{"idade": {"min": 110, "max": 1}}'})
    mal_formados = cliente.get(url, params={"limites": "{nao e json"})

    assert invertidos.status_code == 400
    assert invertidos.json()["codigo"] == "LIMITES_INVALIDOS"
    assert mal_formados.status_code == 422


def test_aplicar_e_desfazer_limpeza(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    pedido = {
        "acoes": [
            {"problema": "duplicados", "acao": "remover"},
            {"problema": "faltantes", "acao": "preencher_mediana", "coluna": "peso_kg"},
            {"problema": "faltantes", "acao": "manter", "coluna": "cidade"},
        ]
    }

    aplicada = cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=pedido)
    resumo = cliente.get(f"/api/datasets/{dataset_id}").json()["resumo"]
    desfeita = cliente.post(f"/api/datasets/{dataset_id}/limpeza/desfazer")

    assert aplicada.status_code == 200
    assert aplicada.json()["n_linhas"] == 227
    assert [e["acao"] for e in aplicada.json()["log"]] == ["remover", "preencher_mediana"]
    assert len(resumo["log_limpeza"]) == 2
    assert desfeita.json()["n_linhas"] == 230
    assert desfeita.json()["log"] == []


def test_acao_incompativel(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    pedido = {"acoes": [{"problema": "faltantes", "acao": "preencher_media", "coluna": "cidade"}]}

    resposta = cliente.post(f"/api/datasets/{dataset_id}/limpeza", json=pedido)

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "ACAO_INCOMPATIVEL"
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_router_limpeza.py --no-cov` → FAIL (404)

**Passo 3: schemas** — em `app/dominios/datasets/schemas.py`, trocar o import do Pydantic por `from pydantic import BaseModel, ConfigDict, TypeAdapter` e acrescentar no fim:
```python
class Limites(Modelo):
    min: float | None = None
    max: float | None = None


LIMITES_POR_COLUNA = TypeAdapter(dict[str, Limites])


class ValoresSugeridos(Modelo):
    media: float | None
    mediana: float | None
    moda: Celula


class FaltantesColuna(Modelo):
    coluna: str
    n: int
    linhas: list[int]
    sugeridos: ValoresSugeridos


class GrupoDuplicado(Modelo):
    linha_original: int
    copias: list[int]


class Ocorrencia(Modelo):
    linha: int
    valor: Celula


class ForaDeFaixaColuna(Modelo):
    coluna: str
    limite_inferior: float
    limite_superior: float
    origem: Literal["iqr", "usuario"]
    ocorrencias: list[Ocorrencia]


class Grafia(Modelo):
    texto: str
    n: int


class GrupoGrafias(Modelo):
    forma_preferida: str
    variacoes: list[Grafia]


class InconsistenciaColuna(Modelo):
    coluna: str
    grupos: list[GrupoGrafias]


class TipoMistoColuna(Modelo):
    coluna: str
    ocorrencias: list[Ocorrencia]


class Diagnostico(Modelo):
    n_linhas: int
    faltantes: list[FaltantesColuna]
    duplicados: list[GrupoDuplicado]
    fora_de_faixa: list[ForaDeFaixaColuna]
    inconsistencias: list[InconsistenciaColuna]
    tipo_misto: list[TipoMistoColuna]


type Problema = Literal["faltantes", "duplicados", "fora_de_faixa", "inconsistencia", "tipo_misto"]
type Acao = Literal[
    "manter",
    "remover_linhas",
    "preencher_media",
    "preencher_mediana",
    "preencher_moda",
    "preencher_valor",
    "remover",
    "limitar",
    "marcar_faltante",
    "unificar",
]


class AcaoLimpeza(BaseModel):
    problema: Problema
    acao: Acao
    coluna: str | None = None
    valor: Celula = None
    limites: Limites | None = None
    grupo: str | None = None


class PedidoLimpeza(BaseModel):
    acoes: list[AcaoLimpeza]


class ResultadoLimpeza(Modelo):
    log: list[EntradaLog]
    n_linhas: int
    n_linhas_original: int
    colunas: list[TipoColuna]
```

**Passo 4: router completo** — `app/dominios/datasets/router.py`:
```python
"""Rotas HTTP do domínio datasets (spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.dominios.datasets import schemas
from app.dominios.datasets.schemas import (
    AlteracaoTipo,
    DatasetCriado,
    Diagnostico,
    PaginaDataset,
    PedidoLimpeza,
    ResultadoLimpeza,
    TipoColuna,
)
from app.dominios.datasets.servico import (
    AcaoLimpeza,
    Limites,
    OpcoesLeitura,
    ServicoDatasets,
    obter_servico_datasets,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])

Servico = Annotated[ServicoDatasets, Depends(obter_servico_datasets)]
TAMANHO_MAXIMO_PAGINA = 500


def _opcoes_leitura(
    separador: Annotated[str | None, Form()] = None,
    decimal: Annotated[Literal[",", "."] | None, Form()] = None,
    codificacao: Annotated[str | None, Form()] = None,
    aba: Annotated[str | None, Form()] = None,
    tem_cabecalho: Annotated[bool | None, Form()] = None,
) -> OpcoesLeitura:
    """Campos opcionais do formulário que sobrescrevem a detecção (spec 01)."""
    return OpcoesLeitura(separador, decimal, codificacao, aba, tem_cabecalho)


Opcoes = Annotated[OpcoesLeitura, Depends(_opcoes_leitura)]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Importa um arquivo de dados")
def importar(servico: Servico, arquivo: UploadFile, opcoes: Opcoes) -> DatasetCriado:
    nome = arquivo.filename or "arquivo"
    return DatasetCriado.model_validate(servico.importar(arquivo.file.read(), nome, opcoes))


@router.post(
    "/exemplo",
    status_code=status.HTTP_201_CREATED,
    summary="Importa o arquivo de exemplo (pesquisa_saude.txt)",
)
def importar_exemplo(servico: Servico) -> DatasetCriado:
    return DatasetCriado.model_validate(servico.importar_exemplo())


@router.get("/{dataset_id}", summary="Resumo do dataset e linhas paginadas")
def obter_pagina(
    servico: Servico,
    dataset_id: str,
    pagina: Annotated[int, Query(ge=1)] = 1,
    tamanho: Annotated[int, Query(ge=1, le=TAMANHO_MAXIMO_PAGINA)] = 20,
    versao: Literal["atual", "original"] = "atual",
) -> PaginaDataset:
    return PaginaDataset.model_validate(servico.pagina(dataset_id, pagina, tamanho, versao))


@router.delete(
    "/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Descarta o dataset"
)
def remover(servico: Servico, dataset_id: str) -> Response:
    servico.remover(dataset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{dataset_id}/colunas", summary="Tipo de cada coluna, com o motivo")
def listar_colunas(servico: Servico, dataset_id: str) -> list[TipoColuna]:
    return [TipoColuna.model_validate(c) for c in servico.colunas(dataset_id)]


@router.patch("/{dataset_id}/colunas/{coluna}", summary="Corrige o tipo de uma coluna")
def alterar_tipo(
    servico: Servico, dataset_id: str, coluna: str, alteracao: AlteracaoTipo
) -> TipoColuna:
    novo = servico.alterar_tipo(dataset_id, coluna, alteracao.tipo, alteracao.categorias_ordem)
    return TipoColuna.model_validate(novo)


def _limites(limite: schemas.Limites | None) -> Limites | None:
    return Limites(limite.min, limite.max) if limite else None


def _acao(acao: schemas.AcaoLimpeza) -> AcaoLimpeza:
    limites = _limites(acao.limites)
    return AcaoLimpeza(acao.problema, acao.acao, acao.coluna, acao.valor, limites, acao.grupo)


def _limites_por_coluna(
    limites: Annotated[
        str | None,
        Query(description='Limites por coluna em JSON: {"idade": {"min": 1, "max": 110}}'),
    ] = None,
) -> dict[str, Limites]:
    try:
        lidos = schemas.LIMITES_POR_COLUNA.validate_json(limites or "{}")
    except ValidationError as erro:
        detalhe = {"type": "json_invalid", "loc": ("query", "limites"), "msg": "JSON inválido"}
        raise RequestValidationError([detalhe]) from erro
    return {coluna: Limites(faixa.min, faixa.max) for coluna, faixa in lidos.items()}


LimitesPorColuna = Annotated[dict[str, Limites], Depends(_limites_por_coluna)]


@router.get("/{dataset_id}/diagnostico", summary="Problemas encontrados (não altera nada)")
def diagnosticar(servico: Servico, dataset_id: str, limites: LimitesPorColuna) -> Diagnostico:
    return Diagnostico.model_validate(servico.diagnosticar(dataset_id, limites))


@router.post("/{dataset_id}/limpeza", summary="Aplica ações de limpeza na versão atual")
def limpar(servico: Servico, dataset_id: str, pedido: PedidoLimpeza) -> ResultadoLimpeza:
    acoes = [_acao(acao) for acao in pedido.acoes]
    return ResultadoLimpeza.model_validate(servico.limpar(dataset_id, acoes))


@router.post("/{dataset_id}/limpeza/desfazer", summary="Desfaz toda a limpeza")
def desfazer_limpeza(servico: Servico, dataset_id: str) -> ResultadoLimpeza:
    return ResultadoLimpeza.model_validate(servico.desfazer_limpeza(dataset_id))
```

> `limites` chega como JSON na query (contrato da spec 14). O FastAPI 0.142 não aceita `Json[...]` em parâmetro de query, por isso a dependência `_limites_por_coluna` valida com `TypeAdapter`; JSON mal formado vira 422 `ENTRADA_INVALIDA` pelo handler existente. `_limites` e `_acao` só convertem schema → objeto de domínio (sem regra).

**Passo 5: suíte toda**
```bash
ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest
```

**Passo 6: commit**
```bash
git add app/dominios/datasets/schemas.py app/dominios/datasets/router.py tests/dominios/datasets/test_router_limpeza.py
git commit -m "feat(datasets): expõe diagnóstico, limpeza e desfazer na API"
```

---

### Tarefa 5: tipos do frontend, decisão, specs e CHANGELOG

**Passo 1: tipos**
```bash
python scripts/exportar_openapi.py
cd ../frontend && npm run gerar:tipos && npm run lint && npm run build && cd ../backend
```
Esperado: `schema.d.ts` com `Diagnostico`, `AcaoLimpeza`, `PedidoLimpeza`, `ResultadoLimpeza`…

**Passo 2: `docs/decisions.md`**
```
| D50 | DD/10/2026 | Duplicados comparam todas as colunas menos as `identificador`; a 1ª ocorrência fica | Comparar a linha inteira | Com uma coluna id, nenhuma linha seria igual (design 3a: "igual à linha 44, exceto id") | — |
```

**Passo 3: `docs/specs/03-limpeza.md`**
- Tabela do diagnóstico, linha "Duplicados": `df.duplicated(keep="first")` nas colunas que não são identificador (D50).
- Linha "Fora de faixa": "limites informados pelo usuário (`min` e/ou `max`; o lado vazio segue o IQR); `min ≥ max` → erro `LIMITES_INVALIDOS`".
- Em "Regras", acrescentar: "Tipos `manual` são mantidos após a limpeza se continuarem válidos; só as contagens são atualizadas." e "Se uma coluna numérica ainda tem texto (tipo misto mantido), o valor de preenchimento entra como texto no formato do arquivo."
- Em "Log", trocar os exemplos para o formato real: "Removemos 3 linhas duplicadas." / "Preenchemos 3 valores faltantes de peso_kg com a mediana (69,4)."

**Passo 4: `CHANGELOG.md`** — *Não lançado › Adicionado*:
```
- Diagnóstico de limpeza (faltantes, duplicados, fora de faixa com limites opcionais, grafias diferentes e tipo misto) e aplicação de ações com log em frases, "Desfazer tudo" e reclassificação dos tipos (`GET /api/datasets/{id}/diagnostico`, `POST /api/datasets/{id}/limpeza`, `POST /api/datasets/{id}/limpeza/desfazer`).
```

**Passo 5: commit**
```bash
git add ../frontend/src/shared/api/schema.d.ts ../docs ../CHANGELOG.md
git commit -m "docs: registra D50 e atualiza spec 03 com as regras da limpeza"
```

---

### Tarefa 6: verificação final, teste manual e PR

**Passo 1: tudo verde** (backend, frontend e jscpd, como no M1.2).

**Passo 2: teste manual pelo preview** — subir `backend` e em `/docs`:
1. `POST /api/datasets/exemplo` → guardar o `dataset_id`.
2. `GET .../diagnostico?limites={"idade":{"min":1,"max":110},"altura_m":{"min":1.2,"max":2.2},"peso_kg":{"min":30,"max":200}}` → 7 faltantes em 4 colunas; duplicados 45, 46, 47 da 44; 5 valores fora de faixa (altura linha 77, idade 19 e 201, peso 99 e 160); 2 grupos de grafias em cidade (os números do print 3a).
3. `POST .../limpeza` com remover duplicados, unificar cidade, preencher peso_kg com a mediana → `n_linhas = 227`, 3 frases no log, `cidade` com 7 categorias.
4. `GET /api/datasets/{id}` → `resumo.log_limpeza` com as 3 entradas.
5. `POST .../limpeza/desfazer` → 230 linhas, log vazio.

**Passo 3: resumo e PR** — mostrar o resumo ao usuário; só com o ok:
```bash
git push -u origin feat/datasets-limpeza
gh pr create --base develop --title "feat(datasets): diagnóstico e limpeza com log e desfazer (M1.3)" --body "<resumo + spec 03 + checklist do padroes-codigo.md §8>"
```
Sem atribuição de IA. Merge só quando o usuário pedir, com os 3 checks verdes.

---

## Critérios de pronto do M1.3
- [ ] Diagnóstico com os 5 problemas da spec 03, sem alterar os dados
- [ ] Todas as ações da spec 03, na ordem fixa, com log em frases e linhas afetadas
- [ ] `original` intocado; "Desfazer tudo" restaura e zera o log
- [ ] Tipos reclassificados depois da limpeza (manuais mantidos)
- [ ] `schema.d.ts` regenerado; D50, spec 03 e CHANGELOG atualizados; CI verde
