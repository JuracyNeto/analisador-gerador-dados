# M1.2 — Datasets: leitura e tipos — plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md` e os contratos em `docs/plans/2026-10-03-m1-visao-geral.md`.

**Objetivo:** importar TXT/CSV/TSV/XLSX/JSON com detecção automática (spec 01), classificar o tipo de cada coluna com motivo (spec 02), guardar o dataset em memória (ADR 0004) e expor importação, consulta, colunas e ajuste de tipo pela API (spec 14).

**Arquitetura:** `compartilhado/` ganha tipos, formatação pt-BR, helpers de séries e de texto. O domínio `datasets` fica dividido em módulos puros (`deteccao`, `leitura`, `escalas_ordinais`, `classificacao`, `ajuste_tipo`, `tabela`), um `repositorio` em memória e a fachada `servico` (`ServicoDatasets` + `obter_servico_datasets`). O `router` só monta dependências e converte para os schemas. A injeção entre domínios segue a ADR 0009, escrita aqui.

**Stack:** Python 3.12, pandas 3 (copy-on-write, dtype `str`), numpy, openpyxl, FastAPI, Pydantic 2, pytest.

**Branch:** `feat/datasets-leitura-tipos` (sai de `develop`) → PR para `develop`.

**Prazo sugerido:** 10/10/2026. **Depende de:** nada (pode andar junto com o M1.1).

**Código validado:** o código das tarefas foi rodado antes num rascunho com ruff, ruff format, mypy, complexipy e pytest (175 testes, 99% de cobertura). Se algo falhar na sua máquina, corrija a causa; não silencie regras.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | `compartilhado/`: tipos, números, textos, séries | `app/compartilhado/*.py` |
| 2 | Configuração e erro 413 | `core/config.py`, `core/erros.py` |
| 3 | Modelos e erros do domínio | `datasets/modelos.py`, `datasets/erros.py` |
| 4 | Detecção (formato, codificação, separador, decimal, cabeçalho) | `datasets/deteccao.py` |
| 5 | Leitura por formato | `datasets/leitura.py`, `tests/fixtures/*` |
| 6 | Escalas ordinais e classificação | `datasets/escalas_ordinais.py`, `datasets/classificacao.py` |
| 7 | Ajuste manual do tipo | `datasets/ajuste_tipo.py` |
| 8 | Tabela (células e paginação) e repositório | `datasets/tabela.py`, `datasets/repositorio.py` |
| 9 | Fachada `ServicoDatasets` | `datasets/servico.py`, `tests/conftest.py` |
| 10 | Schemas, router e registro no `main` | `datasets/schemas.py`, `datasets/router.py`, `main.py` |
| 11 | Tipos do frontend, ADR 0009, decisões, specs e CHANGELOG | `schema.d.ts`, `docs/**` |
| 12 | Verificação final, teste manual e PR | — |

Todas as tarefas rodam em `backend/` com o venv ativo (`source .venv/Scripts/activate` no Git Bash ou `.venv\Scripts\activate` no PowerShell). Testes isolados com `--no-cov` (a cobertura mínima vale para a suíte inteira).

---

### Tarefa 1: `compartilhado/` — tipos, números, textos e séries

**Arquivos:**
- Criar: `backend/app/compartilhado/tipos.py`, `numeros.py`, `textos.py`, `series.py`
- Teste: `backend/tests/compartilhado/__init__.py` (vazio), `test_numeros.py`, `test_textos.py`, `test_series.py`

**Passo 1: escrever os testes (falham)**

`tests/compartilhado/test_numeros.py`
```python
import pytest

from app.compartilhado.numeros import formatar_inteiro, formatar_numero, formatar_percentual


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (70.314, "70,31"),
        (12345.6, "12.346"),
        (0.0012346, "0,001235"),
        (72.0, "72"),
        (0.0, "0"),
        (-3.14159, "-3,142"),
        (1.5, "1,5"),
    ],
)
def test_formatar_numero_usa_4_significativos_sem_zeros_a_direita(
    valor: float, esperado: str
) -> None:
    assert formatar_numero(valor) == esperado


def test_formatar_numero_aceita_outra_precisao() -> None:
    assert formatar_numero(70.314, casas_significativas=3) == "70,3"


def test_formatar_inteiro_usa_ponto_de_milhar() -> None:
    assert formatar_inteiro(1234567) == "1.234.567"


def test_formatar_percentual_usa_virgula() -> None:
    assert formatar_percentual(21.6) == "21,6%"
    assert formatar_percentual(100) == "100,0%"
```

`tests/compartilhado/test_textos.py`
```python
import pytest

from app.compartilhado.textos import juntar_lista, normalizar_texto, pluralizar


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [("  São   Paulo ", "sao paulo"), ("GOIÂNIA", "goiania"), ("Pós-graduação", "pos-graduacao")],
)
def test_normalizar_texto_tira_acento_caixa_e_espacos(texto: str, esperado: str) -> None:
    assert normalizar_texto(texto) == esperado


def test_pluralizar_escolhe_pela_quantidade() -> None:
    assert pluralizar(1, "linha", "linhas") == "linha"
    assert pluralizar(0, "linha", "linhas") == "linhas"
    assert pluralizar(3, "linha", "linhas") == "linhas"


@pytest.mark.parametrize(
    ("itens", "esperado"),
    [([], ""), (["a"], "a"), (["a", "b"], "a e b"), (["a", "b", "c"], "a, b e c")],
)
def test_juntar_lista_em_portugues(itens: list[str], esperado: str) -> None:
    assert juntar_lista(itens) == esperado
```

`tests/compartilhado/test_series.py`
```python
import math

import pandas as pd
import pytest

from app.compartilhado.series import (
    casas_decimais,
    converter_para_numero,
    eh_inteira,
    proporcao_numerica,
)


def test_converter_texto_com_virgula_decimal_e_ponto_de_milhar() -> None:
    serie = pd.Series(["1,72", "1.234,5", " 7 ", "doze", None])

    convertida = converter_para_numero(serie, decimal=",")

    assert convertida.iloc[:3].tolist() == [1.72, 1234.5, 7.0]
    assert math.isnan(convertida.iloc[3])
    assert math.isnan(convertida.iloc[4])
    assert convertida.dtype == "float64"


def test_converter_serie_ja_numerica_mantem_valores() -> None:
    assert converter_para_numero(pd.Series([1, 2])).tolist() == [1.0, 2.0]


def test_converter_booleanos_nao_vira_numero() -> None:
    assert converter_para_numero(pd.Series([True, False])).isna().all()


def test_proporcao_numerica_ignora_faltantes() -> None:
    serie = pd.Series(["1", "2", "3", "doze", None])

    assert proporcao_numerica(serie) == pytest.approx(0.75)
    assert proporcao_numerica(pd.Series([None, None])) == 0.0


@pytest.mark.parametrize(
    ("valores", "esperado"),
    [([1.0, 2.0, 3.0], True), ([1.0, 2.5], False), ([1.0, None, 4.0], True)],
)
def test_eh_inteira(valores: list[float | None], esperado: bool) -> None:
    assert eh_inteira(pd.Series(valores, dtype="float64")) is esperado


@pytest.mark.parametrize(
    ("valores", "esperado"),
    [([1.0, 2.0], 0), ([1.5, 2.0], 1), ([1.62, 1.7], 2), ([0.1234567], 6)],
)
def test_casas_decimais(valores: list[float], esperado: int) -> None:
    assert casas_decimais(pd.Series(valores)) == esperado
```

**Passo 2: rodar e ver falhar**
`pytest tests/compartilhado -v --no-cov` → FAIL (`ModuleNotFoundError: app.compartilhado.numeros`)

**Passo 3: implementar**

`app/compartilhado/tipos.py`
```python
"""Enums e value objects compartilhados entre domínios (padroes-codigo.md §2)."""

from enum import StrEnum


class TipoVariavel(StrEnum):
    """Tipos de variável da spec 02 (identificador é auxiliar e fica fora das análises)."""

    NOMINAL = "nominal"
    ORDINAL = "ordinal"
    DISCRETA = "discreta"
    CONTINUA = "continua"
    BINARIA = "binaria"
    IDENTIFICADOR = "identificador"


class OrigemTipo(StrEnum):
    """Quem definiu o tipo: a classificação automática ou o usuário."""

    AUTO = "auto"
    MANUAL = "manual"


TIPOS_NUMERICOS = frozenset({TipoVariavel.DISCRETA, TipoVariavel.CONTINUA})
TIPOS_CATEGORICOS = frozenset({TipoVariavel.NOMINAL, TipoVariavel.ORDINAL, TipoVariavel.BINARIA})
```

`app/compartilhado/numeros.py`
```python
"""Formatação de números no padrão pt-BR (vírgula decimal, ponto de milhar)."""

import math

CASAS_SIGNIFICATIVAS_PADRAO = 4


def _trocar_separadores(texto: str) -> str:
    """Converte '1,234.5' (formato do Python) em '1.234,5'."""
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def casas_para_significativos(valor: float, casas_significativas: int) -> int:
    """Casas decimais que mantêm `casas_significativas` dígitos, sem cortar a parte inteira."""
    if valor == 0 or not math.isfinite(valor):
        return 0
    ordem = math.floor(math.log10(abs(valor)))
    return max(0, casas_significativas - 1 - ordem)


def formatar_numero(valor: float, casas_significativas: int = CASAS_SIGNIFICATIVAS_PADRAO) -> str:
    """Número com até 4 dígitos significativos, sem zeros à direita: 70,31 · 12.346 · 0,001235."""
    casas = casas_para_significativos(valor, casas_significativas)
    texto = f"{valor:,.{casas}f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return _trocar_separadores(texto)


def formatar_inteiro(valor: int) -> str:
    """Inteiro com ponto de milhar: 1.234."""
    return _trocar_separadores(f"{valor:,d}")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    """Percentual já na escala 0–100: 21,6%."""
    return _trocar_separadores(f"{valor:,.{casas}f}") + "%"
```

> A regra de `formatar_numero` é a mesma de `formatarNumero` do frontend (M1.1). Atenção: `0.0012345` em binário é `0,00123449…` e arredonda para `0,001234`; por isso o teste usa `0.0012346`.

`app/compartilhado/textos.py`
```python
"""Utilitários de texto sem regra de negócio (spec 16)."""

import re
import unicodedata

_ESPACOS = re.compile(r"\s+")


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sem acento e com espaços colapsados: '  São  Paulo ' → 'sao paulo'."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return _ESPACOS.sub(" ", sem_acento).strip().lower()


def pluralizar(quantidade: int, singular: str, plural: str) -> str:
    """Escolhe singular ou plural pela quantidade (1 linha · 3 linhas)."""
    return singular if quantidade == 1 else plural


def juntar_lista(itens: list[str]) -> str:
    """Junta itens em português: 'a', 'a e b', 'a, b e c'."""
    if len(itens) <= 1:
        return "".join(itens)
    return f"{', '.join(itens[:-1])} e {itens[-1]}"
```

`app/compartilhado/series.py`
```python
"""Helpers de pandas sem regra de negócio (conversão numérica, inteiros, casas decimais)."""

import numpy as np
import pandas as pd

MAX_CASAS_DECIMAIS = 6
_TOLERANCIA = 1e-9


def converter_para_numero(serie: pd.Series, decimal: str | None = ".") -> pd.Series:
    """Converte para float; o que não for número vira NaN. Com decimal ',' o '.' é milhar."""
    if pd.api.types.is_bool_dtype(serie):
        return pd.Series(np.nan, index=serie.index, dtype="float64")
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype("float64")
    texto = serie.astype("string").str.strip()
    if decimal == ",":
        texto = texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce").astype("float64")


def proporcao_numerica(serie: pd.Series, decimal: str | None = ".") -> float:
    """Fração dos valores não faltantes que viram número (0 se não houver valores)."""
    validos = serie.dropna()
    if validos.empty:
        return 0.0
    return float(converter_para_numero(validos, decimal).notna().mean())


def eh_inteira(numeros: pd.Series) -> bool:
    """Todos os valores válidos são inteiros (ex.: 3.0 conta como inteiro)."""
    valores = numeros.dropna().to_numpy(dtype="float64")
    return bool(np.all(np.abs(valores - np.round(valores)) < _TOLERANCIA))


def casas_decimais(numeros: pd.Series) -> int:
    """Menor número de casas decimais que representa todos os valores (máx. 6)."""
    valores = numeros.dropna().to_numpy(dtype="float64")
    for casas in range(MAX_CASAS_DECIMAIS):
        escalados = valores * 10**casas
        if np.all(np.abs(escalados - np.round(escalados)) < _TOLERANCIA * 10**casas):
            return casas
    return MAX_CASAS_DECIMAIS
```

**Passo 4: rodar e ver passar**
`pytest tests/compartilhado -v --no-cov` → 29 passed

**Passo 5: commit**
```bash
git add app/compartilhado tests/compartilhado
git commit -m "feat(compartilhado): adiciona tipos de variável, formatação pt-BR e helpers de séries"
```

---

### Tarefa 2: configuração e erro 413

**Arquivos:**
- Modificar: `backend/app/core/config.py`, `backend/app/core/erros.py`
- Teste: `backend/tests/core/test_config.py`

**Passo 1: atualizar o teste (falha)**
```python
import pytest

from app.core.config import Configuracao


def test_valores_padrao_seguem_as_specs() -> None:
    config = Configuracao()

    assert config.limite_arquivo_mb == 50
    assert config.limite_arquivo_bytes == 50 * 1024 * 1024
    assert config.max_datasets == 20
    assert config.limiar_discreta == 30
    assert config.limiar_unicos_identificador == 0.95
    assert config.limiar_numerico == 0.9
    assert config.tamanho_previa == 20
    assert "http://localhost:5173" in config.cors_origens


def test_exemplo_padrao_existe_no_repositorio() -> None:
    config = Configuracao()

    assert (config.pasta_exemplos / config.arquivo_exemplo).is_file()


def test_variavel_de_ambiente_sobrescreve_padrao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGD_LIMIAR_DISCRETA", "40")

    assert Configuracao().limiar_discreta == 40
```

**Passo 2: rodar e ver falhar** — `pytest tests/core/test_config.py --no-cov` → FAIL (`AttributeError: limite_arquivo_bytes`)

**Passo 3: implementar**

`app/core/config.py` (substituir)
```python
"""Configuração da aplicação, lida de variáveis de ambiente com prefixo AGD_."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[3]


class Configuracao(BaseSettings):
    """Parâmetros globais; limiares documentados em docs/specs/02-tipos.md e ADR 0004."""

    model_config = SettingsConfigDict(env_prefix="AGD_", env_file=".env", extra="ignore")

    nome_app: str = "Analisador e Gerador de Dados"
    versao: str = "0.0.0"
    cors_origens: list[str] = ["http://localhost:5173"]
    limite_arquivo_mb: int = 50
    max_datasets: int = 20
    limiar_discreta: int = 30
    limiar_unicos_identificador: float = 0.95
    limiar_numerico: float = 0.9
    tamanho_previa: int = 20
    pasta_exemplos: Path = RAIZ_REPOSITORIO / "dados-exemplo"
    arquivo_exemplo: str = "pesquisa_saude.txt"

    @property
    def limite_arquivo_bytes(self) -> int:
        return self.limite_arquivo_mb * 1024 * 1024


@lru_cache
def obter_configuracao() -> Configuracao:
    """Instância única, injetada via Depends."""
    return Configuracao()
```

> `pasta_exemplos` aponta para `dados-exemplo/` na raiz do repositório (criada no commit dos planos, junto com `backend/scripts/gerar_exemplos.py`). Funciona tanto rodando de `backend/` quanto pelo `launch.json` (cwd na raiz).

`app/core/erros.py` — acrescentar no fim:
```python


class ArquivoGrande(ErroAplicacao):
    status = HTTPStatus.REQUEST_ENTITY_TOO_LARGE
```

**Passo 4: rodar e ver passar** — `pytest tests/core --no-cov` → todos passam

**Passo 5: commit**
```bash
git add app/core tests/core
git commit -m "feat(core): adiciona limiar numérico, prévia, pasta de exemplos e erro 413"
```

---

### Tarefa 3: modelos e erros do domínio

Value objects usados pelas tarefas seguintes. Sem teste próprio: são cobertos pelos testes das Tarefas 4–10.

**Arquivos:**
- Criar: `backend/app/dominios/datasets/modelos.py`, `backend/app/dominios/datasets/erros.py`

`app/dominios/datasets/modelos.py`
```python
"""Value objects do domínio datasets (specs 01–03, ADR 0004)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from app.compartilhado.tipos import OrigemTipo, TipoVariavel

type Celula = str | float | int | bool | None


@dataclass(frozen=True, slots=True)
class OpcoesLeitura:
    """Escolhas do usuário que sobrescrevem a detecção automática (spec 01)."""

    separador: str | None = None
    decimal: str | None = None
    codificacao: str | None = None
    aba: str | None = None
    tem_cabecalho: bool | None = None


@dataclass(frozen=True, slots=True)
class Aviso:
    codigo: str
    mensagem: str


@dataclass(frozen=True, slots=True)
class MetadadosLeitura:
    formato: str
    codificacao: str | None
    separador: str | None
    decimal: str | None
    tem_cabecalho: bool | None
    n_linhas: int
    n_colunas: int
    abas: tuple[str, ...] = ()
    avisos: tuple[Aviso, ...] = ()
    motivos: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, eq=False)
class ResultadoLeitura:
    dados: pd.DataFrame
    metadados: MetadadosLeitura


@dataclass(frozen=True, slots=True)
class TipoColuna:
    """Resultado da classificação de uma coluna (spec 02)."""

    coluna: str
    tipo: TipoVariavel
    motivo: str
    origem: OrigemTipo
    n_validos: int
    n_faltantes: int
    n_distintos: int
    exemplos: tuple[str, ...] = ()
    categorias_ordem: tuple[str, ...] = ()
    contagens: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EntradaLog:
    """Uma ação de limpeza registrada para o usuário e para o relatório (spec 03)."""

    problema: str
    acao: str
    coluna: str | None
    linhas_afetadas: tuple[int, ...]
    antes_exemplo: str
    depois_exemplo: str
    quando: datetime
    frase: str


@dataclass(frozen=True, slots=True)
class LinhaDados:
    linha: int
    valores: Mapping[str, Celula]


@dataclass(slots=True, eq=False)
class Dataset:
    """Estado de um conjunto importado: original intocado e atual após a limpeza (ADR 0004)."""

    id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    original: pd.DataFrame
    atual: pd.DataFrame
    tipos: dict[str, TipoColuna]
    log_limpeza: list[EntradaLog] = field(default_factory=list)
    criado_em: datetime = field(default_factory=datetime.now)
```

> `eq=False` nas dataclasses com `DataFrame`: comparar DataFrames com `==` é ambíguo. `EntradaLog` já nasce aqui porque `ResumoDataset.log_limpeza` faz parte do contrato do M1.2; quem preenche o log é o M1.3.

`app/dominios/datasets/erros.py`
```python
"""Erros do domínio datasets com textos da spec 01/02/17 (formato da spec 16)."""

from app.core.erros import ArquivoGrande, EntradaInvalida, NaoEncontrado


def arquivo_vazio() -> EntradaInvalida:
    return EntradaInvalida(
        "ARQUIVO_VAZIO", "O arquivo está vazio.", "Confira se escolheu o arquivo certo."
    )


def formato_nao_suportado(nome_arquivo: str) -> EntradaInvalida:
    return EntradaInvalida(
        "FORMATO_NAO_SUPORTADO",
        f"Não conseguimos ler este arquivo: {nome_arquivo}. "
        "Este tipo de arquivo não é aceito. Use TXT, CSV, TSV, XLSX ou JSON.",
        "Abra o arquivo na planilha de origem e salve como CSV ou XLSX, depois envie de novo.",
    )


def arquivo_grande(limite_mb: int) -> ArquivoGrande:
    return ArquivoGrande(
        "ARQUIVO_GRANDE",
        f"O arquivo passa de {limite_mb} MB.",
        "Envie só as colunas e linhas que vai analisar.",
    )


def json_invalido() -> EntradaInvalida:
    return EntradaInvalida(
        "JSON_INVALIDO",
        "Não conseguimos ler este JSON. Verifique se é uma lista de registros.",
        'Use o formato [{"coluna": valor}, …] ou {"coluna": [valores]}.',
    )


def arquivo_ilegivel() -> EntradaInvalida:
    return EntradaInvalida(
        "ARQUIVO_ILEGIVEL",
        "Não conseguimos ler este arquivo como tabela.",
        "Escolha outro separador ou confira se todas as linhas têm o mesmo número de colunas.",
    )


def dataset_nao_encontrado() -> NaoEncontrado:
    return NaoEncontrado(
        "DATASET_NAO_ENCONTRADO", "Sua sessão expirou.", "Envie o arquivo novamente."
    )


def coluna_nao_encontrada(coluna: str) -> NaoEncontrado:
    return NaoEncontrado(
        "COLUNA_NAO_ENCONTRADA",
        f"Não encontramos a coluna {coluna}.",
        "Ela pode ter sido renomeada — recarregue a página.",
    )


def tipo_incompativel(mensagem: str) -> EntradaInvalida:
    return EntradaInvalida("TIPO_INCOMPATIVEL", mensagem, "Escolha outro tipo para esta coluna.")


def categorias_incompletas(faltando: list[str]) -> EntradaInvalida:
    return EntradaInvalida(
        "CATEGORIAS_INCOMPLETAS",
        f"Faltam categorias na ordem: {', '.join(faltando)}.",
        "Inclua todas as categorias da coluna na ordem.",
    )
```

**Conferir:** `ruff check . && mypy app` → sem erros.

**Commit:**
```bash
git add app/dominios/datasets/modelos.py app/dominios/datasets/erros.py
git commit -m "feat(datasets): adiciona modelos do domínio e erros com mensagens da spec 01"
```

---

### Tarefa 4: detecção automática (spec 01)

**Arquivos:**
- Criar: `backend/app/dominios/datasets/deteccao.py`
- Teste: `backend/tests/dominios/__init__.py`, `backend/tests/dominios/datasets/__init__.py` (vazios), `backend/tests/dominios/datasets/test_deteccao.py`

**Regras implementadas** (registrar os ajustes na spec 01 na Tarefa 11):
- Codificação: BOM → `utf-8-sig`; senão `utf-8` → `cp1252` → `latin-1` (latin-1 nunca falha, é o último recurso).
- Separador: entre `; , \t |` e "espaços" (2+ espaços), vence o que aparece **o mesmo número de vezes em ≥ 90% das linhas** e gera mais colunas. É o desempate da spec 01 aplicado direto, sem `csv.Sniffer` (o Sniffer confunde a vírgula decimal de `1,62;58,2` com separador).
- Decimal: olha só os números que têm `,` ou `.`; vírgula se ≥ 80% casam o padrão `1.234,5`. Sem números decimais, vale a regra da spec (`;` → vírgula). Isso evita ler `1.72` como `172` num arquivo com `;` e ponto decimal.
- Cabeçalho: há cabeçalho se a 1ª linha tem só textos, todos diferentes, e nenhum deles aparece como valor na própria coluna. Substitui o `Sniffer.has_header`, que erra em tabelas só de texto.

**Passo 1: escrever os testes (falham)**
```python
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.deteccao import (
    SEPARADOR_ESPACOS,
    decodificar,
    detectar_cabecalho,
    detectar_decimal,
    detectar_formato,
    detectar_separador,
    linhas_amostra,
)


@pytest.mark.parametrize(
    ("nome", "formato"),
    [
        ("dados.TXT", "txt"),
        ("a.csv", "csv"),
        ("a.tsv", "tsv"),
        ("a.xlsx", "xlsx"),
        ("a.json", "json"),
    ],
)
def test_formato_vem_da_extensao(nome: str, formato: str) -> None:
    assert detectar_formato(nome).valor == formato


def test_extensao_desconhecida_e_recusada() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        detectar_formato("relatorio_final.pdf")

    assert erro.value.codigo == "FORMATO_NAO_SUPORTADO"
    assert "relatorio_final.pdf" in erro.value.mensagem


@pytest.mark.parametrize(
    ("conteudo", "codificacao"),
    [
        ("Goiânia".encode("utf-8-sig"), "utf-8-sig"),
        ("Goiânia".encode(), "utf-8"),
        ("Goiânia – ok".encode("cp1252"), "cp1252"),
        (b"Goi\x81nia", "latin-1"),
    ],
)
def test_codificacao_segue_a_ordem_da_spec(conteudo: bytes, codificacao: str) -> None:
    _, detectada = decodificar(conteudo, None)

    assert detectada.valor == codificacao


def test_codificacao_escolhida_pelo_usuario_vence() -> None:
    texto, detectada = decodificar("Goiânia".encode("latin-1"), "latin-1")

    assert texto == "Goiânia"
    assert detectada.motivo == "Escolhida por você."


def test_motivo_da_codificacao_cita_uma_palavra_acentuada() -> None:
    _, detectada = decodificar("cidade\nGoiânia\n".encode(), None)

    assert detectada.motivo == "Acentos lidos sem erro (Goiânia)."


@pytest.mark.parametrize(
    ("texto", "separador"),
    [
        ("a;b;c\n1,5;2;3\n4;5,5;6\n", ";"),
        ("a,b\n1.5,2\n3,4\n", ","),
        ("a\tb\n1\t2\n", "\t"),
        ("a|b\n1|2\n", "|"),
        ("nome    idade\nAna     34\nBruno   27\n", SEPARADOR_ESPACOS),
    ],
)
def test_separador_e_o_que_se_repete_em_todas_as_linhas(texto: str, separador: str) -> None:
    detectado = detectar_separador(linhas_amostra(texto))

    assert detectado.valor == separador


def test_ponto_e_virgula_vence_a_virgula_decimal() -> None:
    texto = "id;altura;peso\n1;1,62;58,2\n2;1,78;\n3;1,58;63,0\n"

    detectado = detectar_separador(linhas_amostra(texto))

    assert detectado.valor == ";"
    assert detectado.motivo == "Aparece 2 vezes em todas as linhas."


def test_sem_separador_le_uma_coluna() -> None:
    assert detectar_separador(["valor", "1", "2"]).valor is None


@pytest.mark.parametrize(
    ("linhas", "separador", "decimal"),
    [
        (["a;b", "1,62;58,2", "1.234,5;7"], ";", ","),
        (["a,b", "1.62,58.2"], ",", "."),
        (["a;b", "1;2"], ";", ","),
        (["a,b", "1,2"], ",", "."),
    ],
)
def test_decimal_detectado(linhas: list[str], separador: str, decimal: str) -> None:
    assert detectar_decimal(linhas, separador).valor == decimal


def test_motivo_do_decimal_mostra_exemplos() -> None:
    detectado = detectar_decimal(["a;b", "1,72;68,4"], ";")

    assert detectado.motivo == "Valores como 1,72 e 68,4."


@pytest.mark.parametrize(
    ("linhas", "tem_cabecalho"),
    [
        (["nome;idade", "Ana;34", "Bruno;27"], True),
        (["10;1,5", "20;2,5"], False),
        (["F;bom", "M;ruim", "F;bom"], False),
        (["sexo;satisfacao", "F;bom", "M;ruim"], True),
        (["só uma linha"], True),
    ],
)
def test_cabecalho_detectado(linhas: list[str], tem_cabecalho: bool) -> None:
    assert detectar_cabecalho(linhas, ";").valor is tem_cabecalho
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_deteccao.py --no-cov` → FAIL (`ModuleNotFoundError`)

**Passo 3: implementar `app/dominios/datasets/deteccao.py`**
```python
"""Detecção automática de formato, codificação, separador, decimal e cabeçalho (spec 01)."""

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import PurePath

from app.dominios.datasets import erros

FORMATOS = {".txt": "txt", ".csv": "csv", ".tsv": "tsv", ".xlsx": "xlsx", ".json": "json"}
CODIFICACOES = ("utf-8", "cp1252")
CODIFICACAO_FINAL = "latin-1"  # decodifica qualquer byte; é o último recurso
BOM_UTF8 = b"\xef\xbb\xbf"
LINHAS_AMOSTRA = 50
MIN_LINHAS_CABECALHO = 2
FRACAO_LINHAS_CONSTANTE = 0.9
FRACAO_DECIMAL_VIRGULA = 0.8
SEM_SEPARADOR = "\x1f"  # caractere que não aparece em texto: a linha inteira vira uma célula
SEPARADOR_ESPACOS = r"\s{2,}"
CANDIDATOS_SEPARADOR = (";", ",", "\t", "|", SEPARADOR_ESPACOS)
_NUMERO = re.compile(r"^-?[\d.,]*\d[\d.,]*$")
_NUMERO_VIRGULA = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+,\d+$")
_PALAVRA = re.compile(r"\w+")


@dataclass(frozen=True, slots=True)
class Deteccao[T]:
    """Valor detectado (ou escolhido) e o motivo mostrado na tela 1a (D53)."""

    valor: T
    motivo: str


def detectar_formato(nome_arquivo: str) -> Deteccao[str]:
    """Formato pela extensão do arquivo."""
    formato = FORMATOS.get(PurePath(nome_arquivo).suffix.lower())
    if formato is None:
        raise erros.formato_nao_suportado(nome_arquivo)
    return Deteccao(formato, "Pela extensão do arquivo.")


def _motivo_codificacao(texto: str) -> str:
    acentuada = next((p for p in _PALAVRA.findall(texto) if not p.isascii()), None)
    if acentuada is None:
        return "O texto não tem acentos."
    return f"Acentos lidos sem erro ({acentuada})."


def decodificar(conteudo: bytes, codificacao: str | None) -> tuple[str, Deteccao[str]]:
    """Texto e codificação; tenta utf-8-sig → utf-8 → cp1252 → latin-1."""
    if codificacao:
        texto = conteudo.decode(codificacao, errors="replace")
        return texto, Deteccao(codificacao, "Escolhida por você.")
    if conteudo.startswith(BOM_UTF8):
        texto = conteudo.decode("utf-8-sig", errors="replace")
        return texto, Deteccao("utf-8-sig", "O arquivo começa com a marca do UTF-8.")
    for candidata in CODIFICACOES:
        try:
            texto = conteudo.decode(candidata)
        except UnicodeDecodeError:
            continue
        return texto, Deteccao(candidata, _motivo_codificacao(texto))
    texto = conteudo.decode(CODIFICACAO_FINAL)
    return texto, Deteccao(CODIFICACAO_FINAL, _motivo_codificacao(texto))


def linhas_amostra(texto: str) -> list[str]:
    """Primeiras linhas não vazias, usadas nas detecções."""
    return [linha for linha in texto.splitlines() if linha.strip()][:LINHAS_AMOSTRA]


def quebrar(linha: str, separador: str | None) -> list[str]:
    """Células de uma linha (sem tratar aspas; serve só para as detecções)."""
    if separador == SEPARADOR_ESPACOS:
        return re.split(SEPARADOR_ESPACOS, linha.strip())
    return linha.split(separador or SEM_SEPARADOR)


def _contagem_constante(linhas: list[str], separador: str) -> int:
    """Nº de separadores por linha se ele se repete em ≥ 90% das linhas; senão 0."""
    contagens = Counter(len(quebrar(linha, separador)) - 1 for linha in linhas)
    contagem, vezes = contagens.most_common(1)[0]
    return contagem if vezes >= FRACAO_LINHAS_CONSTANTE * len(linhas) else 0


def detectar_separador(linhas: list[str]) -> Deteccao[str | None]:
    """O candidato que aparece o mesmo número de vezes nas linhas e gera mais colunas."""
    if not linhas:
        return Deteccao(None, "Não há linhas para analisar.")
    contagens = {c: _contagem_constante(linhas, c) for c in CANDIDATOS_SEPARADOR}
    melhor = max(CANDIDATOS_SEPARADOR, key=lambda c: contagens[c])
    if contagens[melhor] == 0:
        return Deteccao(None, "Não encontramos um separador; lemos uma coluna só.")
    return Deteccao(melhor, f"Aparece {contagens[melhor]} vezes em todas as linhas.")


def _tokens_decimais(linhas: list[str], separador: str | None) -> list[str]:
    celulas = (c.strip() for linha in linhas for c in quebrar(linha, separador))
    return [c for c in celulas if _NUMERO.match(c) and ("," in c or "." in c)]


def detectar_decimal(linhas: list[str], separador: str | None) -> Deteccao[str]:
    """Vírgula se ≥ 80% dos números com separador seguem o padrão 1.234,5; senão ponto."""
    tokens = _tokens_decimais(linhas, separador)
    if not tokens:
        decimal = "," if separador == ";" else "."
        return Deteccao(decimal, "Não há números com casas decimais.")
    com_virgula = [t for t in tokens if _NUMERO_VIRGULA.match(t)]
    decimal = "," if len(com_virgula) >= FRACAO_DECIMAL_VIRGULA * len(tokens) else "."
    exemplos = [t for t in tokens if decimal in t][:2] or tokens[:2]
    return Deteccao(decimal, f"Valores como {' e '.join(exemplos)}.")


def _eh_numero(celula: str) -> bool:
    return bool(_NUMERO.match(celula.strip()))


def _so_nomes_unicos(celulas: list[str]) -> bool:
    return all(c and not _eh_numero(c) for c in celulas) and len(set(celulas)) == len(celulas)


def _nome_se_repete(nomes: list[str], resto: list[list[str]]) -> bool:
    """Algum nome da 1ª linha aparece como valor na própria coluna (então é dado)."""
    return any(
        nome in {linha[i] for linha in resto if i < len(linha)} for i, nome in enumerate(nomes)
    )


def detectar_cabecalho(linhas: list[str], separador: str | None) -> Deteccao[bool]:
    """Há cabeçalho se a 1ª linha tem só textos únicos que não se repetem nas colunas abaixo."""
    if len(linhas) < MIN_LINHAS_CABECALHO:
        return Deteccao(True, "O arquivo só tem uma linha.")
    tabela = [[c.strip() for c in quebrar(linha, separador)] for linha in linhas]
    primeira, resto = tabela[0], tabela[1:]
    if _so_nomes_unicos(primeira) and not _nome_se_repete(primeira, resto):
        return Deteccao(True, "A 1ª linha tem só nomes, sem números.")
    return Deteccao(False, "A 1ª linha parece ser de dados; criamos os nomes col_1, col_2…")
```

**Passo 4: rodar e ver passar** — `pytest tests/dominios/datasets/test_deteccao.py -v --no-cov` → todos passam

**Passo 5: commit**
```bash
git add app/dominios/datasets/deteccao.py tests/dominios
git commit -m "feat(datasets): detecta formato, codificação, separador, decimal e cabeçalho"
```

---

### Tarefa 5: leitura por formato (spec 01)

**Arquivos:**
- Criar: `backend/app/dominios/datasets/leitura.py`
- Criar fixtures em `backend/tests/fixtures/` (conteúdo abaixo, LF, UTF-8)
- Teste: `backend/tests/dominios/datasets/test_leitura.py`

**Passo 1: criar as fixtures**

`tests/fixtures/ponto_e_virgula.txt`
```text
nome;altura;peso
Ana;1,62;58,2
Bruno;1,78;1.079,6
Carla;1,58;NA
```

`tests/fixtures/virgula.csv`
```text
cidade,valor,quantidade
Goiania,1.5,3
Anapolis,2.25,4
Trindade,3.0,5
```

`tests/fixtures/tabulacao.tsv` (as separações são **tabulações** reais; crie com `printf 'produto\tpreco\tunidades\nCaneta\t2.5\t10\nLapis\t1.25\t20\n' > tests/fixtures/tabulacao.tsv`)
```text
produto	preco	unidades
Caneta	2.5	10
Lapis	1.25	20
```

`tests/fixtures/sem_cabecalho.txt`
```text
10;1,5;A
20;2,5;B
30;3,5;C
```

`tests/fixtures/aninhado.json`
```json
[{"nome": "Ana", "endereco": {"cidade": "Goiânia", "uf": "GO"}, "idade": 34},
 {"nome": "Bruno", "endereco": {"cidade": "Anápolis", "uf": "GO"}, "idade": 27}]
```

`tests/fixtures/colunas.json`
```json
{"x": [1, 2, 3], "y": ["a", "b", "c"]}
```

O XLSX e o latin-1 são montados dentro dos testes (binário não entra como fixture de texto).

**Passo 2: escrever os testes (falham)**
```python
import io
import math
from pathlib import Path

import pandas as pd
import pytest

from app.core.erros import EntradaInvalida
from app.dominios.datasets.leitura import ler_arquivo, padronizar_nomes
from app.dominios.datasets.modelos import OpcoesLeitura, ResultadoLeitura

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
SEM_OPCOES = OpcoesLeitura()


def _ler(nome: str, opcoes: OpcoesLeitura = SEM_OPCOES) -> ResultadoLeitura:
    return ler_arquivo((FIXTURES / nome).read_bytes(), nome, opcoes)


def test_txt_com_ponto_e_virgula_e_virgula_decimal() -> None:
    resultado = _ler("ponto_e_virgula.txt")

    assert resultado.metadados.separador == ";"
    assert resultado.metadados.decimal == ","
    assert resultado.dados["altura"].tolist() == [1.62, 1.78, 1.58]
    assert resultado.dados["peso"].iloc[1] == 1079.6
    assert math.isnan(resultado.dados["peso"].iloc[2])


def test_csv_com_virgula_e_ponto_decimal() -> None:
    resultado = _ler("virgula.csv")

    assert resultado.metadados.formato == "csv"
    assert resultado.dados["valor"].tolist() == [1.5, 2.25, 3.0]


def test_tsv_usa_tabulacao() -> None:
    resultado = _ler("tabulacao.tsv")

    assert resultado.metadados.separador == "\t"
    assert list(resultado.dados.columns) == ["produto", "preco", "unidades"]


def test_sem_cabecalho_cria_nomes_col_n() -> None:
    resultado = _ler("sem_cabecalho.txt")

    assert resultado.metadados.tem_cabecalho is False
    assert list(resultado.dados.columns) == ["col_1", "col_2", "col_3"]
    assert len(resultado.dados) == 3


def test_latin1_com_acentos_e_lido_pela_cp1252() -> None:
    # cp1252 vem antes de latin-1 na spec e decodifica os acentos do português igual.
    conteudo = "cidade;valor\nGoiânia;1,5\nAnápolis;2,5\n".encode("latin-1")

    resultado = ler_arquivo(conteudo, "dados.txt", SEM_OPCOES)

    assert resultado.metadados.codificacao == "cp1252"
    assert resultado.dados["cidade"].tolist() == ["Goiânia", "Anápolis"]


def test_json_aninhado_vira_colunas_com_ponto() -> None:
    resultado = _ler("aninhado.json")

    assert "endereco.cidade" in resultado.dados.columns
    assert resultado.dados["idade"].tolist() == [34, 27]


def test_json_de_colunas() -> None:
    assert _ler("colunas.json").dados.shape == (3, 2)


@pytest.mark.parametrize("conteudo", [b"{nao e json", b"[1, 2, 3]", b'{"a": 1}'])
def test_json_invalido(conteudo: bytes) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(conteudo, "dados.json", SEM_OPCOES)

    assert erro.value.codigo == "JSON_INVALIDO"


def test_xlsx_le_a_primeira_aba_e_lista_as_abas() -> None:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as planilha:
        pd.DataFrame({"x": [1, 2], "y": ["a", "b"]}).to_excel(
            planilha, sheet_name="dados", index=False
        )
        pd.DataFrame({"z": [3]}).to_excel(planilha, sheet_name="outra", index=False)

    resultado = ler_arquivo(buffer.getvalue(), "dados.xlsx", SEM_OPCOES)

    assert resultado.metadados.abas == ("dados", "outra")
    assert resultado.dados["x"].tolist() == [1, 2]


def test_xlsx_escolhe_a_aba() -> None:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as planilha:
        pd.DataFrame({"x": [1]}).to_excel(planilha, sheet_name="dados", index=False)
        pd.DataFrame({"z": [3, 4]}).to_excel(planilha, sheet_name="outra", index=False)

    resultado = ler_arquivo(buffer.getvalue(), "dados.xlsx", OpcoesLeitura(aba="outra"))

    assert list(resultado.dados.columns) == ["z"]


def test_xlsx_corrompido() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(b"isto nao e uma planilha", "dados.xlsx", SEM_OPCOES)

    assert erro.value.codigo == "ARQUIVO_ILEGIVEL"


def test_opcoes_do_usuario_sobrescrevem_a_deteccao() -> None:
    opcoes = OpcoesLeitura(separador=",", decimal=".", tem_cabecalho=True)

    resultado = ler_arquivo(b"a,b\n1.5,2\n", "dados.txt", opcoes)

    assert resultado.metadados.motivos["separador"] == "Escolhido por você."
    assert resultado.dados["a"].tolist() == [1.5]


@pytest.mark.parametrize("conteudo", [b"", b"   \n  "])
def test_arquivo_vazio(conteudo: bytes) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(conteudo, "dados.csv", SEM_OPCOES)

    assert erro.value.codigo == "ARQUIVO_VAZIO"


def test_so_cabecalho_tambem_e_vazio() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ler_arquivo(b"a;b;c\n", "dados.txt", OpcoesLeitura(tem_cabecalho=True))

    assert erro.value.codigo == "ARQUIVO_VAZIO"


def test_uma_coluna_com_separador_suspeito_gera_aviso() -> None:
    opcoes = OpcoesLeitura(separador="|")

    resultado = ler_arquivo(b"a;b\n1;2\n3;4\n", "dados.txt", opcoes)

    assert [a.codigo for a in resultado.metadados.avisos] == ["UMA_COLUNA"]


@pytest.mark.parametrize("marcador", ["NA", "N/A", "NaN", "null", "None", "-", "?", "—", " "])
def test_marcadores_de_faltante(marcador: str) -> None:
    conteudo = f"cidade;n\nGoiânia;1\n{marcador};2\n".encode()

    resultado = ler_arquivo(conteudo, "dados.txt", SEM_OPCOES)

    assert resultado.dados["cidade"].isna().sum() == 1


def test_indice_e_o_numero_da_linha() -> None:
    assert _ler("virgula.csv").dados.index.tolist() == [1, 2, 3]


@pytest.mark.parametrize(
    ("nomes", "esperado"),
    [
        ([" idade ", "peso  kg"], ["idade", "peso kg"]),
        (["a", "a", "a"], ["a", "a_2", "a_3"]),
        (["", None], ["col_1", "col_2"]),
    ],
)
def test_padronizar_nomes(nomes: list[object], esperado: list[str]) -> None:
    assert padronizar_nomes(nomes) == esperado


def test_exemplo_pesquisa_saude() -> None:
    caminho = Path(__file__).resolve().parents[4] / "dados-exemplo" / "pesquisa_saude.txt"

    resultado = ler_arquivo(caminho.read_bytes(), caminho.name, SEM_OPCOES)

    assert (resultado.metadados.n_linhas, resultado.metadados.n_colunas) == (230, 8)
    assert resultado.metadados.motivos["separador"] == "Aparece 7 vezes em todas as linhas."
```

**Passo 3: rodar e ver falhar** — `pytest tests/dominios/datasets/test_leitura.py --no-cov` → FAIL (`ModuleNotFoundError`)

**Passo 4: implementar `app/dominios/datasets/leitura.py`**
```python
"""Leitura de TXT/CSV/TSV/XLSX/JSON para DataFrame + metadados (spec 01)."""

import csv
import io
import json
import re
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field

import pandas as pd

from app.dominios.datasets import erros
from app.dominios.datasets.deteccao import (
    SEM_SEPARADOR,
    SEPARADOR_ESPACOS,
    Deteccao,
    decodificar,
    detectar_cabecalho,
    detectar_decimal,
    detectar_formato,
    detectar_separador,
    linhas_amostra,
)
from app.dominios.datasets.modelos import Aviso, MetadadosLeitura, OpcoesLeitura, ResultadoLeitura

VALORES_FALTANTES = ("", "NA", "N/A", "NaN", "null", "None", "-", "?", "—")
SEPARADORES_SUSPEITOS = (";", ",", "\t")
NAO_SE_APLICA = "Não se aplica a este formato."
ESCOLHIDO = "Escolhido por você."
_ESPACOS = re.compile(r"\s+")


@dataclass(frozen=True, slots=True, eq=False)
class _LeituraBruta:
    dados: pd.DataFrame
    codificacao: str | None = None
    separador: str | None = None
    decimal: str | None = None
    tem_cabecalho: bool | None = None
    abas: tuple[str, ...] = ()
    motivos: dict[str, str] = field(default_factory=dict)
    amostra: tuple[str, ...] = ()


type Leitor = Callable[[bytes, str, OpcoesLeitura], _LeituraBruta]


def _ou_detectar[T](escolhido: T | None, detectar: Callable[[], Deteccao[T]]) -> Deteccao[T]:
    return detectar() if escolhido is None else Deteccao(escolhido, ESCOLHIDO)


def padronizar_nomes(nomes: list[object]) -> list[str]:
    """strip, espaços múltiplos → um, vazios → col_N e duplicados com sufixo _2, _3…"""
    resultado: list[str] = []
    for posicao, nome in enumerate(nomes, start=1):
        base = _ESPACOS.sub(" ", str(nome)).strip() if nome is not None else ""
        base = base if base and base.lower() != "nan" else f"col_{posicao}"
        candidato, sufixo = base, 2
        while candidato in resultado:
            candidato, sufixo = f"{base}_{sufixo}", sufixo + 1
        resultado.append(candidato)
    return resultado


def _nomes_do_cabecalho(texto: str, separador: str | None) -> list[object]:
    primeira = next(linha for linha in texto.splitlines() if linha.strip())
    if separador == SEPARADOR_ESPACOS:
        return list(re.split(SEPARADOR_ESPACOS, primeira.strip()))
    return list(next(csv.reader([primeira], delimiter=separador or SEM_SEPARADOR)))


def _ler_csv(texto: str, separador: str | None, decimal: str, tem_cabecalho: bool) -> pd.DataFrame:
    nomes = padronizar_nomes(_nomes_do_cabecalho(texto, separador)) if tem_cabecalho else None
    try:
        dados = pd.read_csv(
            io.StringIO(texto),
            sep=separador or SEM_SEPARADOR,
            engine="python" if separador == SEPARADOR_ESPACOS else "c",
            decimal=decimal,
            thousands="." if decimal == "," else None,
            header=None,
            skiprows=1 if tem_cabecalho else 0,
            names=nomes,
            index_col=False,
            na_values=list(VALORES_FALTANTES),
            keep_default_na=False,
            skipinitialspace=True,
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as erro:
        raise erros.arquivo_ilegivel() from erro
    if nomes is None:
        dados.columns = pd.Index(padronizar_nomes([None] * dados.shape[1]))
    return dados


def _separador(opcoes: OpcoesLeitura, formato: str, amostra: list[str]) -> Deteccao[str | None]:
    if opcoes.separador is not None:
        return Deteccao(opcoes.separador, ESCOLHIDO)
    if formato == "tsv":
        return Deteccao("\t", "Arquivos TSV usam tabulação.")
    return detectar_separador(amostra)


def _ler_texto(conteudo: bytes, formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    texto, codificacao = decodificar(conteudo, opcoes.codificacao)
    amostra = linhas_amostra(texto)
    separador = _separador(opcoes, formato, amostra)
    decimal = _ou_detectar(opcoes.decimal, lambda: detectar_decimal(amostra, separador.valor))
    cabecalho = _ou_detectar(
        opcoes.tem_cabecalho, lambda: detectar_cabecalho(amostra, separador.valor)
    )
    dados = _ler_csv(texto, separador.valor, decimal.valor, cabecalho.valor)
    return _LeituraBruta(
        dados=dados,
        codificacao=codificacao.valor,
        separador=separador.valor,
        decimal=decimal.valor,
        tem_cabecalho=cabecalho.valor,
        motivos={
            "codificacao": codificacao.motivo,
            "separador": separador.motivo,
            "decimal": decimal.motivo,
            "cabecalho": cabecalho.motivo,
        },
        amostra=tuple(amostra),
    )


def _ler_xlsx(conteudo: bytes, _formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    try:
        planilha = pd.ExcelFile(io.BytesIO(conteudo), engine="openpyxl")
        abas = tuple(str(nome) for nome in planilha.sheet_names)
        aba = opcoes.aba or abas[0]
        bruto = planilha.parse(aba, header=None)
    except (ValueError, KeyError, zipfile.BadZipFile, OSError) as erro:
        raise erros.arquivo_ilegivel() from erro
    tem_cabecalho = opcoes.tem_cabecalho is not False
    dados = bruto.iloc[1:] if tem_cabecalho else bruto
    nomes = list(bruto.iloc[0]) if tem_cabecalho else [None] * bruto.shape[1]
    dados = dados.set_axis(padronizar_nomes(nomes), axis="columns").infer_objects()
    motivo_cabecalho = ESCOLHIDO if opcoes.tem_cabecalho is not None else f"1ª linha da aba {aba}."
    return _LeituraBruta(
        dados=dados,
        tem_cabecalho=tem_cabecalho,
        abas=abas,
        motivos={"cabecalho": motivo_cabecalho},
    )


def _tabela_json(dados: object) -> pd.DataFrame:
    if isinstance(dados, list) and dados and all(isinstance(r, dict) for r in dados):
        return pd.json_normalize(dados)
    if isinstance(dados, dict) and dados and all(isinstance(v, list) for v in dados.values()):
        try:
            return pd.DataFrame(dados)
        except ValueError as erro:
            raise erros.json_invalido() from erro
    raise erros.json_invalido()


def _ler_json(conteudo: bytes, _formato: str, opcoes: OpcoesLeitura) -> _LeituraBruta:
    texto, codificacao = decodificar(conteudo, opcoes.codificacao)
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise erros.json_invalido() from erro
    tabela = _tabela_json(dados)
    tabela.columns = pd.Index(padronizar_nomes(list(tabela.columns)))
    return _LeituraBruta(
        dados=tabela,
        codificacao=codificacao.valor,
        tem_cabecalho=True,
        motivos={"codificacao": codificacao.motivo, "cabecalho": "Nomes vêm das chaves do JSON."},
    )


LEITORES: dict[str, Leitor] = {
    "txt": _ler_texto,
    "csv": _ler_texto,
    "tsv": _ler_texto,
    "xlsx": _ler_xlsx,
    "json": _ler_json,
}


def _limpar_textos(serie: pd.Series) -> pd.Series:
    """Tira espaços das pontas e troca marcadores de faltante (NA, -, ?, …) por NaN."""
    if pd.api.types.is_numeric_dtype(serie) or pd.api.types.is_bool_dtype(serie):
        return serie
    aparada = serie.map(lambda valor: valor.strip() if isinstance(valor, str) else valor)
    return aparada.mask(aparada.isin(VALORES_FALTANTES))


def padronizar_dados(dados: pd.DataFrame) -> pd.DataFrame:
    """Faltantes padronizados, linhas vazias fora e índice = nº da linha (1…n, D49)."""
    limpos = dados.apply(_limpar_textos).infer_objects().dropna(how="all")
    return limpos.set_axis(pd.RangeIndex(1, len(limpos) + 1), axis="index")


def _avisos(bruta: _LeituraBruta, n_colunas: int) -> tuple[Aviso, ...]:
    suspeita = any(s in linha for linha in bruta.amostra for s in SEPARADORES_SUSPEITOS)
    if n_colunas == 1 and suspeita:
        mensagem = (
            "Encontramos só uma coluna. O separador pode estar errado — tente escolher outro."
        )
        return (Aviso("UMA_COLUNA", mensagem),)
    return ()


def _metadados(
    formato: Deteccao[str], bruta: _LeituraBruta, dados: pd.DataFrame
) -> MetadadosLeitura:
    motivos = {
        "formato": formato.motivo,
        "codificacao": NAO_SE_APLICA,
        "separador": NAO_SE_APLICA,
        "decimal": NAO_SE_APLICA,
    }
    return MetadadosLeitura(
        formato=formato.valor,
        codificacao=bruta.codificacao,
        separador=bruta.separador,
        decimal=bruta.decimal,
        tem_cabecalho=bruta.tem_cabecalho,
        n_linhas=len(dados),
        n_colunas=dados.shape[1],
        abas=bruta.abas,
        avisos=_avisos(bruta, dados.shape[1]),
        motivos=motivos | bruta.motivos,
    )


def ler_arquivo(conteudo: bytes, nome_arquivo: str, opcoes: OpcoesLeitura) -> ResultadoLeitura:
    """Lê o arquivo detectando formato, codificação, separador, decimal e cabeçalho."""
    formato = detectar_formato(nome_arquivo)
    if not conteudo.strip():
        raise erros.arquivo_vazio()
    bruta = LEITORES[formato.valor](conteudo, formato.valor, opcoes)
    dados = padronizar_dados(bruta.dados)
    if dados.empty:
        raise erros.arquivo_vazio()
    return ResultadoLeitura(dados=dados, metadados=_metadados(formato, bruta, dados))
```

Notas:
- O cabeçalho é lido à parte (`csv.reader` na 1ª linha) para aplicar a regra de duplicados `_2` da spec; o `read_csv` com `header=0` usaria o sufixo `.1` do pandas.
- `padronizar_dados` dá ao índice os números `1…n` (D49): a "linha 45" continua sendo a mesma depois da limpeza.
- Marcadores de faltante (`NA`, `-`, `?`, `—`…) viram `NaN` em todos os formatos.

**Passo 5: rodar e ver passar** — `pytest tests/dominios/datasets/test_leitura.py -v --no-cov` → todos passam

**Passo 6: commit**
```bash
git add app/dominios/datasets/leitura.py tests/fixtures tests/dominios/datasets/test_leitura.py
git commit -m "feat(datasets): lê TXT, CSV, TSV, XLSX e JSON com faltantes padronizados"
```

---

### Tarefa 6: escalas ordinais e classificação (spec 02, ADR 0006)

**Arquivos:**
- Criar: `backend/app/dominios/datasets/escalas_ordinais.py`, `backend/app/dominios/datasets/classificacao.py`
- Teste: `backend/tests/dominios/datasets/test_escalas_ordinais.py`, `test_classificacao.py`

**Passo 1: escrever os testes (falham)**

`test_escalas_ordinais.py`
```python
import pytest

from app.dominios.datasets.escalas_ordinais import ordenar_por_escala


@pytest.mark.parametrize(
    ("valores", "ordem"),
    [
        (["bom", "ruim", "ótimo", "regular"], ("ruim", "regular", "bom", "ótimo")),
        (["Alto", "baixo", "Médio"], ("baixo", "Médio", "Alto")),
        (["pós", "médio", "fundamental", "superior"], ("fundamental", "médio", "superior", "pós")),
        (["G", "P", "M"], ("P", "M", "G")),
        (["grave", "leve"], ("leve", "grave")),
        (["3º", "1º", "2º"], ("1º", "2º", "3º")),
        (["sempre", "nunca", "às vezes"], ("nunca", "às vezes", "sempre")),
    ],
)
def test_ordena_pela_escala_conhecida(valores: list[str], ordem: tuple[str, ...]) -> None:
    assert ordenar_por_escala(valores) == ordem


@pytest.mark.parametrize("valores", [["Goiânia", "Anápolis"], ["bom", "azul"], ["1º", "segundo"]])
def test_sem_escala_devolve_none(valores: list[str]) -> None:
    assert ordenar_por_escala(valores) is None
```

`test_classificacao.py`
```python
import pandas as pd
import pytest

from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.dominios.datasets.classificacao import (
    Classificacao,
    Limiares,
    classificar,
    classificar_tabela,
    ler_coluna,
)

LIMIARES = Limiares()


def _classificar(nome: str, valores: list[object]) -> Classificacao:
    return classificar(ler_coluna(nome, pd.Series(valores), ",", LIMIARES))


def test_coluna_vazia_e_ignorada() -> None:
    resultado = _classificar("obs", [None, None])

    assert resultado.tipo == TipoVariavel.IDENTIFICADOR
    assert resultado.motivo == "A coluna está vazia; foi ignorada."


@pytest.mark.parametrize("nome", ["id", "ID_cliente", "Código", "cpf", "CEP", "matrícula"])
def test_nome_de_codigo_vira_identificador(nome: str) -> None:
    resultado = _classificar(nome, ["1", "1", "2"])

    assert resultado.tipo == TipoVariavel.IDENTIFICADOR
    assert resultado.motivo == f"O nome da coluna indica um código ({nome})."


def test_idade_nao_e_confundida_com_id() -> None:
    assert _classificar("idade", [20, 30, 30, 40]).tipo == TipoVariavel.DISCRETA


def test_cep_numerico_sem_nome_de_codigo_vira_identificador_pelos_unicos() -> None:
    valores = [74000000 + i for i in range(25)]

    resultado = _classificar("local", valores)

    assert resultado.tipo == TipoVariavel.IDENTIFICADOR
    assert resultado.motivo == "Parece um código: 100% dos valores são únicos."


def test_decimais_unicos_nao_viram_identificador() -> None:
    valores = [1.5 + i / 100 for i in range(25)]

    assert _classificar("peso", valores).tipo == TipoVariavel.CONTINUA


@pytest.mark.parametrize(
    ("valores", "motivo"),
    [(["M", "F", "F"], "Tem só dois valores: F e M."), ([0, 1, 1], "Tem só dois valores: 0 e 1.")],
)
def test_dois_valores_vira_binaria(valores: list[object], motivo: str) -> None:
    resultado = _classificar("x", valores)

    assert (resultado.tipo, resultado.motivo) == (TipoVariavel.BINARIA, motivo)


def test_likert_vira_ordinal_com_a_ordem_da_escala() -> None:
    resultado = _classificar("satisfacao", ["bom", "ruim", "ótimo", "regular", "bom"])

    assert resultado.tipo == TipoVariavel.ORDINAL
    assert resultado.categorias_ordem == ("ruim", "regular", "bom", "ótimo")
    assert (
        resultado.motivo == "Os valores seguem uma escala conhecida: ruim < regular < bom < ótimo."
    )


def test_texto_sem_escala_vira_nominal() -> None:
    resultado = _classificar("cidade", ["Goiânia", "Anápolis", "Trindade", "Goiânia"])

    assert resultado.tipo == TipoVariavel.NOMINAL
    assert resultado.motivo == "São categorias sem ordem natural (3 categorias)."


def test_inteiros_com_poucos_valores_viram_discreta() -> None:
    resultado = _classificar("filhos", [0, 1, 2, 2, 3])

    assert resultado.tipo == TipoVariavel.DISCRETA
    assert resultado.motivo == "Números inteiros com 4 valores diferentes (contagem)."


def test_inteiros_com_muitos_valores_viram_continua() -> None:
    valores = [i % 40 for i in range(41)] + [0] * 5

    resultado = _classificar("idade", valores)

    assert resultado.tipo == TipoVariavel.CONTINUA
    assert resultado.motivo == "Inteiros com muitos valores diferentes (40); tratada como contínua."


def test_texto_com_virgula_decimal_vira_continua() -> None:
    resultado = _classificar("altura", ["1,62", "1,78", "1,58"])

    assert (resultado.tipo, resultado.motivo) == (
        TipoVariavel.CONTINUA,
        "Números com casas decimais.",
    )


def test_um_texto_entre_numeros_nao_muda_o_tipo() -> None:
    # 19 de 20 valores (95%) viram número: acima do limiar de 90% (D48).
    valores = [str(i % 10) for i in range(19)] + ["doze"]

    assert _classificar("filhos", valores).tipo == TipoVariavel.DISCRETA


def test_muitos_textos_entre_numeros_viram_nominal() -> None:
    valores = ["1", "2", "3", "doze", "treze", "1"]

    assert _classificar("filhos", valores).tipo == TipoVariavel.NOMINAL


def test_limiar_de_discreta_vem_da_configuracao() -> None:
    coluna = ler_coluna("n", pd.Series([1, 2, 3, 4]), ".", Limiares(discreta=3))

    assert classificar(coluna).tipo == TipoVariavel.CONTINUA


def test_classificar_tabela_descreve_cada_coluna() -> None:
    dados = pd.DataFrame(
        {"sexo": ["F", "M", None, "F"], "peso": [58.2, 79.6, 63.0, None]},
        index=pd.RangeIndex(1, 5),
    )

    tipos = classificar_tabela(dados, ".", LIMIARES)

    sexo = tipos["sexo"]
    assert (sexo.n_validos, sexo.n_faltantes, sexo.n_distintos) == (3, 1, 2)
    assert sexo.origem == OrigemTipo.AUTO
    assert sexo.contagens == {"F": 2, "M": 1}
    assert tipos["peso"].exemplos == ("58,2", "79,6", "63")
    assert tipos["peso"].contagens == {}
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_escalas_ordinais.py tests/dominios/datasets/test_classificacao.py --no-cov` → FAIL

**Passo 3: implementar**

`app/dominios/datasets/escalas_ordinais.py` — "pós" entra como sinônimo de "pós-graduação" (D51, design 2a):
```python
"""Dicionário de escalas ordinais conhecidas (spec 02) e ordenação de categorias."""

import re
from collections.abc import Iterable

from app.compartilhado.textos import normalizar_texto

# Cada escala é uma sequência de níveis; um nível pode ter sinônimos (ótimo = excelente).
type Escala = tuple[tuple[str, ...], ...]

ESCALAS: tuple[Escala, ...] = (
    (("muito baixo",), ("baixo",), ("medio",), ("alto",), ("muito alto",)),
    (("pessimo",), ("ruim",), ("regular",), ("bom",), ("otimo", "excelente")),
    (
        ("discordo totalmente",),
        ("discordo",),
        ("neutro",),
        ("concordo",),
        ("concordo totalmente",),
    ),
    (("nunca",), ("raramente",), ("as vezes",), ("frequentemente",), ("sempre",)),
    (("pp",), ("p",), ("m",), ("g",), ("gg",), ("xg",)),
    (
        ("fundamental incompleto",),
        ("fundamental",),
        ("medio incompleto",),
        ("medio",),
        ("superior incompleto",),
        ("superior",),
        ("pos-graduacao", "pos graduacao", "pos"),
    ),
    (("pequeno",), ("medio",), ("grande",)),
    (("leve",), ("moderado",), ("grave",)),
)

_ORDINAL_NUMERICO = re.compile(r"^(\d+)\s*[º°ª]$")


def _posicoes(escala: Escala) -> dict[str, int]:
    return {nome: nivel for nivel, sinonimos in enumerate(escala) for nome in sinonimos}


def _posicao_numerica(valor: str) -> int | None:
    casamento = _ORDINAL_NUMERICO.match(valor.strip())
    return int(casamento.group(1)) if casamento else None


def _ordenar_por(valores: Iterable[str], posicoes: dict[str, int]) -> tuple[str, ...] | None:
    lista = list(valores)
    if not all(normalizar_texto(v) in posicoes for v in lista):
        return None
    return tuple(sorted(lista, key=lambda v: (posicoes[normalizar_texto(v)], v)))


def _ordenar_numericos(valores: Iterable[str]) -> tuple[str, ...] | None:
    lista = list(valores)
    numeros = {v: _posicao_numerica(v) for v in lista}
    if any(n is None for n in numeros.values()):
        return None
    return tuple(sorted(lista, key=lambda v: (numeros[v] or 0, v)))


def ordenar_por_escala(valores: Iterable[str]) -> tuple[str, ...] | None:
    """Categorias na ordem da 1ª escala que contém todas elas; None se nenhuma servir."""
    lista = list(valores)
    for escala in ESCALAS:
        ordenados = _ordenar_por(lista, _posicoes(escala))
        if ordenados is not None:
            return ordenados
    return _ordenar_numericos(lista)
```

`app/dominios/datasets/classificacao.py` — Chain of Responsibility: `REGRAS` em ordem; sem resposta, contínua (regra 6). `ColunaLida` converte a coluna uma vez (números com o decimal detectado e textos pt-BR); a coluna é numérica se ≥ 90% dos valores válidos viram número (D48).
```python
"""Classificação automática do tipo de cada coluna (spec 02, ADR 0006).

Chain of Responsibility: as regras são testadas em ordem e a primeira que responder vence;
se nenhuma responder, a coluna é contínua.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.series import converter_para_numero, eh_inteira
from app.compartilhado.textos import normalizar_texto, pluralizar
from app.compartilhado.tipos import TIPOS_CATEGORICOS, OrigemTipo, TipoVariavel
from app.dominios.datasets.escalas_ordinais import ordenar_por_escala
from app.dominios.datasets.modelos import TipoColuna

N_MINIMO_IDENTIFICADOR = 20
N_EXEMPLOS = 5
VALORES_BINARIA = 2
PRECISAO_TEXTO = 12
_NOME_DE_CODIGO = re.compile(r"^(id|cod|codigo|cpf|cnpj|cep|telefone|fone|matricula)\b")


@dataclass(frozen=True, slots=True)
class Limiares:
    """Limiares de config.py (spec 02, D48)."""

    discreta: int = 30
    unicos_identificador: float = 0.95
    numerico: float = 0.9


@dataclass(frozen=True, slots=True)
class Classificacao:
    tipo: TipoVariavel
    motivo: str
    categorias_ordem: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, eq=False)
class ColunaLida:
    """Coluna pronta para classificar: valores válidos e, se for numérica, os números."""

    nome: str
    serie: pd.Series
    numeros: pd.Series | None
    textos: pd.Series
    limiares: Limiares

    @property
    def validos(self) -> pd.Series:
        return self.textos.dropna()

    @property
    def n_distintos(self) -> int:
        serie = self.validos if self.numeros is None else self.numeros.dropna()
        return int(serie.nunique())

    def categorias(self) -> list[str]:
        """Valores distintos como texto, em ordem crescente (numérica quando for número)."""
        if self.numeros is None:
            return sorted(str(v) for v in self.validos.unique())
        return [texto_do_numero(v) for v in sorted(self.numeros.dropna().unique())]


def serie_numerica(serie: pd.Series, decimal: str | None, limiar: float) -> pd.Series | None:
    """Série convertida para número se ≥ limiar dos valores válidos viram número (D48)."""
    n_validos = int(serie.notna().sum())
    if n_validos == 0:
        return None
    numeros = converter_para_numero(serie, decimal)
    return numeros if numeros.notna().sum() / n_validos >= limiar else None


def texto_do_numero(valor: float) -> str:
    """Inteiros sem separador de milhar (códigos, contagens); decimais com vírgula."""
    if float(valor).is_integer():
        return str(int(valor))
    return formatar_numero(float(valor), PRECISAO_TEXTO)


def _textos(serie: pd.Series, numeros: pd.Series | None) -> pd.Series:
    if numeros is None:
        return serie.map(lambda v: v if pd.isna(v) else str(v))
    return numeros.map(lambda v: v if pd.isna(v) else texto_do_numero(v))


def ler_coluna(nome: str, serie: pd.Series, decimal: str | None, limiares: Limiares) -> ColunaLida:
    """Converte uma vez e guarda números e textos (números no formato pt-BR)."""
    numeros = serie_numerica(serie, decimal, limiares.numerico)
    return ColunaLida(nome, serie, numeros, _textos(serie, numeros), limiares)


def _eh_decimal(coluna: ColunaLida) -> bool:
    return coluna.numeros is not None and not eh_inteira(coluna.numeros)


def _vazia(coluna: ColunaLida) -> Classificacao | None:
    if not coluna.validos.empty:
        return None
    return Classificacao(TipoVariavel.IDENTIFICADOR, "A coluna está vazia; foi ignorada.")


def _identificador(coluna: ColunaLida) -> Classificacao | None:
    nome = normalizar_texto(coluna.nome).replace("_", " ").replace("-", " ")
    if _NOME_DE_CODIGO.match(nome):
        motivo = f"O nome da coluna indica um código ({coluna.nome})."
        return Classificacao(TipoVariavel.IDENTIFICADOR, motivo)
    n = len(coluna.validos)
    if _eh_decimal(coluna) or n < N_MINIMO_IDENTIFICADOR:
        return None
    unicos = coluna.n_distintos / n
    if unicos < coluna.limiares.unicos_identificador:
        return None
    motivo = f"Parece um código: {formatar_numero(unicos * 100, 3)}% dos valores são únicos."
    return Classificacao(TipoVariavel.IDENTIFICADOR, motivo)


def _binaria(coluna: ColunaLida) -> Classificacao | None:
    if coluna.n_distintos != VALORES_BINARIA:
        return None
    a, b = coluna.categorias()
    return Classificacao(TipoVariavel.BINARIA, f"Tem só dois valores: {a} e {b}.")


def _ordinal(coluna: ColunaLida) -> Classificacao | None:
    ordem = ordenar_por_escala(coluna.categorias()) if coluna.numeros is None else None
    if ordem is None:
        return None
    motivo = f"Os valores seguem uma escala conhecida: {' < '.join(ordem)}."
    return Classificacao(TipoVariavel.ORDINAL, motivo, ordem)


def _nominal(coluna: ColunaLida) -> Classificacao | None:
    if coluna.numeros is not None:
        return None
    k = coluna.n_distintos
    motivo = f"São categorias sem ordem natural ({k} {pluralizar(k, 'categoria', 'categorias')})."
    return Classificacao(TipoVariavel.NOMINAL, motivo)


def _discreta(coluna: ColunaLida) -> Classificacao | None:
    if _eh_decimal(coluna) or coluna.n_distintos > coluna.limiares.discreta:
        return None
    motivo = f"Números inteiros com {coluna.n_distintos} valores diferentes (contagem)."
    return Classificacao(TipoVariavel.DISCRETA, motivo)


def _continua(coluna: ColunaLida) -> Classificacao:
    if _eh_decimal(coluna):
        return Classificacao(TipoVariavel.CONTINUA, "Números com casas decimais.")
    k = coluna.n_distintos
    motivo = f"Inteiros com muitos valores diferentes ({k}); tratada como contínua."
    return Classificacao(TipoVariavel.CONTINUA, motivo)


type Regra = Callable[[ColunaLida], Classificacao | None]

REGRAS: tuple[Regra, ...] = (_vazia, _identificador, _binaria, _ordinal, _nominal, _discreta)


def classificar(coluna: ColunaLida) -> Classificacao:
    """Primeira regra que responder; sem resposta, a coluna é contínua (regra 6)."""
    for regra in REGRAS:
        resultado = regra(coluna)
        if resultado is not None:
            return resultado
    return _continua(coluna)


def descrever(coluna: ColunaLida, classificacao: Classificacao, origem: OrigemTipo) -> TipoColuna:
    """Junta o tipo com contagens, exemplos e (para categóricas) as frequências."""
    contagens = coluna.validos.value_counts()
    categorica = classificacao.tipo in TIPOS_CATEGORICOS
    return TipoColuna(
        coluna=coluna.nome,
        tipo=classificacao.tipo,
        motivo=classificacao.motivo,
        origem=origem,
        n_validos=len(coluna.validos),
        n_faltantes=int(coluna.serie.isna().sum()),
        n_distintos=coluna.n_distintos,
        exemplos=tuple(str(v) for v in coluna.validos.unique()[:N_EXEMPLOS]),
        categorias_ordem=classificacao.categorias_ordem,
        contagens={str(k): int(v) for k, v in contagens.items()} if categorica else {},
    )


def classificar_tabela(
    dados: pd.DataFrame, decimal: str | None, limiares: Limiares
) -> dict[str, TipoColuna]:
    """Classifica todas as colunas (origem automática)."""
    resultado: dict[str, TipoColuna] = {}
    for nome in dados.columns:
        coluna = ler_coluna(str(nome), dados[nome], decimal, limiares)
        resultado[str(nome)] = descrever(coluna, classificar(coluna), OrigemTipo.AUTO)
    return resultado
```

**Passo 4: rodar e ver passar** — `pytest tests/dominios/datasets -v --no-cov` → todos passam

**Passo 5: conferir com o exemplo real** (manual, só olhar)
```bash
python -c "from pathlib import Path; from app.dominios.datasets.leitura import ler_arquivo; from app.dominios.datasets.modelos import OpcoesLeitura; from app.dominios.datasets.classificacao import classificar_tabela, Limiares; r = ler_arquivo(Path('../dados-exemplo/pesquisa_saude.txt').read_bytes(), 'pesquisa_saude.txt', OpcoesLeitura()); [print(t.coluna, t.tipo.value, '-', t.motivo) for t in classificar_tabela(r.dados, r.metadados.decimal, Limiares()).values()]"
```
Esperado: `id` identificador · `sexo` binária · `idade` contínua ("Inteiros com muitos valores diferentes (55)…") · `altura_m` e `peso_kg` contínua · `escolaridade` ordinal (fundamental < médio < superior < pós) · `cidade` nominal (10 categorias, por causa das grafias) · `satisfacao` ordinal.

> O print 2a mostra `idade` como discreta; pela regra 5 da spec (≤ 30 valores distintos) ela é contínua. O usuário corrige na tela Variáveis. Ver dúvida registrada na visão geral.

**Passo 6: commit**
```bash
git add app/dominios/datasets/escalas_ordinais.py app/dominios/datasets/classificacao.py tests/dominios/datasets
git commit -m "feat(datasets): classifica o tipo de cada coluna com motivo (regras da spec 02)"
```

---

### Tarefa 7: ajuste manual do tipo

**Arquivos:**
- Criar: `backend/app/dominios/datasets/ajuste_tipo.py`
- Teste: `backend/tests/dominios/datasets/test_ajuste_tipo.py`

**Passo 1: escrever os testes (falham)**
```python
import pandas as pd
import pytest

from app.compartilhado.tipos import OrigemTipo, TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.datasets.ajuste_tipo import (
    MOTIVO_MANUAL,
    MOTIVO_ORDEM_ALFABETICA,
    ajustar_tipo,
)
from app.dominios.datasets.classificacao import ColunaLida, Limiares, ler_coluna


def _coluna(valores: list[object]) -> ColunaLida:
    return ler_coluna("x", pd.Series(valores), ",", Limiares())


def test_tipo_manual_registra_origem_e_motivo() -> None:
    tipo = ajustar_tipo(_coluna([1, 2, 3]), TipoVariavel.DISCRETA, None)

    assert (tipo.tipo, tipo.origem, tipo.motivo) == (
        TipoVariavel.DISCRETA,
        OrigemTipo.MANUAL,
        MOTIVO_MANUAL,
    )


def test_texto_nao_pode_ser_numerico() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["a", "b"]), TipoVariavel.CONTINUA, None)

    assert erro.value.codigo == "TIPO_INCOMPATIVEL"
    assert erro.value.mensagem == "Esta coluna tem textos; não pode ser numérica."


def test_binaria_exige_dois_valores() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["a", "b", "c"]), TipoVariavel.BINARIA, None)

    assert "esta coluna tem 3" in erro.value.mensagem


def test_ordinal_com_ordem_informada() -> None:
    tipo = ajustar_tipo(_coluna(["b", "a", "c"]), TipoVariavel.ORDINAL, ["c", "a", "b", "z"])

    assert tipo.categorias_ordem == ("c", "a", "b")


def test_ordinal_com_ordem_incompleta_e_recusado() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajustar_tipo(_coluna(["b", "a", "c"]), TipoVariavel.ORDINAL, ["a", "b"])

    assert erro.value.codigo == "CATEGORIAS_INCOMPLETAS"


def test_ordinal_sem_ordem_usa_a_escala_ou_a_ordem_alfabetica() -> None:
    escala = ajustar_tipo(_coluna(["bom", "ruim"]), TipoVariavel.ORDINAL, None)
    alfabetica = ajustar_tipo(_coluna(["c", "a", "b"]), TipoVariavel.ORDINAL, None)

    assert escala.categorias_ordem == ("ruim", "bom")
    assert alfabetica.categorias_ordem == ("a", "b", "c")
    assert alfabetica.motivo == MOTIVO_ORDEM_ALFABETICA


def test_numeros_podem_virar_ordinal_com_categorias_em_texto() -> None:
    tipo = ajustar_tipo(_coluna([3, 1, 2, 1]), TipoVariavel.ORDINAL, ["1", "2", "3"])

    assert tipo.categorias_ordem == ("1", "2", "3")
    assert tipo.contagens == {"1": 2, "3": 1, "2": 1}
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_ajuste_tipo.py --no-cov` → FAIL

**Passo 3: implementar `app/dominios/datasets/ajuste_tipo.py`**
```python
"""Ajuste manual do tipo de uma coluna (spec 02, "Ajuste manual")."""

from app.compartilhado.tipos import TIPOS_NUMERICOS, OrigemTipo, TipoVariavel
from app.dominios.datasets import erros
from app.dominios.datasets.classificacao import (
    VALORES_BINARIA,
    Classificacao,
    ColunaLida,
    descrever,
)
from app.dominios.datasets.escalas_ordinais import ordenar_por_escala
from app.dominios.datasets.modelos import TipoColuna

MOTIVO_MANUAL = "Tipo escolhido por você."
MOTIVO_ORDEM_ALFABETICA = (
    "Tipo escolhido por você. Sem escala conhecida, usamos a ordem alfabética; "
    "ajuste a ordem das categorias."
)


def _validar(coluna: ColunaLida, tipo: TipoVariavel) -> None:
    if tipo in TIPOS_NUMERICOS and coluna.numeros is None:
        raise erros.tipo_incompativel("Esta coluna tem textos; não pode ser numérica.")
    if tipo == TipoVariavel.BINARIA and coluna.n_distintos != VALORES_BINARIA:
        mensagem = f"Binária precisa de exatamente 2 valores; esta coluna tem {coluna.n_distintos}."
        raise erros.tipo_incompativel(mensagem)


def _ordem_informada(coluna: ColunaLida, ordem: list[str]) -> Classificacao:
    presentes = coluna.categorias()
    faltando = [c for c in presentes if c not in ordem]
    if faltando:
        raise erros.categorias_incompletas(faltando)
    ordenadas = tuple(c for c in ordem if c in presentes)
    return Classificacao(TipoVariavel.ORDINAL, MOTIVO_MANUAL, ordenadas)


def _ordem_automatica(coluna: ColunaLida) -> Classificacao:
    ordem = ordenar_por_escala(coluna.categorias())
    if ordem is None:
        alfabetica = tuple(sorted(coluna.categorias()))
        return Classificacao(TipoVariavel.ORDINAL, MOTIVO_ORDEM_ALFABETICA, alfabetica)
    return Classificacao(TipoVariavel.ORDINAL, MOTIVO_MANUAL, ordem)


def ajustar_tipo(
    coluna: ColunaLida, tipo: TipoVariavel, categorias_ordem: list[str] | None
) -> TipoColuna:
    """Aplica o tipo escolhido pelo usuário (origem manual) depois de validar."""
    _validar(coluna, tipo)
    if tipo != TipoVariavel.ORDINAL:
        return descrever(coluna, Classificacao(tipo, MOTIVO_MANUAL), OrigemTipo.MANUAL)
    if categorias_ordem:
        return descrever(coluna, _ordem_informada(coluna, categorias_ordem), OrigemTipo.MANUAL)
    return descrever(coluna, _ordem_automatica(coluna), OrigemTipo.MANUAL)
```

**Passo 4: rodar e ver passar** — `pytest tests/dominios/datasets/test_ajuste_tipo.py -v --no-cov`

**Passo 5: commit**
```bash
git add app/dominios/datasets/ajuste_tipo.py tests/dominios/datasets/test_ajuste_tipo.py
git commit -m "feat(datasets): permite corrigir o tipo e a ordem das categorias"
```

---

### Tarefa 8: tabela (células e paginação) e repositório

**Arquivos:**
- Criar: `backend/app/dominios/datasets/tabela.py`, `backend/app/dominios/datasets/repositorio.py`
- Teste: `backend/tests/dominios/datasets/test_tabela.py`, `test_repositorio.py`

**Passo 1: escrever os testes (falham)**

`test_tabela.py`
```python
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from app.dominios.datasets.tabela import celula, linhas_dados, paginar


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (np.int64(3), 3),
        (np.float64(1.5), 1.5),
        (float("nan"), None),
        (None, None),
        (pd.NA, None),
        ("Goiânia", "Goiânia"),
        (np.True_, True),
        (datetime(2026, 10, 3, 9, 30), "2026-10-03T09:30:00"),
    ],
)
def test_celula_vira_tipo_simples(valor: object, esperado: object) -> None:
    assert celula(valor) == esperado


def test_linhas_guardam_o_numero_original() -> None:
    dados = pd.DataFrame({"a": [1, 2, 3]}, index=pd.Index([1, 5, 9]))

    assert [linha.linha for linha in linhas_dados(dados)] == [1, 5, 9]


def test_paginar() -> None:
    dados = pd.DataFrame({"a": range(45)}, index=pd.RangeIndex(1, 46))

    pagina = paginar(dados, pagina=3, tamanho=20)

    assert pagina.total_paginas == 3
    assert [linha.linha for linha in pagina.linhas] == [41, 42, 43, 44, 45]
```

`test_repositorio.py`
```python
import pandas as pd
import pytest

from app.core.erros import NaoEncontrado
from app.dominios.datasets.modelos import Dataset, MetadadosLeitura
from app.dominios.datasets.repositorio import RepositorioDatasets


def _dataset(identificador: str) -> Dataset:
    dados = pd.DataFrame({"a": [1]})
    metadados = MetadadosLeitura("csv", "utf-8", ",", ".", True, 1, 1)
    return Dataset(identificador, "a.csv", metadados, dados, dados.copy(), {})


def test_repositorio_guarda_e_devolve() -> None:
    repositorio = RepositorioDatasets(limite=2)
    repositorio.adicionar(_dataset("a"))

    assert repositorio.obter("a").id == "a"


def test_repositorio_descarta_o_mais_antigo() -> None:
    repositorio = RepositorioDatasets(limite=2)
    for identificador in ("a", "b", "c"):
        repositorio.adicionar(_dataset(identificador))

    assert len(repositorio) == 2
    with pytest.raises(NaoEncontrado) as erro:
        repositorio.obter("a")
    assert erro.value.codigo == "DATASET_NAO_ENCONTRADO"


def test_repositorio_remove() -> None:
    repositorio = RepositorioDatasets(limite=2)
    repositorio.adicionar(_dataset("a"))

    repositorio.remover("a")

    assert len(repositorio) == 0
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_tabela.py tests/dominios/datasets/test_repositorio.py --no-cov` → FAIL

**Passo 3: implementar**

`app/dominios/datasets/tabela.py`
```python
"""Conversão de linhas do DataFrame em células simples para a API (prévia e paginação)."""

import math
from dataclasses import dataclass
from datetime import date, datetime

import numpy as np
import pandas as pd

from app.dominios.datasets.modelos import Celula, LinhaDados


def celula(valor: object) -> Celula:
    """Valor de uma célula como tipo simples; faltante vira None."""
    if isinstance(valor, np.generic):
        valor = valor.item()
    if isinstance(valor, datetime | date):
        return valor.isoformat()
    if isinstance(valor, float) and math.isnan(valor):
        return None
    if valor is None or valor is pd.NA or valor is pd.NaT:
        return None
    if isinstance(valor, str | int | float | bool):
        return valor
    return str(valor)


def linhas_dados(dados: pd.DataFrame) -> tuple[LinhaDados, ...]:
    """Linhas com o número original (índice) e os valores por coluna."""
    registros = dados.to_dict(orient="records")
    return tuple(
        LinhaDados(linha=int(numero), valores={str(c): celula(v) for c, v in valores.items()})
        for numero, valores in zip(dados.index.tolist(), registros, strict=True)
    )


@dataclass(frozen=True, slots=True)
class Pagina:
    linhas: tuple[LinhaDados, ...]
    pagina: int
    tamanho: int
    total_paginas: int


def paginar(dados: pd.DataFrame, pagina: int, tamanho: int) -> Pagina:
    """Recorte das linhas da página pedida (a 1ª página é 1)."""
    total_paginas = max(1, math.ceil(len(dados) / tamanho))
    inicio = (pagina - 1) * tamanho
    return Pagina(
        linhas_dados(dados.iloc[inicio : inicio + tamanho]), pagina, tamanho, total_paginas
    )
```

`app/dominios/datasets/repositorio.py`
```python
"""Repositório em memória: dataset_id → Dataset (ADR 0004)."""

from collections import OrderedDict

from app.dominios.datasets import erros
from app.dominios.datasets.modelos import Dataset


class RepositorioDatasets:
    """Guarda até `limite` datasets; ao passar do limite, o mais antigo é descartado."""

    def __init__(self, limite: int) -> None:
        self._limite = limite
        self._itens: OrderedDict[str, Dataset] = OrderedDict()

    def __len__(self) -> int:
        return len(self._itens)

    def adicionar(self, dataset: Dataset) -> None:
        self._itens[dataset.id] = dataset
        while len(self._itens) > self._limite:
            self._itens.popitem(last=False)

    def obter(self, dataset_id: str) -> Dataset:
        dataset = self._itens.get(dataset_id)
        if dataset is None:
            raise erros.dataset_nao_encontrado()
        return dataset

    def remover(self, dataset_id: str) -> None:
        self.obter(dataset_id)
        del self._itens[dataset_id]
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/datasets/tabela.py app/dominios/datasets/repositorio.py tests/dominios/datasets
git commit -m "feat(datasets): adiciona repositório em memória e paginação de linhas"
```

---

### Tarefa 9: fachada `ServicoDatasets`

**Arquivos:**
- Criar: `backend/app/dominios/datasets/servico.py`
- Modificar: `backend/tests/conftest.py`
- Teste: `backend/tests/dominios/datasets/test_servico.py`

**Passo 1: atualizar o `conftest.py` e escrever os testes (falham)**

`tests/conftest.py` (substituir) — o `cliente` troca o serviço por um com repositório novo, então cada teste começa sem datasets e o estado não vaza entre testes:
```python
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Configuracao
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.main import create_app


@pytest.fixture
def servico_datasets() -> ServicoDatasets:
    """Serviço com repositório novo: cada teste começa sem datasets."""
    config = Configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)


@pytest.fixture
def cliente(servico_datasets: ServicoDatasets) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[obter_servico_datasets] = lambda: servico_datasets
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
```

`tests/dominios/datasets/test_servico.py`
```python
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.core.config import Configuracao
from app.core.erros import ArquivoGrande, NaoEncontrado
from app.dominios.datasets.repositorio import RepositorioDatasets
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets

CONTEUDO = b"id;sexo;peso\n1;F;58,2\n2;M;79,6\n3;F;\n4;M;63,0\n"


def _importar(servico: ServicoDatasets) -> str:
    return servico.importar(CONTEUDO, "dados.txt", OpcoesLeitura()).dataset_id


def test_importar_guarda_original_e_atual_separados(servico_datasets: ServicoDatasets) -> None:
    dataset = servico_datasets.obter(_importar(servico_datasets))

    assert dataset.original is not dataset.atual
    assert dataset.tipos["sexo"].tipo == TipoVariavel.BINARIA


def test_importar_devolve_previa_e_colunas(servico_datasets: ServicoDatasets) -> None:
    importacao = servico_datasets.importar(CONTEUDO, "dados.txt", OpcoesLeitura())

    assert [linha.linha for linha in importacao.previa] == [1, 2, 3, 4]
    assert importacao.previa[2].valores["peso"] is None
    assert [c.coluna for c in importacao.colunas] == ["id", "sexo", "peso"]


def test_arquivo_acima_do_limite() -> None:
    config = Configuracao(limite_arquivo_mb=0)
    servico = ServicoDatasets(RepositorioDatasets(1), config)

    with pytest.raises(ArquivoGrande):
        servico.importar(b"a\n1\n", "a.csv", OpcoesLeitura())


def test_importar_exemplo(servico_datasets: ServicoDatasets) -> None:
    importacao = servico_datasets.importar_exemplo()

    assert importacao.nome_arquivo == "pesquisa_saude.txt"
    assert importacao.metadados.n_linhas == 230


def test_resumo_e_pagina(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    pagina = servico_datasets.pagina(dataset_id, pagina=1, tamanho=2, versao="original")

    assert pagina.resumo.n_linhas == 4
    assert pagina.total_paginas == 2
    assert len(pagina.linhas) == 2


def test_alterar_tipo_atualiza_o_dataset(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    servico_datasets.alterar_tipo(dataset_id, "sexo", TipoVariavel.NOMINAL)

    assert servico_datasets.colunas(dataset_id)[1].tipo == TipoVariavel.NOMINAL


def test_coluna_inexistente(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    with pytest.raises(NaoEncontrado) as erro:
        servico_datasets.coluna_para_analise(dataset_id, "altura")

    assert erro.value.codigo == "COLUNA_NAO_ENCONTRADA"


def test_coluna_para_analise_entrega_numeros_ou_textos(servico_datasets: ServicoDatasets) -> None:
    dataset_id = _importar(servico_datasets)

    peso = servico_datasets.coluna_para_analise(dataset_id, "peso")
    sexo = servico_datasets.coluna_para_analise(dataset_id, "sexo")

    assert peso.numeros is not None
    assert peso.numeros.dropna().tolist() == [58.2, 79.6, 63.0]
    assert sexo.numeros is None
    assert sexo.textos.tolist() == ["F", "M", "F", "M"]
    assert isinstance(sexo.textos, pd.Series)
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_servico.py --no-cov` → FAIL (`ModuleNotFoundError: app.dominios.datasets.servico`)

**Passo 3: implementar `app/dominios/datasets/servico.py`**
```python
"""Fachada do domínio datasets: casos de uso de importação, consulta e tipos (D54)."""

import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import pandas as pd

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.core.config import Configuracao, obter_configuracao
from app.dominios.datasets import erros
from app.dominios.datasets.ajuste_tipo import ajustar_tipo
from app.dominios.datasets.classificacao import (
    ColunaLida,
    Limiares,
    classificar_tabela,
    ler_coluna,
)
from app.dominios.datasets.leitura import ler_arquivo
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
    "ColunaAnalise",
    "Importacao",
    "OpcoesLeitura",
    "PaginaDataset",
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


@lru_cache
def obter_servico_datasets() -> ServicoDatasets:
    """Instância única (repositório em memória compartilhado entre requisições)."""
    config = obter_configuracao()
    return ServicoDatasets(RepositorioDatasets(config.max_datasets), config)
```

Notas:
- `coluna_para_analise` é a porta de entrada do domínio `analise` (M1.4): devolve números (para discreta/contínua) ou textos (para categóricas) já convertidos, mais a ordem das categorias.
- `__all__` reexporta `OpcoesLeitura` para o `router` (que só pode importar `schemas`, `servico`, `core` e `fastapi`).

**Passo 4: rodar e ver passar** — `pytest tests/dominios/datasets -v --no-cov`

**Passo 5: commit**
```bash
git add app/dominios/datasets/servico.py tests/conftest.py tests/dominios/datasets/test_servico.py
git commit -m "feat(datasets): adiciona fachada do domínio com importação, páginas e tipos"
```

---

### Tarefa 10: schemas, router e registro no `main`

**Arquivos:**
- Criar: `backend/app/dominios/datasets/schemas.py`, `backend/app/dominios/datasets/router.py`
- Modificar: `backend/app/main.py`
- Teste: `backend/tests/dominios/datasets/test_router.py`

**Passo 1: escrever os testes (falham)**
```python
from fastapi.testclient import TestClient

ARQUIVO = ("pesquisa.txt", b"id;sexo;peso\n1;F;58,2\n2;M;79,6\n3;F;\n4;M;63,0\n", "text/plain")


def _importar(cliente: TestClient) -> str:
    resposta = cliente.post("/api/datasets", files={"arquivo": ARQUIVO})
    assert resposta.status_code == 201
    return str(resposta.json()["dataset_id"])


def test_importar_devolve_metadados_previa_e_colunas(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets", files={"arquivo": ARQUIVO})

    corpo = resposta.json()
    assert resposta.status_code == 201
    assert corpo["metadados"]["separador"] == ";"
    assert corpo["metadados"]["motivos"]["decimal"] == "Valores como 58,2 e 79,6."
    assert corpo["previa"][0] == {"linha": 1, "valores": {"id": 1, "sexo": "F", "peso": 58.2}}
    assert [c["tipo"] for c in corpo["colunas"]] == ["identificador", "binaria", "continua"]


def test_importar_com_opcoes_do_formulario(cliente: TestClient) -> None:
    resposta = cliente.post(
        "/api/datasets",
        files={"arquivo": ARQUIVO},
        data={"separador": ";", "decimal": ",", "tem_cabecalho": "true"},
    )

    assert resposta.json()["metadados"]["motivos"]["separador"] == "Escolhido por você."


def test_formato_nao_suportado(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets", files={"arquivo": ("a.pdf", b"%PDF", "x")})

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "FORMATO_NAO_SUPORTADO"


def test_importar_exemplo(cliente: TestClient) -> None:
    resposta = cliente.post("/api/datasets/exemplo")

    assert resposta.status_code == 201
    assert resposta.json()["nome_arquivo"] == "pesquisa_saude.txt"


def test_pagina_com_resumo(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    corpo = cliente.get(f"/api/datasets/{dataset_id}", params={"tamanho": 2}).json()

    assert corpo["resumo"]["n_linhas"] == 4
    assert corpo["resumo"]["log_limpeza"] == []
    assert corpo["total_paginas"] == 2


def test_dataset_inexistente(cliente: TestClient) -> None:
    resposta = cliente.get("/api/datasets/nao-existe")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "codigo": "DATASET_NAO_ENCONTRADO",
        "mensagem": "Sua sessão expirou.",
        "sugestao": "Envie o arquivo novamente.",
    }


def test_remover(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    assert cliente.delete(f"/api/datasets/{dataset_id}").status_code == 204
    assert cliente.get(f"/api/datasets/{dataset_id}").status_code == 404


def test_listar_e_alterar_tipo(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    resposta = cliente.patch(
        f"/api/datasets/{dataset_id}/colunas/sexo",
        json={"tipo": "ordinal", "categorias_ordem": ["M", "F"]},
    )
    colunas = cliente.get(f"/api/datasets/{dataset_id}/colunas").json()

    assert resposta.status_code == 200
    assert resposta.json()["origem"] == "manual"
    assert colunas[1]["categorias_ordem"] == ["M", "F"]


def test_alterar_tipo_incompativel(cliente: TestClient) -> None:
    dataset_id = _importar(cliente)

    resposta = cliente.patch(f"/api/datasets/{dataset_id}/colunas/sexo", json={"tipo": "continua"})

    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "TIPO_INCOMPATIVEL"
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/datasets/test_router.py --no-cov` → FAIL (404 nas rotas)

**Passo 3: implementar**

`app/dominios/datasets/schemas.py`
```python
"""Contratos HTTP do domínio datasets (spec 14; nomes na visão geral do M1)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.compartilhado.tipos import OrigemTipo, TipoVariavel

type Celula = str | float | int | bool | None


class Modelo(BaseModel):
    """Base: aceita dataclasses do domínio via atributos."""

    model_config = ConfigDict(from_attributes=True)


class Aviso(Modelo):
    codigo: str
    mensagem: str


class MetadadosLeitura(Modelo):
    formato: Literal["txt", "csv", "tsv", "xlsx", "json"]
    codificacao: str | None
    separador: str | None
    decimal: str | None
    tem_cabecalho: bool | None
    n_linhas: int
    n_colunas: int
    abas: list[str]
    avisos: list[Aviso]
    motivos: dict[str, str]


class TipoColuna(Modelo):
    coluna: str
    tipo: TipoVariavel
    motivo: str
    origem: OrigemTipo
    n_validos: int
    n_faltantes: int
    n_distintos: int
    exemplos: list[str]
    categorias_ordem: list[str]
    contagens: dict[str, int]


class LinhaDados(Modelo):
    linha: int
    valores: dict[str, Celula]


class DatasetCriado(Modelo):
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    previa: list[LinhaDados]
    colunas: list[TipoColuna]


class EntradaLog(Modelo):
    problema: str
    acao: str
    coluna: str | None
    linhas_afetadas: list[int]
    antes_exemplo: str
    depois_exemplo: str
    quando: datetime
    frase: str


class ResumoDataset(Modelo):
    dataset_id: str
    nome_arquivo: str
    metadados: MetadadosLeitura
    n_linhas: int
    n_linhas_original: int
    n_colunas: int
    log_limpeza: list[EntradaLog]


class PaginaDataset(Modelo):
    resumo: ResumoDataset
    versao: Literal["atual", "original"]
    pagina: int
    tamanho: int
    total_paginas: int
    linhas: list[LinhaDados]


class AlteracaoTipo(BaseModel):
    tipo: TipoVariavel
    categorias_ordem: list[str] | None = None
```

`app/dominios/datasets/router.py`
```python
"""Rotas HTTP do domínio datasets (spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile, status

from app.dominios.datasets.schemas import (
    AlteracaoTipo,
    DatasetCriado,
    PaginaDataset,
    TipoColuna,
)
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets, obter_servico_datasets

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
```

> Por que `_opcoes_leitura` com `Form()` campo a campo e não um modelo Pydantic com `Form()`: com `UploadFile` no mesmo endpoint, o FastAPI 0.142 trata o modelo como um campo único e devolve 422. A função de dependência mantém o endpoint com 3 parâmetros (limite de 5).

`app/main.py` (substituir)
```python
"""Ponto de entrada: monta a aplicação FastAPI (monólito em camadas por domínio, ADR 0007)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import saude
from app.core.config import obter_configuracao
from app.core.handlers import registrar_handlers
from app.dominios.datasets import router as datasets

PREFIXO_API = "/api"


def create_app() -> FastAPI:
    """Fábrica da aplicação: middlewares, handlers e routers dos domínios."""
    config = obter_configuracao()
    app = FastAPI(title=config.nome_app, version=config.versao)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origens,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    registrar_handlers(app)
    app.include_router(saude.router, prefix=PREFIXO_API)
    app.include_router(datasets.router, prefix=PREFIXO_API)
    return app


app = create_app()
```

**Passo 4: rodar a suíte toda**
```bash
ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest
```
Esperado: tudo verde; cobertura total ≥ 80% (no rascunho deu 99%). O teste `tests/arquitetura` confirma que o router só importa `schemas`/`servico` e que o domínio não importa FastAPI/Pydantic.

**Passo 5: conferir no navegador**
`uvicorn app.main:app --reload` → `http://localhost:8000/docs`: "Importa um arquivo de dados" com `../dados-exemplo/pesquisa_saude.txt` → 201 com 8 colunas; `POST /api/datasets/exemplo` → 201.

**Passo 6: commit**
```bash
git add app/dominios/datasets/schemas.py app/dominios/datasets/router.py app/main.py tests/dominios/datasets/test_router.py
git commit -m "feat(datasets): expõe importação, páginas, colunas e ajuste de tipo na API"
```

---

### Tarefa 11: tipos do frontend, ADR 0009, decisões, specs e CHANGELOG

**Passo 1: gerar os tipos do frontend**
```bash
python scripts/exportar_openapi.py
cd ../frontend && npm run gerar:tipos && npm run lint && npm run build && cd ../backend
```
Esperado: `frontend/src/shared/api/schema.d.ts` passa a ter `DatasetCriado`, `TipoColuna`, `PaginaDataset`, `TipoVariavel`… O frontend ainda não usa esses tipos (M1.6), mas o arquivo gerado entra no commit.

**Passo 2: ADR 0009** — criar `docs/adr/0009-injecao-entre-dominios.md`:
```markdown
# 0009 — Injeção de serviços entre domínios
- **Status:** Aceito
- **Data:** DD/10/2026

## Contexto
Domínios conversam só pela fachada `servico.py` (ADR 0007), e o `servico` não pode importar FastAPI. Mesmo assim, o repositório em memória precisa ser único por processo e trocável nos testes (`dependency_overrides`), e o domínio `analise` precisa do `datasets`.

## Opções consideradas
1. Funções soltas no `servico` lendo um repositório global.
2. `Depends` dentro do `servico`.
3. Classe de fachada por domínio + provedor sem FastAPI; o `router` monta as dependências.

## Decisão
Opção 3. Cada domínio expõe `Servico<Dominio>` (fachada com os casos de uso) e `obter_servico_<dominio>()` com `@lru_cache` em `servico.py`. Quem depende de outro domínio recebe a fachada no construtor. Só o `router.py` usa `Depends`, por exemplo `def _servico(datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)]) -> ServicoAnalise`.

## Consequências
- (+) `servico` continua sem FastAPI e testável com objetos comuns.
- (+) Um único override (`obter_servico_datasets`) isola o estado em todos os testes de API.
- (−) Um pouco de código de montagem em cada router. Aceitável.
```
E acrescentar a linha da 0009 na tabela de `docs/adr/README.md`.

**Passo 3: `docs/decisions.md`** — acrescentar (data do dia):
```
| D48 | DD/10/2026 | Coluna é numérica se ≥ 90% dos valores válidos viram número (`limiar_numerico`); o resto aparece como "tipo misto" na limpeza | Exigir 100%; tratar como texto | Um "doze" no meio de números não deve mudar o tipo da coluna | [0006](adr/0006-classificacao-de-tipos.md) |
| D49 | DD/10/2026 | Índice do DataFrame = número da linha no arquivo (1…n), mantido após a limpeza | Reindexar após cada ação | "Linha 45" significa sempre a mesma linha para o usuário | [0004](adr/0004-estado-em-memoria.md) |
| D51 | DD/10/2026 | "pós" é sinônimo de "pós-graduação" na escala de escolaridade | Escala separada | Abreviação comum (design 2a) | [0006](adr/0006-classificacao-de-tipos.md) |
| D52 | DD/10/2026 | `POST /api/datasets/exemplo` carrega `dados-exemplo/pesquisa_saude.txt` | O frontend baixar o arquivo | Link "Abrir … de exemplo" da tela 1 sem servir arquivos estáticos | — |
| D53 | DD/10/2026 | `MetadadosLeitura.motivos` explica cada detecção; separador por contagem constante e cabeçalho por regra própria (sem `csv.Sniffer`) | `csv.Sniffer` | Tela 1a mostra o porquê; o Sniffer confunde vírgula decimal com separador | — |
| D54 | DD/10/2026 | Fachada `Servico<Dominio>` + `obter_servico_<dominio>()`; `Depends` só no router | Funções soltas; `Depends` no serviço | Testável e com override único | [0009](adr/0009-injecao-entre-dominios.md) |
| D55 | DD/10/2026 | `GET /datasets/{id}` devolve `resumo` (nome, metadados, linhas atuais/originais, log da limpeza) e a página de linhas | Endpoint de resumo separado | Cabeçalho e painel de log usam a mesma chamada da prévia | — |
```

**Passo 4: specs**
- `docs/specs/01-leitura.md`: em "Detecção automática", trocar o item 2 por "Separador: entre `; , \t |` e espaço múltiplo, o que aparece o mesmo número de vezes em ≥ 90% das 50 primeiras linhas e gera mais colunas (D53)"; item 3 por "Cabeçalho: a 1ª linha tem só textos únicos que não aparecem como valor na própria coluna; senão `col_1..col_n`"; item 4 por "Decimal: entre os números com `,` ou `.`, vírgula se ≥ 80% casam o padrão `1.234,5`; sem números decimais, `;` → vírgula". Em "Entrada / saída", acrescentar `abas[]` e `motivos{}` aos metadados.
- `docs/specs/02-tipos.md`: em "Regras", acrescentar antes da tabela "Coluna de texto conta como numérica se ≥ 90% dos valores válidos viram número (`LIMIAR_NUMERICO = 0,9`, D48)"; no dicionário, "superior < pós-graduação / pós". Em "Configuração", acrescentar `LIMIAR_NUMERICO = 0.9`.
- `docs/specs/14-api.md`: acrescentar a linha `POST /datasets/exemplo` e, na linha `GET /datasets/{id}`, a resposta `{resumo, versao, pagina, tamanho, total_paginas, linhas}`.

**Passo 5: `CHANGELOG.md`** — em *Não lançado › Adicionado*:
```
- Importação de TXT, CSV, TSV, XLSX e JSON com detecção de codificação, separador, decimal e cabeçalho, e o motivo de cada detecção.
- Classificação automática do tipo de cada coluna (nominal, ordinal, discreta, contínua, binária, identificador) com motivo, e ajuste manual do tipo e da ordem das categorias.
- Datasets em memória (até 20) e endpoints `POST /api/datasets`, `POST /api/datasets/exemplo`, `GET/DELETE /api/datasets/{id}`, `GET /api/datasets/{id}/colunas`, `PATCH /api/datasets/{id}/colunas/{coluna}`.
```

**Passo 6: commit**
```bash
git add ../frontend/src/shared/api/schema.d.ts ../docs ../CHANGELOG.md
git commit -m "docs: registra ADR 0009, decisões D48–D55 e atualiza specs 01, 02 e 14"
```

---

### Tarefa 12: verificação final, teste manual e PR

**Passo 1: tudo verde**
```bash
cd backend && ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest
cd ../frontend && npm run lint && npm run format && npm run test && npm run build
cd .. && npx --yes jscpd@4 backend/app backend/tests frontend/src
```

**Passo 2: teste manual pelo preview** — subir `backend` pelo `.claude/launch.json` e, em `http://localhost:8000/docs`:
1. `POST /api/datasets/exemplo` → 201, 230 linhas × 8 colunas, `motivos.separador = "Aparece 7 vezes em todas as linhas."`.
2. `POST /api/datasets` com `dados-exemplo/notas_turma.csv` → separador `,`, decimal `.`, `matricula` identificador, `faltas` discreta, `conceito` ordinal.
3. `PATCH .../colunas/idade` com `{"tipo": "discreta"}` → 200, `origem: "manual"`; com `{"tipo": "continua"}` em `cidade` → 400 `TIPO_INCOMPATIVEL`.
4. `GET /api/datasets/qualquer` → 404 com "Sua sessão expirou.".
5. Upload de um `.pdf` → 400 `FORMATO_NAO_SUPORTADO`.

**Passo 3: resumo para o usuário e PR** — mostrar o resumo (o que foi feito, saída dos comandos, teste manual, desvios). Só com o ok:
```bash
git push -u origin feat/datasets-leitura-tipos
gh pr create --base develop --title "feat(datasets): leitura, classificação de tipos e API de datasets (M1.2)" --body "<resumo + specs 01, 02, 14 + checklist do padroes-codigo.md §8>"
```
Sem linhas de coautoria ou atribuição de IA. Acompanhar o CI (`backend`, `frontend`, `duplicacao`); merge só quando o usuário pedir.

---

## Critérios de pronto do M1.2
- [ ] `POST /api/datasets` lê os 5 formatos com as detecções e motivos da spec 01; erros `ARQUIVO_VAZIO`, `FORMATO_NAO_SUPORTADO`, `ARQUIVO_GRANDE` (413), `JSON_INVALIDO`, `ARQUIVO_ILEGIVEL` com `{codigo, mensagem, sugestao}`
- [ ] Classificação com as 6 regras + coluna vazia, motivo em linguagem simples, ajuste manual validado
- [ ] Repositório com limite de 20 e `DATASET_NAO_ENCONTRADO` (404)
- [ ] `schema.d.ts` regenerado; ADR 0009, D48–D55, specs e CHANGELOG atualizados
- [ ] ruff, mypy, complexipy, pytest (≥ 80%), verificador de arquitetura, ESLint, build e jscpd verdes no CI
