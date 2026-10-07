# M1.4 — Análise descritiva — plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 04–07 e os contratos em `docs/plans/2026-10-03-m1-visao-geral.md`.

**Objetivo:** para qualquer coluna analisável, calcular tabela de frequências (spec 04), tendência central (05), separatrizes e "onde está meu valor?" (06) e dispersão (07), com aplicabilidade por tipo, motivo do que não se aplica, cálculo passo a passo, interpretações automáticas e fórmulas; expor em `GET /analise` e `GET /posicao`.

**Arquitetura:** domínio `analise` com módulos puros por spec (`classes`, `frequencias`, `tendencia`, `separatrizes`, `posicao`, `dispersao`) e um montador (`univariada.analisar_amostra`) que junta tudo no value object `Analise`. Os textos ficam em `textos.py` e as fórmulas em `formulas.py` (catálogo com chave estável). A fachada `ServicoAnalise` recebe o `ServicoDatasets` (ADR 0009) e transforma a coluna em `Amostra`. `figuras` volta vazio; o M1.5 preenche.

**Stack:** Python 3.12, pandas 3, numpy, FastAPI, Pydantic 2, pytest. Sem scipy neste bloco: a posição percentil é a fórmula da spec com numpy (o `mypy --strict` pede `scipy-stubs`, que não está no projeto; ver dúvidas na visão geral).

**Branch:** `feat/analise-descritiva` (sai de `develop` **depois do merge do M1.2**) → PR para `develop`.

**Prazo sugerido:** 17/10/2026. **Depende de:** M1.2. Pode andar junto com o M1.3.

**Código validado:** rodado num rascunho sobre M1.2 + M1.3 com ruff, mypy, complexipy, jscpd e pytest (284 testes no total, 99% de cobertura; `analise/` entre 91% e 100% por arquivo).

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Resultados, fórmulas e textos | `analise/resultados.py`, `formulas.py`, `textos.py`, `compartilhado/numeros.py` |
| 2 | Classes (Sturges) e tabelas de frequência | `analise/classes.py`, `frequencias.py` |
| 3 | Tendência central | `analise/tendencia.py` |
| 4 | Separatrizes e "onde está meu valor?" | `analise/separatrizes.py`, `posicao.py` |
| 5 | Dispersão | `analise/dispersao.py` |
| 6 | Montagem da análise univariada | `analise/univariada.py` |
| 7 | Fachada, erros, schemas, router | `analise/servico.py`, `erros.py`, `schemas.py`, `router.py`, `main.py` |
| 8 | Tipos do frontend, decisões, specs e CHANGELOG | `schema.d.ts`, `docs/**` |
| 9 | Verificação final, teste manual e PR | — |

### Regras que o código implementa
- **Aplicabilidade por tipo** (o frontend nunca decide): chaves de `aplicavel` = `acumulada, media, mediana, moda_czuber, proporcao, separatrizes, posicao, dispersao, variancia, cv`. Todo item que não se aplica entra em `nao_aplicavel` com o motivo no formato da spec 16 ("{medida} não se aplica a {tipo}: {motivo}."); casos de borda numéricos usam "{medida} não se aplica: {motivo}." e o CV com média zero usa o texto literal da spec 07.
- **Binária:** sem média (vem a proporção p, com sucesso = `1/sim/s/true/verdadeiro` ou a categoria menos frequente; `?sucesso=` escolhe outra); dispersão só com `p(1 − p)` e o desvio.
- **Ordinal:** mediana e separatrizes como categoria; amplitude e IQR em categorias ("de ruim a ótimo"); sem "onde está meu valor?".
- **Contínua:** classes de Sturges (`?classes=3..30` sobrescreve); `h` arredondada para cima na casa decimal dos dados; rótulo "60,0 ⊢ 65,5" (a última classe inclui o limite da direita); moda bruta e moda de Czuber.
- **Separatrizes:** `numpy.quantile(method="linear")`; percentis P1..P99 e `destaques` = P1, P5, P10, P25, P50, P75, P90, P95, P99.
- **Posição:** `PR = 100 · (nº < v + 0,5 · nº = v) / n`; quartil/decil pela região entre as marcas (limite da direita fechado); percentil = ⌈PR⌉ limitado a 1..100; `marcas` tem 3 (quartil), 9 (decil) ou os 9 destaques (percentil) — resolve a lacuna apontada no plano do M1.7.
- **Fórmulas:** cada `Medida` aplicável traz `formula` = chave do catálogo (`media`, `mediana`, `moda_czuber`, `proporcao`, `amplitude`, `variancia`, `variancia_populacional`, `desvio_padrao`, `iqr`, `cv`, `variancia_binaria`); `Analise.formulas` lista só as usadas, cada uma com `chave`, `nome`, `latex` e `texto`. O frontend acha a fórmula do card por `medida.formula` (sem depender do nome).

---

### Tarefa 1: resultados, fórmulas e textos

**Arquivos:**
- Criar: `backend/app/dominios/analise/resultados.py`, `formulas.py`, `textos.py`
- Modificar: `backend/app/compartilhado/numeros.py`, `backend/tests/compartilhado/test_numeros.py`

**Passo 1: teste do formatador novo (falha)** — acrescentar a `tests/compartilhado/test_numeros.py` (e `formatar_fixo` ao import):
```python


def test_formatar_fixo_mantem_as_casas() -> None:
    assert formatar_fixo(60.0, 1) == "60,0"
    assert formatar_fixo(1234.5, 2) == "1.234,50"
```

**Passo 2: rodar e ver falhar** — `pytest tests/compartilhado/test_numeros.py --no-cov` → FAIL (`ImportError: formatar_fixo`)

**Passo 3: implementar** — acrescentar ao fim de `app/compartilhado/numeros.py`:
```python


def formatar_fixo(valor: float, casas: int) -> str:
    """Número com casas decimais fixas: 60,0 · 1.234,50 (limites de classe)."""
    return _trocar_separadores(f"{valor:,.{casas}f}")
```

`app/dominios/analise/resultados.py` — value objects do contrato `Analise` (`Figura` já nasce aqui com o campo `rotulo`, para o Segmented da aba Gráficos):
```python
"""Value objects dos resultados da análise univariada (specs 04–07, contrato `Analise`)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

from app.compartilhado.tipos import TipoVariavel

type Valor = float | str | None
type TipoSeparatriz = Literal["quartil", "decil", "percentil"]


@dataclass(frozen=True, slots=True, eq=False)
class Amostra:
    """Valores válidos de uma coluna: números (discreta/contínua) ou textos (categóricas)."""

    coluna: str
    tipo: TipoVariavel
    valores: pd.Series
    n_faltantes: int
    ordem: tuple[str, ...] = ()

    @property
    def n(self) -> int:
        return len(self.valores)


@dataclass(frozen=True, slots=True)
class NaoAplicavel:
    item: str
    motivo: str


@dataclass(frozen=True, slots=True)
class Formula:
    chave: str
    nome: str
    latex: str
    texto: str


@dataclass(frozen=True, slots=True)
class Medida:
    """Uma medida com valor, ou não aplicável com motivo (spec 16: nunca some)."""

    valor: Valor = None
    aplicavel: bool = True
    motivo: str | None = None
    calculo: str | None = None
    interpretacao: str | None = None
    formula: str | None = None


def nao_aplicavel(motivo: str) -> Medida:
    return Medida(aplicavel=False, motivo=motivo)


@dataclass(frozen=True, slots=True)
class LinhaFrequencia:
    rotulo: str
    valor: Valor
    fi: int
    fri: float
    fr_pct: float
    limite_inferior: float | None = None
    limite_superior: float | None = None
    ponto_medio: float | None = None
    f_acum: int | None = None
    fr_acum: float | None = None
    fr_acum_pct: float | None = None


@dataclass(frozen=True, slots=True)
class TabelaFrequencia:
    tipo: TipoVariavel
    linhas: tuple[LinhaFrequencia, ...]
    total: int
    acumulada_aplicavel: bool
    motivo_acumulada: str | None = None
    indice_modal: int | None = None
    k: int | None = None
    k_sturges: int | None = None
    h: float | None = None
    metodo_classes: Literal["sturges", "usuario"] | None = None


@dataclass(frozen=True, slots=True)
class Moda:
    valores: tuple[float | str, ...]
    classificacao: Literal["amodal", "unimodal", "bimodal", "multimodal"]
    interpretacao: str


@dataclass(frozen=True, slots=True)
class Tendencia:
    media: Medida
    mediana: Medida
    moda: Moda
    moda_czuber: Medida
    proporcao: Medida


@dataclass(frozen=True, slots=True)
class ValorSeparatriz:
    rotulo: str
    p: float
    valor: float | str


@dataclass(frozen=True, slots=True)
class Separatrizes:
    quartis: tuple[ValorSeparatriz, ...]
    decis: tuple[ValorSeparatriz, ...]
    percentis: tuple[ValorSeparatriz, ...]
    destaques: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Dispersao:
    amplitude: Medida
    variancia: Medida
    variancia_populacional: Medida
    desvio_padrao: Medida
    desvio_padrao_populacional: Medida
    iqr: Medida
    cv: Medida
    classificacao_cv: Literal["baixa", "media", "alta"] | None = None


@dataclass(frozen=True, slots=True)
class Posicao:
    valor: float
    tipo: TipoSeparatriz
    regiao: str
    indice: int
    limite_inferior: float | None
    limite_superior: float | None
    posicao_percentil: float
    fora_da_faixa: Literal["abaixo", "acima"] | None
    minimo: float
    maximo: float
    marcas: tuple[ValorSeparatriz, ...]
    frase: str


@dataclass(frozen=True, slots=True)
class Figura:
    """Figura Plotly pronta (M1.5); `dados` = {"data": [...], "layout": {...}} sem template."""

    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Analise:
    coluna: str
    tipo: TipoVariavel
    n: int
    n_faltantes: int
    aplicavel: Mapping[str, bool]
    nao_aplicavel: tuple[NaoAplicavel, ...]
    frequencias: TabelaFrequencia
    tendencia: Tendencia
    separatrizes: Separatrizes | None
    dispersao: Dispersao | None
    interpretacoes: tuple[str, ...]
    formulas: tuple[Formula, ...]
    figuras: tuple[Figura, ...] = ()
```

`app/dominios/analise/formulas.py`
```python
"""Catálogo de fórmulas (LaTeX + texto) usadas na análise univariada (specs 04–07)."""

from app.dominios.analise.resultados import Formula


def _f(chave: str, nome: str, latex: str, texto: str) -> Formula:
    return Formula(chave, nome, latex, texto)


FORMULAS: dict[str, Formula] = {
    f.chave: f
    for f in (
        _f("frequencia_relativa", "Frequência relativa", r"fr_i = \frac{f_i}{n}", "frᵢ = fᵢ / n"),
        _f(
            "frequencia_acumulada",
            "Frequência acumulada",
            r"F_i = \sum_{j \le i} f_j",
            "Fᵢ = Σⱼ≤ᵢ fⱼ",
        ),
        _f(
            "sturges",
            "Número de classes (Sturges)",
            r"k = \lceil 1 + 3{,}322 \log_{10} n \rceil",
            "k = ⌈1 + 3,322 · log₁₀ n⌉",
        ),
        _f(
            "amplitude_classe",
            "Amplitude da classe",
            r"h = \frac{x_{max} - x_{min}}{k}",
            "h = (xₘₐₓ − xₘᵢₙ) / k",
        ),
        _f("ponto_medio", "Ponto médio", r"x_i = \frac{L_i + L_{i+1}}{2}", "xᵢ = (Lᵢ + Lᵢ₊₁) / 2"),
        _f("media", "Média", r"\bar{x} = \frac{\sum x_i}{n}", "x̄ = Σxᵢ / n"),
        _f(
            "mediana",
            "Mediana",
            r"Md = x_{\left(\frac{n+1}{2}\right)}",
            "Md = valor central dos dados ordenados",
        ),
        _f("moda", "Moda", r"Mo = \text{valor de maior } f_i", "Mo = valor mais frequente"),
        _f(
            "moda_czuber",
            "Moda de Czuber",
            r"Mo = L_i + \frac{\Delta_1}{\Delta_1 + \Delta_2} \cdot h",
            "Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h",
        ),
        _f("proporcao", "Proporção", r"p = \frac{\text{sucessos}}{n}", "p = nº de sucessos / n"),
        _f(
            "quantil",
            "Separatriz (interpolação linear)",
            r"Q_p = x_{(\lfloor h \rfloor)} + (h - \lfloor h \rfloor)"
            r"(x_{(\lfloor h \rfloor + 1)} - x_{(\lfloor h \rfloor)}),\ h = (n-1)p",
            "Qp = x₍⌊h⌋₎ + (h − ⌊h⌋)·(x₍⌊h⌋+1₎ − x₍⌊h⌋₎), h = (n − 1)·p",
        ),
        _f(
            "posicao_percentil",
            "Posição percentil",
            r"PR = 100 \cdot \frac{\#(x_i < v) + 0{,}5 \cdot \#(x_i = v)}{n}",
            "PR = 100 · (nº de xᵢ < v + 0,5 · nº de xᵢ = v) / n",
        ),
        _f("amplitude", "Amplitude", r"A = x_{max} - x_{min}", "A = xₘₐₓ − xₘᵢₙ"),
        _f(
            "variancia",
            "Variância amostral",
            r"s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}",
            "s² = Σ(xᵢ − x̄)² / (n − 1)",
        ),
        _f(
            "variancia_populacional",
            "Variância populacional",
            r"\sigma^2 = \frac{\sum (x_i - \mu)^2}{n}",
            "σ² = Σ(xᵢ − μ)² / n",
        ),
        _f("desvio_padrao", "Desvio padrão", r"s = \sqrt{s^2}", "s = √s²"),
        _f("iqr", "Amplitude interquartil", r"IQR = Q_3 - Q_1", "IQR = Q3 − Q1"),
        _f(
            "cv",
            "Coeficiente de variação",
            r"CV = \frac{s}{\bar{x}} \cdot 100\%",
            "CV = (s / x̄) · 100%",
        ),
        _f("variancia_binaria", "Variância (binária)", r"Var = p(1 - p)", "Var = p(1 − p)"),
    )
}


def formulas_usadas(chaves: list[str | None]) -> tuple[Formula, ...]:
    """Fórmulas citadas pelas medidas aplicáveis, sem repetir, na ordem do catálogo."""
    pedidas = set(chaves)
    return tuple(f for chave, f in FORMULAS.items() if chave in pedidas)
```

`app/dominios/analise/textos.py`
```python
"""Textos da análise: "não se aplica", interpretações e frases (spec 16)."""

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.tipos import TipoVariavel

LIMIAR_SIMETRIA = 0.1
NOMES_NO_PLURAL = frozenset({"separatrizes"})

TIPO_LEGIVEL = {
    TipoVariavel.NOMINAL: "qualitativas nominais",
    TipoVariavel.ORDINAL: "qualitativas ordinais",
    TipoVariavel.BINARIA: "binárias",
    TipoVariavel.DISCRETA: "quantitativas discretas",
    TipoVariavel.CONTINUA: "quantitativas contínuas",
    TipoVariavel.IDENTIFICADOR: "identificadores",
}

MOTIVOS = {
    "acumulada": 'as categorias não têm ordem para somar "até aqui"',
    "media": "não dá para somar categorias",
    "media_binaria": "use a proporção, que é a média de uma variável 0/1",
    "mediana": "as categorias não têm ordem",
    "moda_czuber": "ela só vale para dados contínuos agrupados em classes",
    "proporcao": "ela só vale para variáveis com dois valores",
    "separatrizes": "as categorias não têm ordem para dividir em partes",
    "posicao": "precisa de valores numéricos",
    "dispersao": "precisa de distâncias entre números",
    "distancias": "precisa de distâncias entre números",
    "poucos_valores": "precisa de pelo menos 2 valores",
}

NOMES = {
    "acumulada": "Frequência acumulada",
    "media": "Média",
    "mediana": "Mediana",
    "moda_czuber": "Moda de Czuber",
    "proporcao": "Proporção",
    "separatrizes": "Separatrizes",
    "posicao": '"Onde está meu valor?"',
    "dispersao": "Dispersão",
    "amplitude": "Amplitude",
    "variancia": "Variância",
    "variancia_populacional": "Variância populacional",
    "desvio_padrao": "Desvio padrão",
    "desvio_padrao_populacional": "Desvio padrão populacional",
    "iqr": "Amplitude interquartil",
    "cv": "Coeficiente de variação",
}


def nao_se_aplica(item: str, tipo: TipoVariavel, motivo: str) -> str:
    """ "{medida} não se aplica a {tipo}: {motivo}." (spec 16)."""
    verbo = "se aplicam" if item in NOMES_NO_PLURAL else "se aplica"
    return f"{NOMES[item]} não {verbo} a {TIPO_LEGIVEL[tipo]}: {MOTIVOS[motivo]}."


def nao_calculavel(item: str, motivo: str) -> str:
    """Caso de borda numérico (spec 07), ex.: "Variância não se aplica: precisa de 2 valores"."""
    return f"{NOMES[item]} não se aplica: {MOTIVOS[motivo]}."


def interpretar_media_mediana(media: float, mediana: float, desvio: float) -> str | None:
    """Spec 05: compara média e mediana em relação ao desvio padrão."""
    if desvio == 0:
        return None
    diferenca = formatar_numero(abs(media - mediana))
    if abs(media - mediana) / desvio < LIMIAR_SIMETRIA:
        return (
            f"Média e mediana próximas (diferença de {diferenca}): a distribuição parece simétrica."
        )
    if media > mediana:
        return "Média maior que a mediana: há valores altos puxando a média (assimetria à direita)."
    return "Média menor que a mediana: há valores baixos puxando a média (assimetria à esquerda)."


CV_MEDIA_ZERO = "O CV não pode ser calculado porque a média é zero."
```

**Passo 4: rodar e ver passar** — `pytest tests/compartilhado --no-cov`; `ruff check . && mypy app`

**Passo 5: commit**
```bash
git add app/compartilhado/numeros.py tests/compartilhado/test_numeros.py app/dominios/analise/resultados.py app/dominios/analise/formulas.py app/dominios/analise/textos.py
git commit -m "feat(analise): adiciona resultados, catálogo de fórmulas e textos de não aplicável"
```

---

### Tarefa 2: classes (Sturges) e tabelas de frequência (spec 04)

**Arquivos:**
- Criar: `backend/app/dominios/analise/classes.py`, `frequencias.py`
- Teste: `backend/tests/dominios/analise/__init__.py` (vazio), `conftest.py`, `test_classes.py`, `test_frequencias.py`

**Passo 1: escrever os testes (falham)**

`tests/dominios/analise/conftest.py` — fábrica de amostras usada por todos os testes do domínio:
```python
from collections.abc import Callable, Sequence

import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.resultados import Amostra

type CriarAmostra = Callable[..., Amostra]

ESCALA_SATISFACAO = ("ruim", "regular", "bom", "ótimo")


def _criar(
    tipo: TipoVariavel, valores: Sequence[float | str], ordem: tuple[str, ...] = ()
) -> Amostra:
    serie = pd.Series(list(valores), index=pd.RangeIndex(1, len(valores) + 1))
    return Amostra("x", tipo, serie, 0, ordem)


@pytest.fixture
def criar_amostra() -> CriarAmostra:
    """Fábrica de amostras: criar_amostra(TipoVariavel.CONTINUA, [1.5, 2.0])."""
    return _criar
```

`tests/dominios/analise/test_classes.py`
```python
import pandas as pd
import pytest

from app.dominios.analise.classes import agrupar, amplitude_de_classe, k_sturges

DEZ_VALORES = pd.Series([2.0, 3.5, 4.0, 5.5, 6.0, 7.5, 8.0, 9.5, 10.0, 11.5])


@pytest.mark.parametrize(("n", "k"), [(10, 5), (227, 9), (230, 9), (1, 1), (1000, 11)])
def test_k_de_sturges(n: int, k: int) -> None:
    assert k_sturges(n) == k


def test_amplitude_arredonda_para_cima_na_casa_dos_dados() -> None:
    # Exemplo do design (4b): AT = 49,1 e k = 9 → h = 5,4555… → 5,5.
    assert amplitude_de_classe(49.1, 9, 1) == 5.5
    assert amplitude_de_classe(9.5, 5, 1) == 1.9


def test_classes_por_sturges() -> None:
    agrupamento = agrupar(DEZ_VALORES, None)

    assert (agrupamento.k, agrupamento.h, agrupamento.metodo) == (5, 1.9, "sturges")
    assert [c.inferior for c in agrupamento.classes] == [2.0, 3.9, 5.8, 7.7, 9.6]
    assert [c.frequencia for c in agrupamento.classes] == [2, 2, 2, 2, 2]
    assert agrupamento.classes[0].ponto_medio == pytest.approx(2.95)


def test_classes_escolhidas_pelo_usuario() -> None:
    agrupamento = agrupar(DEZ_VALORES, 3)

    assert (agrupamento.k, agrupamento.h, agrupamento.metodo) == (3, 3.2, "usuario")
    assert [c.frequencia for c in agrupamento.classes] == [3, 4, 3]


def test_limite_da_esquerda_entra_e_ultima_classe_e_fechada() -> None:
    agrupamento = agrupar(pd.Series([0.0, 1.0, 2.0, 3.0, 4.0]), 2)

    assert [c.frequencia for c in agrupamento.classes] == [2, 3]


def test_valores_iguais_formam_uma_classe() -> None:
    agrupamento = agrupar(pd.Series([5.0, 5.0, 5.0]), None)

    assert (agrupamento.k, agrupamento.h) == (1, 0.0)
    assert agrupamento.classes[0].frequencia == 3
```

`tests/dominios/analise/test_frequencias.py`
```python
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.frequencias import tabela_frequencia
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra


def test_nominal_ordena_por_frequencia_e_nao_acumula(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "b", "c", "c", "c"]))

    assert [(linha.rotulo, linha.fi) for linha in tabela.linhas] == [("c", 3), ("b", 2), ("a", 1)]
    assert tabela.linhas[0].fri == 0.5
    assert tabela.linhas[0].fr_pct == 50
    assert tabela.linhas[0].f_acum is None
    assert tabela.acumulada_aplicavel is False
    assert tabela.motivo_acumulada == (
        "Frequência acumulada não se aplica a qualitativas nominais: "
        'as categorias não têm ordem para somar "até aqui".'
    )
    assert (tabela.total, tabela.indice_modal) == (6, 0)


def test_ordinal_segue_a_escala_e_acumula(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(
        TipoVariavel.ORDINAL, ["bom", "ruim", "bom", "ótimo"], ESCALA_SATISFACAO
    )

    tabela = tabela_frequencia(amostra)

    assert [(linha.rotulo, linha.fi, linha.f_acum) for linha in tabela.linhas] == [
        ("ruim", 1, 1),
        ("bom", 2, 3),
        ("ótimo", 1, 4),
    ]
    assert tabela.linhas[-1].fr_acum == 1
    assert tabela.indice_modal == 1


def test_discreta_em_ordem_crescente(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.DISCRETA, [3.0, 1.0, 2.0, 3.0, 2.0, 3.0]))

    assert [(linha.rotulo, linha.fi, linha.f_acum) for linha in tabela.linhas] == [
        ("1", 1, 1),
        ("2", 2, 3),
        ("3", 3, 6),
    ]
    assert tabela.linhas[1].fr_acum_pct == pytest.approx(50)


def test_continua_em_classes_com_notacao_da_spec(criar_amostra: CriarAmostra) -> None:
    valores = [2.0, 3.5, 4.0, 5.5, 6.0, 7.5, 8.0, 9.5, 10.0, 11.5]

    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, valores))

    primeira = tabela.linhas[0]
    assert primeira.rotulo == "2,0 ⊢ 3,9"
    assert (primeira.limite_inferior, primeira.limite_superior) == (2.0, 3.9)
    assert primeira.ponto_medio == pytest.approx(2.95)
    assert (tabela.k, tabela.k_sturges, tabela.h, tabela.metodo_classes) == (5, 5, 1.9, "sturges")
    assert tabela.linhas[-1].f_acum == 10


def test_continua_com_classes_do_usuario(criar_amostra: CriarAmostra) -> None:
    valores = [2.0, 3.5, 4.0, 5.5, 6.0, 7.5, 8.0, 9.5, 10.0, 11.5]

    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, valores), classes=3)

    assert (tabela.k, tabela.metodo_classes) == (3, "usuario")
    assert tabela.indice_modal == 1


def test_binaria_mostra_as_duas_categorias(criar_amostra: CriarAmostra) -> None:
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.BINARIA, ["F", "M", "M"]))

    assert [linha.rotulo for linha in tabela.linhas] == ["M", "F"]
    assert tabela.acumulada_aplicavel is False
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/analise --no-cov` → FAIL

**Passo 3: implementar**

`app/dominios/analise/classes.py`
```python
"""Classes (intervalos) para variáveis contínuas: Sturges, amplitude e contagem (spec 04)."""

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.compartilhado.series import casas_decimais

MIN_CLASSES = 3
MAX_CLASSES = 30
MAX_CASAS = 4
_ARREDONDAMENTO_POSICAO = 9


@dataclass(frozen=True, slots=True)
class Classe:
    inferior: float
    superior: float
    frequencia: int

    @property
    def ponto_medio(self) -> float:
        return (self.inferior + self.superior) / 2


@dataclass(frozen=True, slots=True)
class Agrupamento:
    classes: tuple[Classe, ...]
    k: int
    k_sturges: int
    h: float
    casas: int
    metodo: str


def k_sturges(n: int) -> int:
    """k = ⌈1 + 3,322 · log₁₀ n⌉."""
    return math.ceil(1 + 3.322 * math.log10(n)) if n > 0 else 1


def amplitude_de_classe(amplitude_total: float, k: int, casas: int) -> float:
    """h = AT / k, arredondada para cima na casa decimal dos dados."""
    escala = 10.0**casas
    return math.ceil(round(amplitude_total / k * escala, _ARREDONDAMENTO_POSICAO)) / escala


def _contar(numeros: pd.Series, minimo: float, h: float, k: int) -> np.ndarray:
    posicoes = np.floor(np.round((numeros.to_numpy() - minimo) / h, _ARREDONDAMENTO_POSICAO))
    indices = np.clip(posicoes.astype(int), 0, k - 1)
    return np.bincount(indices, minlength=k)


def agrupar(numeros: pd.Series, classes: int | None) -> Agrupamento:
    """Classes [Lᵢ, Lᵢ + h); a última inclui o limite da direita."""
    valores = numeros.dropna()
    sturges = k_sturges(len(valores))
    minimo, maximo = float(valores.min()), float(valores.max())
    casas = min(casas_decimais(valores), MAX_CASAS)
    if maximo == minimo:
        unica = Classe(minimo, maximo, len(valores))
        return Agrupamento((unica,), 1, sturges, 0.0, casas, "sturges")
    k = classes if classes is not None else sturges
    h = amplitude_de_classe(maximo - minimo, k, casas)
    contagens = _contar(valores, minimo, h, k)
    limites = [round(minimo + i * h, MAX_CASAS + 2) for i in range(k + 1)]
    resultado = tuple(Classe(limites[i], limites[i + 1], int(contagens[i])) for i in range(k))
    metodo = "sturges" if classes is None else "usuario"
    return Agrupamento(resultado, k, sturges, h, max(casas, casas_decimais(pd.Series([h]))), metodo)
```

`app/dominios/analise/frequencias.py` — Strategy: `TABELAS` mapeia tipo → função.
```python
"""Tabelas de frequência por tipo de variável (spec 04). Strategy: tipo → função."""

from collections.abc import Callable
from dataclasses import dataclass
from itertools import accumulate

import pandas as pd

from app.compartilhado.numeros import formatar_fixo, formatar_numero
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.classes import Agrupamento, Classe, agrupar
from app.dominios.analise.resultados import Amostra, LinhaFrequencia, TabelaFrequencia

SIMBOLO_CLASSE = "⊢"
PORCENTO = 100


@dataclass(frozen=True, slots=True)
class _Contagem:
    rotulo: str
    valor: float | str
    fi: int
    classe: Classe | None = None


def _linha(contagem: _Contagem, f_acum: int, n: int, acumular: bool) -> LinhaFrequencia:
    classe = contagem.classe
    return LinhaFrequencia(
        rotulo=contagem.rotulo,
        valor=contagem.valor,
        fi=contagem.fi,
        fri=contagem.fi / n,
        fr_pct=contagem.fi / n * PORCENTO,
        limite_inferior=classe.inferior if classe else None,
        limite_superior=classe.superior if classe else None,
        ponto_medio=classe.ponto_medio if classe else None,
        f_acum=f_acum if acumular else None,
        fr_acum=f_acum / n if acumular else None,
        fr_acum_pct=f_acum / n * PORCENTO if acumular else None,
    )


def _linhas(contagens: list[_Contagem], n: int, acumular: bool) -> tuple[LinhaFrequencia, ...]:
    acumuladas = accumulate(c.fi for c in contagens)
    return tuple(_linha(c, f, n, acumular) for c, f in zip(contagens, acumuladas, strict=True))


def _indice_modal(contagens: list[_Contagem]) -> int | None:
    if not contagens:
        return None
    maior = max(c.fi for c in contagens)
    return next(i for i, c in enumerate(contagens) if c.fi == maior)


def _tabela(amostra: Amostra, contagens: list[_Contagem], acumular: bool) -> TabelaFrequencia:
    motivo = None if acumular else textos.nao_se_aplica("acumulada", amostra.tipo, "acumulada")
    return TabelaFrequencia(
        tipo=amostra.tipo,
        linhas=_linhas(contagens, amostra.n, acumular),
        total=amostra.n,
        acumulada_aplicavel=acumular,
        motivo_acumulada=motivo,
        indice_modal=_indice_modal(contagens),
    )


def _por_frequencia(amostra: Amostra, _classes: int | None) -> TabelaFrequencia:
    """Nominal e binária: categorias da mais para a menos frequente, sem acumulada."""
    contagens = amostra.valores.value_counts()
    ordenadas = sorted(contagens.items(), key=lambda item: (-int(item[1]), str(item[0])))
    linhas = [_Contagem(str(c), str(c), int(fi)) for c, fi in ordenadas]
    return _tabela(amostra, linhas, acumular=False)


def ordem_completa(amostra: Amostra) -> list[str]:
    """Ordem da escala; categorias fora dela (não deveria haver) vão para o fim."""
    presentes = {str(v) for v in amostra.valores.unique()}
    extras = sorted(presentes - set(amostra.ordem))
    return [c for c in amostra.ordem if c in presentes] + extras


def _ordinal(amostra: Amostra, _classes: int | None) -> TabelaFrequencia:
    contagens = amostra.valores.astype(str).value_counts()
    linhas = [_Contagem(c, c, int(contagens[c])) for c in ordem_completa(amostra)]
    return _tabela(amostra, linhas, acumular=True)


def _discreta(amostra: Amostra, _classes: int | None) -> TabelaFrequencia:
    contagens = amostra.valores.value_counts().sort_index()
    pares = zip(contagens.index.tolist(), contagens.tolist(), strict=True)
    linhas = [_Contagem(formatar_numero(float(v)), float(v), int(fi)) for v, fi in pares]
    return _tabela(amostra, linhas, acumular=True)


def rotulo_classe(classe: Classe, casas: int) -> str:
    """Notação da spec 04: "10,0 ⊢ 20,0"."""
    inferior, superior = (
        formatar_fixo(classe.inferior, casas),
        formatar_fixo(classe.superior, casas),
    )
    return f"{inferior} {SIMBOLO_CLASSE} {superior}"


def _continua(amostra: Amostra, classes: int | None) -> TabelaFrequencia:
    agrupamento: Agrupamento = agrupar(amostra.valores, classes)
    linhas = [
        _Contagem(rotulo_classe(c, agrupamento.casas), c.ponto_medio, c.frequencia, c)
        for c in agrupamento.classes
    ]
    base = _tabela(amostra, linhas, acumular=True)
    return TabelaFrequencia(
        tipo=base.tipo,
        linhas=base.linhas,
        total=base.total,
        acumulada_aplicavel=True,
        indice_modal=base.indice_modal,
        k=agrupamento.k,
        k_sturges=agrupamento.k_sturges,
        h=agrupamento.h,
        metodo_classes="usuario" if agrupamento.metodo == "usuario" else "sturges",
    )


TABELAS: dict[TipoVariavel, Callable[[Amostra, int | None], TabelaFrequencia]] = {
    TipoVariavel.NOMINAL: _por_frequencia,
    TipoVariavel.BINARIA: _por_frequencia,
    TipoVariavel.ORDINAL: _ordinal,
    TipoVariavel.DISCRETA: _discreta,
    TipoVariavel.CONTINUA: _continua,
}


def tabela_frequencia(amostra: Amostra, classes: int | None = None) -> TabelaFrequencia:
    """fᵢ, frᵢ = fᵢ/n, fr% e, quando há ordem, Fᵢ = Σfⱼ e Frᵢ = Fᵢ/n."""
    return TABELAS[amostra.tipo](amostra, classes)


def contagens_por_categoria(amostra: Amostra) -> pd.Series:
    """Frequências na ordem em que a tabela mostra (usado por moda e separatrizes ordinais)."""
    tabela = tabela_frequencia(amostra)
    return pd.Series({linha.rotulo: linha.fi for linha in tabela.linhas})
```

**Passo 4: rodar e ver passar** — `pytest tests/dominios/analise -v --no-cov`

**Passo 5: commit**
```bash
git add app/dominios/analise/classes.py app/dominios/analise/frequencias.py tests/dominios/analise
git commit -m "feat(analise): calcula tabelas de frequência por tipo com classes de Sturges"
```

---

### Tarefa 3: tendência central (spec 05)

**Arquivos:**
- Criar: `backend/app/dominios/analise/tendencia.py`
- Teste: `backend/tests/dominios/analise/test_tendencia.py`

**Passo 1: escrever os testes (falham)** — o teste da moda de Czuber usa as classes do print 4b (Mo ≈ 70,27):
```python
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.resultados import LinhaFrequencia, TabelaFrequencia
from app.dominios.analise.tendencia import (
    media,
    mediana,
    moda,
    moda_czuber,
    proporcao,
    sucesso_padrao,
)
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra


def test_media_com_calculo(criar_amostra: CriarAmostra) -> None:
    resultado = media(criar_amostra(TipoVariavel.DISCRETA, [2.0, 4.0, 6.0]))

    assert resultado.valor == 4
    assert resultado.calculo == "Σxᵢ / n = 12 / 3 = 4"
    assert resultado.formula == "media"


@pytest.mark.parametrize(
    ("tipo", "motivo"),
    [
        (
            TipoVariavel.NOMINAL,
            "Média não se aplica a qualitativas nominais: não dá para somar categorias.",
        ),
        (
            TipoVariavel.BINARIA,
            "Média não se aplica a binárias: use a proporção, que é a média de uma variável 0/1.",
        ),
    ],
)
def test_media_nao_se_aplica_a_categorias(
    criar_amostra: CriarAmostra, tipo: TipoVariavel, motivo: str
) -> None:
    resultado = media(criar_amostra(tipo, ["a", "b"]))

    assert (resultado.aplicavel, resultado.motivo, resultado.valor) == (False, motivo, None)


def test_mediana_par_e_media_dos_centrais(criar_amostra: CriarAmostra) -> None:
    assert mediana(criar_amostra(TipoVariavel.CONTINUA, [4.0, 1.0, 3.0, 2.0])).valor == 2.5


def test_mediana_ordinal_e_a_categoria_da_posicao_central(criar_amostra: CriarAmostra) -> None:
    valores = ["ruim", "bom", "bom", "ótimo", "regular"]

    resultado = mediana(criar_amostra(TipoVariavel.ORDINAL, valores, ESCALA_SATISFACAO))

    assert resultado.valor == "bom"
    assert resultado.calculo == "posição (n + 1) / 2 = 3 → bom"


def test_mediana_nao_se_aplica_a_nominal(criar_amostra: CriarAmostra) -> None:
    assert mediana(criar_amostra(TipoVariavel.NOMINAL, ["a", "b"])).aplicavel is False


@pytest.mark.parametrize(
    ("valores", "esperado", "classificacao"),
    [
        ([1.0, 2.0, 2.0, 3.0], (2.0,), "unimodal"),
        ([1.0, 1.0, 2.0, 2.0, 3.0], (1.0, 2.0), "bimodal"),
        ([1.0, 2.0, 3.0], (), "amodal"),
        ([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0], (1.0, 2.0, 3.0), "multimodal"),
    ],
)
def test_moda_e_classificacao(
    criar_amostra: CriarAmostra,
    valores: list[float],
    esperado: tuple[float, ...],
    classificacao: str,
) -> None:
    resultado = moda(criar_amostra(TipoVariavel.DISCRETA, valores))

    assert (resultado.valores, resultado.classificacao) == (esperado, classificacao)


def test_frases_da_moda(criar_amostra: CriarAmostra) -> None:
    uni = moda(criar_amostra(TipoVariavel.NOMINAL, ["Goiânia", "Goiânia", "Anápolis"]))
    bi = moda(criar_amostra(TipoVariavel.DISCRETA, [1.0, 1.0, 2.0, 2.0, 3.0]))

    assert uni.interpretacao == "O valor mais frequente é Goiânia (2 vezes)."
    assert bi.interpretacao == "Há 2 modas: 1 e 2 (2 vezes cada)."


def _tabela_do_design() -> TabelaFrequencia:
    """Classes do print 4b: h = 5,5 e classe modal 65,5 ⊢ 71,0 (fᵢ = 49)."""
    frequencias = [4, 9, 20, 36, 49, 47, 34, 18, 10]
    linhas = tuple(
        LinhaFrequencia(
            rotulo="",
            valor=None,
            fi=fi,
            fri=0.0,
            fr_pct=0.0,
            limite_inferior=43.5 + i * 5.5,
            limite_superior=49.0 + i * 5.5,
            ponto_medio=46.25 + i * 5.5,
        )
        for i, fi in enumerate(frequencias)
    )
    return TabelaFrequencia(
        TipoVariavel.CONTINUA, linhas, 227, True, indice_modal=4, k=9, k_sturges=9, h=5.5
    )


def test_moda_de_czuber(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.CONTINUA, [1.0, 2.0])

    resultado = moda_czuber(amostra, _tabela_do_design())

    # Mo = 65,5 + [13 / (13 + 2)] · 5,5 = 70,27
    assert resultado.valor == pytest.approx(70.2667, abs=1e-4)
    assert resultado.calculo == "Mo = 65,5 + [13 / (13 + 2)] · 5,5 = 70,27"


def test_moda_de_czuber_so_para_continua(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.DISCRETA, [1.0, 2.0])

    assert moda_czuber(amostra, _tabela_do_design()).aplicavel is False


@pytest.mark.parametrize(
    ("valores", "sucesso"),
    [(["sim", "não", "sim"], "sim"), (["0", "1", "0"], "1"), (["A", "B", "B"], "A")],
)
def test_sucesso_padrao(criar_amostra: CriarAmostra, valores: list[str], sucesso: str) -> None:
    assert sucesso_padrao(criar_amostra(TipoVariavel.BINARIA, valores).valores) == sucesso


def test_proporcao(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.BINARIA, ["sim", "não", "sim", "sim"])

    padrao = proporcao(amostra, None)
    escolhida = proporcao(amostra, "não")

    assert padrao.valor == 0.75
    assert padrao.calculo == "p = 3 / 4 = 0,75"
    assert padrao.interpretacao == '75,0% dos valores são "sim".'
    assert escolhida.valor == 0.25


def test_proporcao_so_para_binaria(criar_amostra: CriarAmostra) -> None:
    assert proporcao(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "c"]), None).aplicavel is False
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/analise/test_tendencia.py --no-cov`

**Passo 3: implementar `app/dominios/analise/tendencia.py`**
```python
"""Medidas de tendência central: média, mediana, moda, moda de Czuber e proporção (spec 05)."""

from typing import Literal

import pandas as pd

from app.compartilhado.numeros import formatar_inteiro, formatar_numero, formatar_percentual
from app.compartilhado.textos import juntar_lista, normalizar_texto
from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.frequencias import ordem_completa
from app.dominios.analise.resultados import (
    Amostra,
    Medida,
    Moda,
    TabelaFrequencia,
    Tendencia,
    nao_aplicavel,
)

SUCESSOS_PADRAO = frozenset({"1", "sim", "s", "true", "verdadeiro"})
VALORES_BIMODAL = 2


def media(amostra: Amostra) -> Medida:
    """x̄ = Σxᵢ / n."""
    if amostra.tipo == TipoVariavel.BINARIA:
        return nao_aplicavel(textos.nao_se_aplica("media", amostra.tipo, "media_binaria"))
    if amostra.tipo not in TIPOS_NUMERICOS:
        return nao_aplicavel(textos.nao_se_aplica("media", amostra.tipo, "media"))
    soma = float(amostra.valores.sum())
    valor = soma / amostra.n
    calculo = f"Σxᵢ / n = {formatar_numero(soma)} / {amostra.n} = {formatar_numero(valor)}"
    return Medida(valor, calculo=calculo, formula="media")


def _posicao_central(n: int) -> float:
    return (n + 1) / 2


def _mediana_ordinal(amostra: Amostra) -> Medida:
    """Categoria que contém a posição (n + 1)/2 na ordem da escala."""
    posicao = _posicao_central(amostra.n)
    contagens = amostra.valores.astype(str).value_counts()
    acumulada = 0
    for categoria in ordem_completa(amostra):
        acumulada += int(contagens.get(categoria, 0))
        if acumulada >= posicao:
            calculo = f"posição (n + 1) / 2 = {formatar_numero(posicao)} → {categoria}"
            return Medida(categoria, calculo=calculo, formula="mediana")
    return nao_aplicavel(textos.nao_se_aplica("mediana", amostra.tipo, "mediana"))


def mediana(amostra: Amostra) -> Medida:
    """Valor central dos dados ordenados; n par → média dos dois centrais."""
    if amostra.tipo == TipoVariavel.ORDINAL:
        return _mediana_ordinal(amostra)
    if amostra.tipo not in TIPOS_NUMERICOS:
        return nao_aplicavel(textos.nao_se_aplica("mediana", amostra.tipo, "mediana"))
    valor = float(amostra.valores.median())
    posicao = formatar_numero(_posicao_central(amostra.n))
    calculo = f"posição (n + 1) / 2 = {posicao} → {formatar_numero(valor)}"
    return Medida(valor, calculo=calculo, formula="mediana")


def _texto(valor: float | str) -> str:
    return formatar_numero(valor) if isinstance(valor, float) else valor


def _valor_da_moda(valor: object, numerica: bool) -> float | str:
    return float(str(valor)) if numerica else str(valor)


def moda(amostra: Amostra) -> Moda:
    """Valor(es) de maior frequência; amodal se todos aparecem igual."""
    contagens = amostra.valores.value_counts()
    maior = int(contagens.max())
    numerica = amostra.tipo in TIPOS_NUMERICOS
    modas = tuple(_valor_da_moda(v, numerica) for v in sorted(contagens[contagens == maior].index))
    vezes = f"{formatar_inteiro(maior)} {'vez' if maior == 1 else 'vezes'}"
    if len(contagens) > 1 and len(modas) == len(contagens):
        frase = "Não há moda: todos os valores aparecem o mesmo número de vezes."
        return Moda((), "amodal", frase)
    if len(modas) == 1:
        return Moda(modas, "unimodal", f"O valor mais frequente é {_texto(modas[0])} ({vezes}).")
    lista = juntar_lista([_texto(m) for m in modas])
    classificacao: Literal["bimodal", "multimodal"] = (
        "bimodal" if len(modas) == VALORES_BIMODAL else "multimodal"
    )
    return Moda(modas, classificacao, f"Há {len(modas)} modas: {lista} ({vezes} cada).")


def moda_czuber(amostra: Amostra, tabela: TabelaFrequencia) -> Medida:
    """Mo = Lᵢ + [Δ₁ / (Δ₁ + Δ₂)] · h, na classe modal."""
    if amostra.tipo != TipoVariavel.CONTINUA or tabela.indice_modal is None or tabela.h is None:
        return nao_aplicavel(textos.nao_se_aplica("moda_czuber", amostra.tipo, "moda_czuber"))
    linhas, i = tabela.linhas, tabela.indice_modal
    modal = linhas[i]
    delta_1 = modal.fi - (linhas[i - 1].fi if i > 0 else 0)
    delta_2 = modal.fi - (linhas[i + 1].fi if i + 1 < len(linhas) else 0)
    inferior = modal.limite_inferior or 0.0
    if delta_1 + delta_2 == 0:
        return Medida(modal.ponto_medio, calculo="Δ₁ + Δ₂ = 0: usamos o ponto médio da classe.")
    valor = inferior + delta_1 / (delta_1 + delta_2) * tabela.h
    calculo = (
        f"Mo = {formatar_numero(inferior)} + [{delta_1} / ({delta_1} + {delta_2})] · "
        f"{formatar_numero(tabela.h)} = {formatar_numero(valor)}"
    )
    return Medida(valor, calculo=calculo, formula="moda_czuber")


def sucesso_padrao(valores: pd.Series) -> str:
    """1, sim, s, true ou verdadeiro; senão a categoria menos frequente (spec 05)."""
    categorias = sorted(str(v) for v in valores.unique())
    conhecida = next((c for c in categorias if normalizar_texto(c) in SUCESSOS_PADRAO), None)
    if conhecida is not None:
        return conhecida
    contagens = valores.astype(str).value_counts()
    return min(categorias, key=lambda c: (int(contagens[c]), c))


def proporcao(amostra: Amostra, sucesso: str | None) -> Medida:
    """p = nº de sucessos / n (só para binárias)."""
    if amostra.tipo != TipoVariavel.BINARIA:
        return nao_aplicavel(textos.nao_se_aplica("proporcao", amostra.tipo, "proporcao"))
    textos_validos = amostra.valores.astype(str)
    escolhida = sucesso if sucesso in set(textos_validos) else sucesso_padrao(textos_validos)
    sucessos = int((textos_validos == escolhida).sum())
    p = sucessos / amostra.n
    return Medida(
        p,
        calculo=f"p = {sucessos} / {amostra.n} = {formatar_numero(p)}",
        interpretacao=f'{formatar_percentual(p * 100)} dos valores são "{escolhida}".',
        formula="proporcao",
    )


def tendencia(amostra: Amostra, tabela: TabelaFrequencia, sucesso: str | None) -> Tendencia:
    return Tendencia(
        media=media(amostra),
        mediana=mediana(amostra),
        moda=moda(amostra),
        moda_czuber=moda_czuber(amostra, tabela),
        proporcao=proporcao(amostra, sucesso),
    )
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/analise/tendencia.py tests/dominios/analise/test_tendencia.py
git commit -m "feat(analise): calcula média, mediana, moda, moda de Czuber e proporção"
```

---

### Tarefa 4: separatrizes e "onde está meu valor?" (spec 06)

**Arquivos:**
- Criar: `backend/app/dominios/analise/separatrizes.py`, `posicao.py`
- Teste: `backend/tests/dominios/analise/test_separatrizes.py`, `test_posicao.py`

**Passo 1: escrever os testes (falham)**

`test_separatrizes.py`
```python
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.separatrizes import separatrizes
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

UM_A_DEZ = [float(i) for i in range(1, 11)]


def test_quartis_decis_e_percentis_por_interpolacao(criar_amostra: CriarAmostra) -> None:
    resultado = separatrizes(criar_amostra(TipoVariavel.CONTINUA, UM_A_DEZ))

    assert resultado is not None
    # h = (n − 1)·p: Q1 → h = 2,25 → 3 + 0,25·(4 − 3) = 3,25
    assert [q.valor for q in resultado.quartis] == [3.25, 5.5, 7.75]
    assert [q.rotulo for q in resultado.quartis] == ["Q1", "Q2", "Q3"]
    assert resultado.decis[0].valor == pytest.approx(1.9)
    assert len(resultado.percentis) == 99
    assert resultado.percentis[-1].valor == pytest.approx(9.91)
    assert "P50" in resultado.destaques


def test_separatrizes_ordinais_sao_categorias(criar_amostra: CriarAmostra) -> None:
    valores = ["ruim", "regular", "bom", "bom"]

    resultado = separatrizes(criar_amostra(TipoVariavel.ORDINAL, valores, ESCALA_SATISFACAO))

    assert resultado is not None
    assert [q.valor for q in resultado.quartis] == ["ruim", "regular", "bom"]


def test_separatrizes_nao_se_aplicam_a_nominal(criar_amostra: CriarAmostra) -> None:
    assert separatrizes(criar_amostra(TipoVariavel.NOMINAL, ["a", "b"])) is None
```

`test_posicao.py`
```python
import numpy as np
import pytest

from app.dominios.analise.posicao import calcular_posicao, posicao_percentil

UM_A_DEZ = [float(i) for i in range(1, 11)]


def test_posicao_percentil_conta_metade_dos_iguais() -> None:
    assert posicao_percentil(np.array(UM_A_DEZ), 6.0) == 55.0


def test_valor_no_terceiro_quartil() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 6.0, "quartil")

    assert (posicao.regiao, posicao.indice) == ("3º quartil", 3)
    assert (posicao.limite_inferior, posicao.limite_superior) == (5.5, 7.75)
    assert posicao.frase == (
        "O valor 6 está no 3º quartil (entre Q2 = 5,5 e Q3 = 7,75). "
        "Cerca de 55% dos dados são menores que ele."
    )
    assert [m.rotulo for m in posicao.marcas] == ["Q1", "Q2", "Q3"]
    assert (posicao.minimo, posicao.maximo) == (1.0, 10.0)


def test_valor_igual_a_q1_fica_no_primeiro_quartil() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 3.25, "quartil")

    assert posicao.indice == 1
    assert "(até Q1 = 3,25)" in posicao.frase


def test_valor_abaixo_do_minimo_avisa() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 0.0, "quartil")

    assert posicao.fora_da_faixa == "abaixo"
    assert posicao.frase.endswith("O valor está abaixo do menor dado observado (1).")


def test_decil_acima_do_ultimo() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 10.0, "decil")

    assert posicao.regiao == "10º decil"
    assert "(acima de D9 = 9,1)" in posicao.frase
    assert posicao.fora_da_faixa is None


def test_percentil_usa_a_posicao_percentil_e_9_marcas() -> None:
    posicao = calcular_posicao(np.array(UM_A_DEZ), 6.0, "percentil")

    assert (posicao.regiao, posicao.indice) == ("percentil 55", 55)
    assert len(posicao.marcas) == 9
    assert posicao.limite_inferior == pytest.approx(5.86)
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar**

`app/dominios/analise/separatrizes.py`
```python
"""Quartis, decis e percentis por interpolação linear; ordinais por categoria (spec 06)."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise.frequencias import ordem_completa
from app.dominios.analise.resultados import (
    Amostra,
    Separatrizes,
    TipoSeparatriz,
    ValorSeparatriz,
)

_TOLERANCIA = 1e-12


@dataclass(frozen=True, slots=True)
class Divisao:
    """Em quantas partes iguais os dados são divididos e o prefixo do rótulo (Q, D, P)."""

    prefixo: str
    partes: int

    @property
    def proporcoes(self) -> tuple[float, ...]:
        return tuple(i / self.partes for i in range(1, self.partes))

    def rotulo(self, p: float) -> str:
        return f"{self.prefixo}{round(p * self.partes)}"


DIVISOES: dict[TipoSeparatriz, Divisao] = {
    "quartil": Divisao("Q", 4),
    "decil": Divisao("D", 10),
    "percentil": Divisao("P", 100),
}
DESTAQUES = ("P1", "P5", "P10", "P25", "P50", "P75", "P90", "P95", "P99")


def quantis(valores: np.ndarray, divisao: Divisao) -> tuple[ValorSeparatriz, ...]:
    """Qp com h = (n − 1)·p e interpolação linear (numpy.quantile, método linear)."""
    resultado = np.quantile(valores, divisao.proporcoes, method="linear")
    return tuple(
        ValorSeparatriz(divisao.rotulo(p), p, float(q))
        for p, q in zip(divisao.proporcoes, resultado, strict=True)
    )


def quantis_ordinais(amostra: Amostra, divisao: Divisao) -> tuple[ValorSeparatriz, ...]:
    """Categoria cuja frequência relativa acumulada atinge p."""
    ordem = ordem_completa(amostra)
    contagens = amostra.valores.astype(str).value_counts()
    acumuladas = np.cumsum([int(contagens.get(c, 0)) for c in ordem]) / amostra.n
    posicoes = np.searchsorted(acumuladas, np.array(divisao.proporcoes) - _TOLERANCIA)
    return tuple(
        ValorSeparatriz(divisao.rotulo(p), p, ordem[min(int(i), len(ordem) - 1)])
        for p, i in zip(divisao.proporcoes, posicoes, strict=True)
    )


def _montar(calcular: Callable[[Divisao], tuple[ValorSeparatriz, ...]]) -> Separatrizes:
    return Separatrizes(
        quartis=calcular(DIVISOES["quartil"]),
        decis=calcular(DIVISOES["decil"]),
        percentis=calcular(DIVISOES["percentil"]),
        destaques=DESTAQUES,
    )


def separatrizes(amostra: Amostra) -> Separatrizes | None:
    """Numéricas por interpolação; ordinais como categoria; nominal/binária não se aplica."""
    if amostra.tipo in TIPOS_NUMERICOS:
        valores = amostra.valores.to_numpy(dtype="float64")
        return _montar(lambda divisao: quantis(valores, divisao))
    if amostra.tipo == TipoVariavel.ORDINAL:
        return _montar(lambda divisao: quantis_ordinais(amostra, divisao))
    return None
```

`app/dominios/analise/posicao.py`
```python
""" "Onde está meu valor?": posição percentil e região entre separatrizes (spec 06)."""

import math
from typing import Literal

import numpy as np

from app.compartilhado.numeros import formatar_numero
from app.dominios.analise.resultados import Posicao, TipoSeparatriz, ValorSeparatriz
from app.dominios.analise.separatrizes import DESTAQUES, DIVISOES, quantis

MAX_PERCENTIL = 100

type Marcas = tuple[ValorSeparatriz, ...]


def posicao_percentil(valores: np.ndarray, valor: float) -> float:
    """PR = 100 · (nº de xᵢ < v + 0,5 · nº de xᵢ = v) / n."""
    menores, iguais = np.sum(valores < valor), np.sum(valores == valor)
    return float(100 * (menores + 0.5 * iguais) / len(valores))


def _indice(valor: float, tipo: TipoSeparatriz, marcas: Marcas, pr: float) -> int:
    """Região 1…k: até a 1ª marca é 1; acima da última, a última região."""
    if tipo == "percentil":
        return min(max(math.ceil(pr), 1), MAX_PERCENTIL)
    limites = [float(m.valor) for m in marcas]
    return int(np.searchsorted(limites, valor, side="left")) + 1


def _vizinhas(indice: int, marcas: Marcas) -> tuple[ValorSeparatriz | None, ValorSeparatriz | None]:
    inferior = marcas[indice - 2] if indice > 1 else None
    superior = marcas[indice - 1] if indice <= len(marcas) else None
    return inferior, superior


def _marca(marca: ValorSeparatriz) -> str:
    return f"{marca.rotulo} = {formatar_numero(float(marca.valor))}"


def _trecho(inferior: ValorSeparatriz | None, superior: ValorSeparatriz | None) -> str:
    if inferior is None and superior is not None:
        return f"até {_marca(superior)}"
    if superior is None and inferior is not None:
        return f"acima de {_marca(inferior)}"
    if inferior is not None and superior is not None:
        return f"entre {_marca(inferior)} e {_marca(superior)}"
    return "em toda a faixa"


def _regiao(tipo: TipoSeparatriz, indice: int) -> str:
    return f"percentil {indice}" if tipo == "percentil" else f"{indice}º {tipo}"


def _fora(valor: float, minimo: float, maximo: float) -> Literal["abaixo", "acima"] | None:
    if valor < minimo:
        return "abaixo"
    return "acima" if valor > maximo else None


def _aviso_fora(fora: str | None, minimo: float, maximo: float) -> str:
    if fora == "abaixo":
        return f" O valor está abaixo do menor dado observado ({formatar_numero(minimo)})."
    if fora == "acima":
        return f" O valor está acima do maior dado observado ({formatar_numero(maximo)})."
    return ""


def calcular_posicao(valores: np.ndarray, valor: float, tipo: TipoSeparatriz) -> Posicao:
    """Em que quartil/decil/percentil o valor cai e quantos dados ficam abaixo dele."""
    todas = quantis(valores, DIVISOES[tipo])
    pr = posicao_percentil(valores, valor)
    indice = _indice(valor, tipo, todas, pr)
    inferior, superior = _vizinhas(indice, todas)
    minimo, maximo = float(valores.min()), float(valores.max())
    fora = _fora(valor, minimo, maximo)
    regiao = _regiao(tipo, indice)
    frase = (
        f"O valor {formatar_numero(valor)} está no {regiao} ({_trecho(inferior, superior)}). "
        f"Cerca de {round(pr)}% dos dados são menores que ele."
        f"{_aviso_fora(fora, minimo, maximo)}"
    )
    marcas = tuple(m for m in todas if m.rotulo in DESTAQUES) if tipo == "percentil" else todas
    return Posicao(
        valor=valor,
        tipo=tipo,
        regiao=regiao,
        indice=indice,
        limite_inferior=float(inferior.valor) if inferior else None,
        limite_superior=float(superior.valor) if superior else None,
        posicao_percentil=pr,
        fora_da_faixa=fora,
        minimo=minimo,
        maximo=maximo,
        marcas=marcas,
        frase=frase,
    )
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/analise/separatrizes.py app/dominios/analise/posicao.py tests/dominios/analise/test_separatrizes.py tests/dominios/analise/test_posicao.py
git commit -m "feat(analise): calcula quartis, decis, percentis e a posição de um valor"
```

---

### Tarefa 5: dispersão (spec 07)

**Arquivos:**
- Criar: `backend/app/dominios/analise/dispersao.py`
- Teste: `backend/tests/dominios/analise/test_dispersao.py`

**Passo 1: escrever os testes (falham)** — exemplo de livro `[2, 4, 4, 4, 5, 5, 7, 9]`: x̄ = 5, σ² = 4, s² = 32/7, IQR = 1,5:
```python
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.dispersao import SEM_DISPERSAO, classificar_cv, dispersao
from app.dominios.analise.resultados import Dispersao, Medida
from app.dominios.analise.separatrizes import separatrizes
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

SEM_PROPORCAO = Medida(aplicavel=False)
LIVRO = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]


def _dispersao(criar_amostra: CriarAmostra, tipo: TipoVariavel, valores: list[float]) -> Dispersao:
    amostra = criar_amostra(tipo, valores)
    resultado = dispersao(amostra, separatrizes(amostra), SEM_PROPORCAO)
    assert resultado is not None
    return resultado


def test_exemplo_de_livro(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, LIVRO)

    assert resultado.amplitude.valor == 7
    assert resultado.variancia_populacional.valor == 4
    assert resultado.variancia.valor == pytest.approx(32 / 7)
    assert resultado.desvio_padrao.valor == pytest.approx(2.13809, abs=1e-5)
    assert resultado.iqr.valor == 1.5
    assert resultado.cv.valor == pytest.approx(42.76, abs=0.01)
    assert resultado.classificacao_cv == "alta"
    assert resultado.variancia.calculo == "Σ(xᵢ − x̄)² / (n − 1) = 32 / 7 = 4,571"


def test_variancia_amostral_usa_n_menos_1(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [1.0, 3.0])

    assert (resultado.variancia.valor, resultado.variancia_populacional.valor) == (2.0, 1.0)


def test_um_valor_so_nao_tem_variancia(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [5.0])

    assert resultado.variancia.motivo == "Variância não se aplica: precisa de pelo menos 2 valores."
    assert resultado.cv.aplicavel is False


def test_media_zero_nao_tem_cv(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [-1.0, 1.0])

    assert resultado.cv.motivo == "O CV não pode ser calculado porque a média é zero."


def test_cv_com_negativos_avisa(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.CONTINUA, [-2.0, 4.0, 6.0])

    assert resultado.cv.interpretacao is not None
    assert resultado.cv.interpretacao.endswith("CV pouco interpretável com valores negativos.")


def test_valores_iguais_nao_tem_dispersao(criar_amostra: CriarAmostra) -> None:
    resultado = _dispersao(criar_amostra, TipoVariavel.DISCRETA, [3.0, 3.0, 3.0])

    assert resultado.desvio_padrao.interpretacao == SEM_DISPERSAO
    assert resultado.classificacao_cv == "baixa"


@pytest.mark.parametrize(
    ("cv", "classe"), [(14.9, "baixa"), (15.0, "media"), (29.9, "media"), (30.1, "alta")]
)
def test_classificacao_do_cv(cv: float, classe: str) -> None:
    assert classificar_cv(cv) == classe


def test_binaria_usa_p_vezes_1_menos_p(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(TipoVariavel.BINARIA, ["a", "b"])

    resultado = dispersao(amostra, None, Medida(0.5))

    assert resultado is not None
    assert (resultado.variancia.valor, resultado.desvio_padrao.valor) == (0.25, 0.5)
    assert resultado.amplitude.aplicavel is False


def test_ordinal_em_categorias(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(
        TipoVariavel.ORDINAL, ["ruim", "regular", "bom", "bom", "ótimo"], ESCALA_SATISFACAO
    )

    resultado = dispersao(amostra, separatrizes(amostra), SEM_PROPORCAO)

    assert resultado is not None
    assert resultado.amplitude.valor == "de ruim a ótimo"
    assert resultado.iqr.valor == "de regular a bom"
    assert resultado.variancia.aplicavel is False


def test_nominal_nao_tem_dispersao(criar_amostra: CriarAmostra) -> None:
    assert dispersao(criar_amostra(TipoVariavel.NOMINAL, ["a", "b"]), None, SEM_PROPORCAO) is None
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar `app/dominios/analise/dispersao.py`**
```python
"""Medidas de dispersão: amplitude, variância, desvio padrão, IQR e CV (spec 07)."""

import math
from typing import Literal

import numpy as np

from app.compartilhado.numeros import formatar_numero
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.frequencias import ordem_completa
from app.dominios.analise.resultados import (
    Amostra,
    Dispersao,
    Medida,
    Separatrizes,
    nao_aplicavel,
)

MIN_VALORES_VARIANCIA = 2

type ClassificacaoCV = Literal["baixa", "media", "alta"]

LIMIARES_CV: tuple[tuple[float, ClassificacaoCV], ...] = ((15.0, "baixa"), (30.0, "media"))
FRASES_CV: dict[ClassificacaoCV, str] = {
    "baixa": "Os dados são homogêneos (pouca variação em relação à média).",
    "media": "Variação moderada em relação à média.",
    "alta": "Os dados são heterogêneos (muita variação em relação à média).",
}
CV_NEGATIVOS = "CV pouco interpretável com valores negativos."
SEM_DISPERSAO = "Todos os valores são iguais; não há dispersão."
ITENS_NUMERICOS = (
    "amplitude",
    "variancia",
    "variancia_populacional",
    "desvio_padrao",
    "desvio_padrao_populacional",
    "iqr",
    "cv",
)


def _f(valor: float) -> str:
    return formatar_numero(valor)


def classificar_cv(cv: float) -> ClassificacaoCV:
    """< 15% baixa · 15–30% média · > 30% alta."""
    return next((classe for limite, classe in LIMIARES_CV if cv < limite), "alta")


def _montar(medidas: dict[str, Medida], classificacao: ClassificacaoCV | None = None) -> Dispersao:
    return Dispersao(
        amplitude=medidas["amplitude"],
        variancia=medidas["variancia"],
        variancia_populacional=medidas["variancia_populacional"],
        desvio_padrao=medidas["desvio_padrao"],
        desvio_padrao_populacional=medidas["desvio_padrao_populacional"],
        iqr=medidas["iqr"],
        cv=medidas["cv"],
        classificacao_cv=classificacao,
    )


def _sem_distancias(tipo: TipoVariavel) -> dict[str, Medida]:
    return {i: nao_aplicavel(textos.nao_se_aplica(i, tipo, "distancias")) for i in ITENS_NUMERICOS}


def _variancias(valores: np.ndarray) -> dict[str, Medida]:
    """s² = Σ(xᵢ − x̄)² / (n − 1) e σ² = Σ(xᵢ − μ)² / n, com os desvios padrão."""
    n = len(valores)
    quadrados = float(np.sum((valores - valores.mean()) ** 2))
    populacional = quadrados / n
    medidas = {
        "variancia_populacional": Medida(
            populacional,
            calculo=f"Σ(xᵢ − μ)² / n = {_f(quadrados)} / {n} = {_f(populacional)}",
            formula="variancia_populacional",
        ),
        "desvio_padrao_populacional": Medida(
            math.sqrt(populacional),
            calculo=f"√{_f(populacional)} = {_f(math.sqrt(populacional))}",
            formula="desvio_padrao",
        ),
    }
    if n < MIN_VALORES_VARIANCIA:
        motivo = textos.nao_calculavel
        medidas["variancia"] = nao_aplicavel(motivo("variancia", "poucos_valores"))
        medidas["desvio_padrao"] = nao_aplicavel(motivo("desvio_padrao", "poucos_valores"))
        return medidas
    amostral = quadrados / (n - 1)
    desvio = math.sqrt(amostral)
    medidas["variancia"] = Medida(
        amostral,
        calculo=f"Σ(xᵢ − x̄)² / (n − 1) = {_f(quadrados)} / {n - 1} = {_f(amostral)}",
        formula="variancia",
    )
    medidas["desvio_padrao"] = Medida(
        desvio,
        calculo=f"√{_f(amostral)} = {_f(desvio)}",
        interpretacao=SEM_DISPERSAO if desvio == 0 else None,
        formula="desvio_padrao",
    )
    return medidas


def _cv(valores: np.ndarray, desvio: Medida) -> Medida:
    """CV = (s / x̄) · 100%; com valores negativos usa |x̄| e avisa."""
    media = float(valores.mean())
    if not desvio.aplicavel or not isinstance(desvio.valor, float):
        return nao_aplicavel(textos.nao_calculavel("cv", "poucos_valores"))
    if media == 0:
        return nao_aplicavel(textos.CV_MEDIA_ZERO)
    cv = desvio.valor / abs(media) * 100
    frase = FRASES_CV[classificar_cv(cv)]
    if bool(np.any(valores < 0)):
        frase = f"{frase} {CV_NEGATIVOS}"
    calculo = f"(s / x̄) · 100% = ({_f(desvio.valor)} / {_f(abs(media))}) · 100% = {_f(cv)}%"
    return Medida(cv, calculo=calculo, interpretacao=frase, formula="cv")


def _iqr_numerico(separatrizes: Separatrizes) -> Medida:
    q1, q3 = float(separatrizes.quartis[0].valor), float(separatrizes.quartis[2].valor)
    calculo = f"Q3 − Q1 = {_f(q3)} − {_f(q1)} = {_f(q3 - q1)}"
    return Medida(q3 - q1, calculo=calculo, formula="iqr")


def _numerica(amostra: Amostra, separatrizes: Separatrizes) -> Dispersao:
    valores = amostra.valores.to_numpy(dtype="float64")
    minimo, maximo = float(valores.min()), float(valores.max())
    calculo = f"xₘₐₓ − xₘᵢₙ = {_f(maximo)} − {_f(minimo)} = {_f(maximo - minimo)}"
    medidas = _variancias(valores)
    cv = _cv(valores, medidas["desvio_padrao"])
    medidas |= {
        "amplitude": Medida(maximo - minimo, calculo=calculo, formula="amplitude"),
        "iqr": _iqr_numerico(separatrizes),
        "cv": cv,
    }
    return _montar(medidas, classificar_cv(cv.valor) if isinstance(cv.valor, float) else None)


def _binaria(amostra: Amostra, proporcao: Medida) -> Dispersao:
    p = float(proporcao.valor) if isinstance(proporcao.valor, float) else 0.0
    variancia = p * (1 - p)
    medidas = _sem_distancias(amostra.tipo) | {
        "variancia": Medida(
            variancia,
            calculo=f"p(1 − p) = {_f(p)} · {_f(1 - p)} = {_f(variancia)}",
            formula="variancia_binaria",
        ),
        "desvio_padrao": Medida(
            math.sqrt(variancia),
            calculo=f"√{_f(variancia)} = {_f(math.sqrt(variancia))}",
            formula="desvio_padrao",
        ),
    }
    return _montar(medidas)


def _ordinal(amostra: Amostra, separatrizes: Separatrizes) -> Dispersao:
    """Amplitude e IQR em categorias ("de baixo a muito alto")."""
    ordem = ordem_completa(amostra)
    q1, q3 = separatrizes.quartis[0].valor, separatrizes.quartis[2].valor
    medidas = _sem_distancias(amostra.tipo) | {
        "amplitude": Medida(f"de {ordem[0]} a {ordem[-1]}"),
        "iqr": Medida(f"de {q1} a {q3}", calculo=f"Q1 = {q1} · Q3 = {q3}"),
    }
    return _montar(medidas)


def dispersao(
    amostra: Amostra, separatrizes: Separatrizes | None, proporcao: Medida
) -> Dispersao | None:
    """Numéricas: todas; binária: p(1 − p); ordinal: em categorias; nominal: não se aplica."""
    if amostra.tipo == TipoVariavel.BINARIA:
        return _binaria(amostra, proporcao)
    if separatrizes is None:
        return None
    if amostra.tipo == TipoVariavel.ORDINAL:
        return _ordinal(amostra, separatrizes)
    return _numerica(amostra, separatrizes)
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/analise/dispersao.py tests/dominios/analise/test_dispersao.py
git commit -m "feat(analise): calcula amplitude, variância, desvio padrão, IQR e CV com casos de borda"
```

---

### Tarefa 6: montagem da análise univariada

**Arquivos:**
- Criar: `backend/app/dominios/analise/univariada.py`
- Teste: `backend/tests/dominios/analise/test_univariada.py`

**Passo 1: escrever os testes (falham)**
```python
from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.formulas import FORMULAS, formulas_usadas
from app.dominios.analise.univariada import analisar_amostra
from tests.dominios.analise.conftest import ESCALA_SATISFACAO, CriarAmostra

LIVRO = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]


def test_continua_tem_tudo_menos_proporcao(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, LIVRO))

    assert analise.aplicavel == {
        "acumulada": True,
        "media": True,
        "mediana": True,
        "moda_czuber": True,
        "proporcao": False,
        "separatrizes": True,
        "posicao": True,
        "dispersao": True,
        "variancia": True,
        "cv": True,
    }
    assert [n.item for n in analise.nao_aplicavel] == ["proporcao"]
    chaves = [f.chave for f in analise.formulas]
    assert {"sturges", "media", "moda_czuber", "variancia", "cv"} <= set(chaves)
    assert analise.figuras == ()


def test_nominal_explica_cada_item_que_nao_se_aplica(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.NOMINAL, ["a", "b", "b"]))

    itens = {n.item: n.motivo for n in analise.nao_aplicavel}
    assert {"acumulada", "media", "mediana", "separatrizes", "posicao", "dispersao"} <= set(itens)
    assert itens["separatrizes"] == (
        "Separatrizes não se aplicam a qualitativas nominais: "
        "as categorias não têm ordem para dividir em partes."
    )
    assert analise.separatrizes is None
    assert analise.dispersao is None
    assert not any(analise.aplicavel.values())
    assert [f.chave for f in analise.formulas] == ["frequencia_relativa", "moda"]


def test_ordinal_tem_mediana_e_separatrizes_em_categorias(criar_amostra: CriarAmostra) -> None:
    amostra = criar_amostra(
        TipoVariavel.ORDINAL, ["ruim", "bom", "bom", "ótimo"], ESCALA_SATISFACAO
    )

    analise = analisar_amostra(amostra)

    assert analise.aplicavel["mediana"] is True
    assert analise.aplicavel["separatrizes"] is True
    assert analise.aplicavel["posicao"] is False
    assert analise.tendencia.mediana.valor == "bom"


def test_interpretacoes_automaticas(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, [1.0, 2.0, 3.0, 4.0, 5.0]))

    assert analise.interpretacoes == (
        "Média e mediana próximas (diferença de 0): a distribuição parece simétrica.",
        "Os dados são heterogêneos (muita variação em relação à média).",
    )


def test_assimetria_a_direita(criar_amostra: CriarAmostra) -> None:
    analise = analisar_amostra(criar_amostra(TipoVariavel.CONTINUA, [1.0, 1.5, 2.0, 2.5, 30.0]))

    assert analise.interpretacoes[0].startswith("Média maior que a mediana")


def test_formulas_usadas_seguem_o_catalogo_sem_repetir() -> None:
    usadas = formulas_usadas(["media", "moda", "media", None])

    assert [f.chave for f in usadas] == ["media", "moda"]
    assert FORMULAS["cv"].texto == "CV = (s / x̄) · 100%"
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar `app/dominios/analise/univariada.py`**
```python
"""Monta a análise univariada de uma coluna: tabela, medidas, aplicabilidade e fórmulas."""

from dataclasses import fields

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import textos
from app.dominios.analise.dispersao import dispersao
from app.dominios.analise.formulas import formulas_usadas
from app.dominios.analise.frequencias import tabela_frequencia
from app.dominios.analise.resultados import (
    Amostra,
    Analise,
    Dispersao,
    Medida,
    NaoAplicavel,
    Separatrizes,
    TabelaFrequencia,
    Tendencia,
)
from app.dominios.analise.separatrizes import separatrizes
from app.dominios.analise.tendencia import tendencia

FORMULAS_DE_CLASSES = ("sturges", "amplitude_classe", "ponto_medio")
INTERPRETACOES_DE_MEDIDAS = ("proporcao", "desvio_padrao", "cv")


def _medidas(tend: Tendencia, disp: Dispersao | None) -> dict[str, Medida]:
    """Medidas com nome; as de dispersão só entram se a dispersão se aplica ao tipo."""
    medidas = {
        "media": tend.media,
        "mediana": tend.mediana,
        "moda_czuber": tend.moda_czuber,
        "proporcao": tend.proporcao,
    }
    if disp is None:
        return medidas
    for campo in fields(disp):
        valor = getattr(disp, campo.name)
        if isinstance(valor, Medida):
            medidas[campo.name] = valor
    return medidas


def _secao(item: str, tipo: TipoVariavel) -> NaoAplicavel:
    return NaoAplicavel(item, textos.nao_se_aplica(item, tipo, item))


def _nao_aplicaveis(
    amostra: Amostra,
    tabela: TabelaFrequencia,
    medidas: dict[str, Medida],
    seps: Separatrizes | None,
) -> tuple[NaoAplicavel, ...]:
    """Tudo que não se aplica aparece com motivo (princípio 3 do design, D46)."""
    itens = [NaoAplicavel(nome, m.motivo or "") for nome, m in medidas.items() if not m.aplicavel]
    if tabela.motivo_acumulada:
        itens.insert(0, NaoAplicavel("acumulada", tabela.motivo_acumulada))
    if seps is None:
        itens.append(_secao("separatrizes", amostra.tipo))
    if amostra.tipo not in TIPOS_NUMERICOS:
        itens.append(_secao("posicao", amostra.tipo))
    if "amplitude" not in medidas:
        itens.append(_secao("dispersao", amostra.tipo))
    return tuple(itens)


def _aplicavel(
    amostra: Amostra,
    tabela: TabelaFrequencia,
    medidas: dict[str, Medida],
    seps: Separatrizes | None,
) -> dict[str, bool]:
    def ok(item: str) -> bool:
        return item in medidas and medidas[item].aplicavel

    return {
        "acumulada": tabela.acumulada_aplicavel,
        "media": ok("media"),
        "mediana": ok("mediana"),
        "moda_czuber": ok("moda_czuber"),
        "proporcao": ok("proporcao"),
        "separatrizes": seps is not None,
        "posicao": amostra.tipo in TIPOS_NUMERICOS,
        "dispersao": "amplitude" in medidas,
        "variancia": ok("variancia"),
        "cv": ok("cv"),
    }


def _numero(medida: Medida | None) -> float | None:
    return medida.valor if medida is not None and isinstance(medida.valor, float) else None


def _interpretacoes(medidas: dict[str, Medida]) -> tuple[str, ...]:
    """Frases automáticas das specs 05 e 07."""
    frases: list[str | None] = []
    media, mediana, desvio = (
        _numero(medidas.get(i)) for i in ("media", "mediana", "desvio_padrao")
    )
    if media is not None and mediana is not None and desvio is not None:
        frases.append(textos.interpretar_media_mediana(media, mediana, desvio))
    frases += [medidas[i].interpretacao for i in INTERPRETACOES_DE_MEDIDAS if i in medidas]
    return tuple(f for f in frases if f)


def _chaves_de_formulas(
    amostra: Amostra, tabela: TabelaFrequencia, medidas: dict[str, Medida]
) -> list[str | None]:
    chaves: list[str | None] = ["frequencia_relativa", "moda"]
    if tabela.acumulada_aplicavel:
        chaves.append("frequencia_acumulada")
    if amostra.tipo == TipoVariavel.CONTINUA:
        chaves += FORMULAS_DE_CLASSES
    if amostra.tipo in TIPOS_NUMERICOS:
        chaves += ["quantil", "posicao_percentil"]
    return chaves + [m.formula for m in medidas.values() if m.aplicavel]


def analisar_amostra(
    amostra: Amostra, classes: int | None = None, sucesso: str | None = None
) -> Analise:
    """Frequências, tendência, separatrizes e dispersão de uma coluna, com motivos e fórmulas."""
    tabela = tabela_frequencia(amostra, classes)
    tend = tendencia(amostra, tabela, sucesso)
    seps = separatrizes(amostra)
    disp = dispersao(amostra, seps, tend.proporcao)
    medidas = _medidas(tend, disp)
    return Analise(
        coluna=amostra.coluna,
        tipo=amostra.tipo,
        n=amostra.n,
        n_faltantes=amostra.n_faltantes,
        aplicavel=_aplicavel(amostra, tabela, medidas, seps),
        nao_aplicavel=_nao_aplicaveis(amostra, tabela, medidas, seps),
        frequencias=tabela,
        tendencia=tend,
        separatrizes=seps,
        dispersao=disp,
        interpretacoes=_interpretacoes(medidas),
        formulas=formulas_usadas(_chaves_de_formulas(amostra, tabela, medidas)),
    )
```

**Passo 4: rodar e ver passar** — `pytest tests/dominios/analise -v --no-cov`

**Passo 5: commit**
```bash
git add app/dominios/analise/univariada.py tests/dominios/analise/test_univariada.py
git commit -m "feat(analise): monta a análise univariada com aplicabilidade, motivos e fórmulas"
```

---

### Tarefa 7: fachada, erros, schemas e router

**Arquivos:**
- Criar: `backend/app/dominios/analise/servico.py`, `erros.py`, `schemas.py`, `router.py`
- Modificar: `backend/app/main.py`
- Teste: `backend/tests/dominios/analise/test_servico.py`, `test_router.py`

**Passo 1: escrever os testes (falham)**

`test_servico.py`
```python
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import OpcoesLeitura, ServicoDatasets

CONTEUDO = b"id;sexo;peso;obs\n1;F;58,2;\n2;M;79,6;\n3;F;;\n4;M;63,0;\n"


@pytest.fixture
def servico(servico_datasets: ServicoDatasets) -> ServicoAnalise:
    return ServicoAnalise(servico_datasets)


@pytest.fixture
def dataset_id(servico_datasets: ServicoDatasets) -> str:
    return servico_datasets.importar(CONTEUDO, "dados.txt", OpcoesLeitura()).dataset_id


def test_analisar_coluna_numerica(servico: ServicoAnalise, dataset_id: str) -> None:
    analise = servico.analisar(dataset_id, "peso")

    assert (analise.tipo, analise.n, analise.n_faltantes) == (TipoVariavel.CONTINUA, 3, 1)


def test_analisar_com_classes(servico: ServicoAnalise, dataset_id: str) -> None:
    assert servico.analisar(dataset_id, "peso", classes=3).frequencias.k == 3


def test_identificador_fica_fora(servico: ServicoAnalise, dataset_id: str) -> None:
    with pytest.raises(EntradaInvalida) as erro:
        servico.analisar(dataset_id, "id")

    assert erro.value.codigo == "COLUNA_IGNORADA"


def test_coluna_vazia(
    servico: ServicoAnalise, servico_datasets: ServicoDatasets, dataset_id: str
) -> None:
    servico_datasets.alterar_tipo(dataset_id, "obs", TipoVariavel.NOMINAL)

    with pytest.raises(EntradaInvalida) as erro:
        servico.analisar(dataset_id, "obs")

    assert erro.value.codigo == "COLUNA_VAZIA"


def test_posicao_so_para_numericas(servico: ServicoAnalise, dataset_id: str) -> None:
    posicao = servico.posicao(dataset_id, "peso", 70.0, "quartil")

    assert posicao.regiao == "3º quartil"
    with pytest.raises(EntradaInvalida) as erro:
        servico.posicao(dataset_id, "sexo", 1.0, "quartil")
    assert erro.value.codigo == "POSICAO_NAO_APLICAVEL"
```

`test_router.py`
```python
from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_analise_de_coluna_continua(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/colunas/altura_m/analise")

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert (corpo["tipo"], corpo["n"], corpo["n_faltantes"]) == ("continua", 229, 1)
    assert corpo["frequencias"]["k_sturges"] == 9
    assert corpo["tendencia"]["media"]["formula"] == "media"
    assert corpo["aplicavel"]["separatrizes"] is True
    assert len(corpo["separatrizes"]["percentis"]) == 99
    assert corpo["figuras"] == []


def test_analise_de_coluna_nominal(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    corpo = cliente.get(f"/api/datasets/{dataset_id}/colunas/cidade/analise").json()

    assert corpo["separatrizes"] is None
    assert corpo["dispersao"] is None
    assert {"separatrizes", "dispersao"} <= {item["item"] for item in corpo["nao_aplicavel"]}


def test_numero_de_classes(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    url = f"/api/datasets/{dataset_id}/colunas/altura_m/analise"

    assert cliente.get(url, params={"classes": 5}).json()["frequencias"]["k"] == 5
    assert cliente.get(url, params={"classes": 2}).status_code == 422


def test_identificador_e_coluna_inexistente(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    identificador = cliente.get(f"/api/datasets/{dataset_id}/colunas/id/analise")
    inexistente = cliente.get(f"/api/datasets/{dataset_id}/colunas/renda/analise")

    assert identificador.status_code == 400
    assert identificador.json()["codigo"] == "COLUNA_IGNORADA"
    assert inexistente.status_code == 404
    assert inexistente.json()["codigo"] == "COLUNA_NAO_ENCONTRADA"


def test_onde_esta_meu_valor(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)
    url = f"/api/datasets/{dataset_id}/colunas/altura_m/posicao"

    resposta = cliente.get(url, params={"valor": 1.7, "tipo": "decil"})
    nominal = cliente.get(f"/api/datasets/{dataset_id}/colunas/cidade/posicao", params={"valor": 1})

    assert resposta.status_code == 200
    assert resposta.json()["tipo"] == "decil"
    assert len(resposta.json()["marcas"]) == 9
    assert nominal.json()["codigo"] == "POSICAO_NAO_APLICAVEL"
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar**

`app/dominios/analise/erros.py`
```python
"""Erros do domínio analise (spec 14, formato da spec 16)."""

from app.core.erros import EntradaInvalida


def coluna_ignorada(coluna: str) -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNA_IGNORADA",
        f"A coluna {coluna} é um identificador e fica fora das análises.",
        "Mude o tipo na etapa Variáveis se ela tiver valores para analisar.",
    )


def coluna_vazia(coluna: str) -> EntradaInvalida:
    return EntradaInvalida(
        "COLUNA_VAZIA",
        f"A coluna {coluna} não tem valores para analisar.",
        "Escolha outra coluna ou confira a limpeza.",
    )


def posicao_nao_aplicavel() -> EntradaInvalida:
    return EntradaInvalida(
        "POSICAO_NAO_APLICAVEL",
        '"Onde está meu valor?" só funciona com colunas numéricas.',
        "Escolha uma coluna discreta ou contínua.",
    )
```

`app/dominios/analise/servico.py` — a montagem com `Depends` fica no router (ADR 0009):
```python
"""Fachada do domínio analise: análise univariada e "onde está meu valor?" (D54)."""

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import erros
from app.dominios.analise.posicao import calcular_posicao
from app.dominios.analise.resultados import Amostra, Analise, Posicao, TipoSeparatriz
from app.dominios.analise.univariada import analisar_amostra
from app.dominios.datasets.servico import ServicoDatasets

__all__ = ["Analise", "Posicao", "ServicoAnalise", "TipoSeparatriz"]


class ServicoAnalise:
    """Casos de uso da análise; os dados vêm da fachada do domínio datasets."""

    def __init__(self, datasets: ServicoDatasets) -> None:
        self._datasets = datasets

    def amostra(self, dataset_id: str, coluna: str) -> Amostra:
        """Valores válidos da coluna, já convertidos conforme o tipo."""
        dados = self._datasets.coluna_para_analise(dataset_id, coluna)
        if dados.tipo == TipoVariavel.IDENTIFICADOR:
            raise erros.coluna_ignorada(coluna)
        serie = dados.numeros if dados.numeros is not None else dados.textos
        validos = serie.dropna()
        if validos.empty:
            raise erros.coluna_vazia(coluna)
        return Amostra(coluna, dados.tipo, validos, int(serie.isna().sum()), dados.categorias_ordem)

    def analisar(
        self,
        dataset_id: str,
        coluna: str,
        classes: int | None = None,
        sucesso: str | None = None,
    ) -> Analise:
        """Frequências, tendência, separatrizes e dispersão da coluna (specs 04–07)."""
        return analisar_amostra(self.amostra(dataset_id, coluna), classes, sucesso)

    def posicao(self, dataset_id: str, coluna: str, valor: float, tipo: TipoSeparatriz) -> Posicao:
        """Em que separatriz o valor cai (spec 06)."""
        amostra = self.amostra(dataset_id, coluna)
        if amostra.tipo not in TIPOS_NUMERICOS:
            raise erros.posicao_nao_aplicavel()
        return calcular_posicao(amostra.valores.to_numpy(dtype="float64"), valor, tipo)
```

`app/dominios/analise/schemas.py`
```python
"""Contratos HTTP do domínio analise (spec 14; nomes na visão geral do M1)."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.compartilhado.tipos import TipoVariavel

type Valor = float | str | None


class Modelo(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class NaoAplicavel(Modelo):
    item: str
    motivo: str


class Formula(Modelo):
    chave: str
    nome: str
    latex: str
    texto: str


class Medida(Modelo):
    valor: Valor
    aplicavel: bool
    motivo: str | None
    calculo: str | None
    interpretacao: str | None
    formula: str | None


class LinhaFrequencia(Modelo):
    rotulo: str
    valor: Valor
    limite_inferior: float | None
    limite_superior: float | None
    ponto_medio: float | None
    fi: int
    fri: float
    fr_pct: float
    f_acum: int | None
    fr_acum: float | None
    fr_acum_pct: float | None


class TabelaFrequencia(Modelo):
    tipo: TipoVariavel
    linhas: list[LinhaFrequencia]
    total: int
    k: int | None
    k_sturges: int | None
    h: float | None
    metodo_classes: Literal["sturges", "usuario"] | None
    acumulada_aplicavel: bool
    motivo_acumulada: str | None
    indice_modal: int | None


class Moda(Modelo):
    valores: list[float | str]
    classificacao: Literal["amodal", "unimodal", "bimodal", "multimodal"]
    interpretacao: str


class Tendencia(Modelo):
    media: Medida
    mediana: Medida
    moda: Moda
    moda_czuber: Medida
    proporcao: Medida


class ValorSeparatriz(Modelo):
    rotulo: str
    p: float
    valor: float | str


class Separatrizes(Modelo):
    quartis: list[ValorSeparatriz]
    decis: list[ValorSeparatriz]
    percentis: list[ValorSeparatriz]
    destaques: list[str]


class Dispersao(Modelo):
    amplitude: Medida
    variancia: Medida
    variancia_populacional: Medida
    desvio_padrao: Medida
    desvio_padrao_populacional: Medida
    iqr: Medida
    cv: Medida
    classificacao_cv: Literal["baixa", "media", "alta"] | None


class Figura(Modelo):
    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: dict[str, Any]


class Analise(Modelo):
    coluna: str
    tipo: TipoVariavel
    n: int
    n_faltantes: int
    aplicavel: dict[str, bool]
    nao_aplicavel: list[NaoAplicavel]
    frequencias: TabelaFrequencia
    tendencia: Tendencia
    separatrizes: Separatrizes | None
    dispersao: Dispersao | None
    interpretacoes: list[str]
    formulas: list[Formula]
    figuras: list[Figura]


class Posicao(Modelo):
    valor: float
    tipo: Literal["quartil", "decil", "percentil"]
    regiao: str
    indice: int
    limite_inferior: float | None
    limite_superior: float | None
    posicao_percentil: float
    fora_da_faixa: Literal["abaixo", "acima"] | None
    minimo: float
    maximo: float
    marcas: list[ValorSeparatriz]
    frase: str
```

`app/dominios/analise/router.py`
```python
"""Rotas HTTP do domínio analise (spec 14). Sem lógica: valida → serviço → schema."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.dominios.analise.schemas import Analise, Posicao
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets

router = APIRouter(prefix="/datasets/{dataset_id}/colunas/{coluna}", tags=["analise"])

MIN_CLASSES = 3
MAX_CLASSES = 30


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
) -> ServicoAnalise:
    return ServicoAnalise(datasets)


Servico = Annotated[ServicoAnalise, Depends(_servico)]


@router.get("/analise", summary="Análise univariada da coluna (specs 04–07)")
def analisar(
    servico: Servico,
    dataset_id: str,
    coluna: str,
    classes: Annotated[int | None, Query(ge=MIN_CLASSES, le=MAX_CLASSES)] = None,
    sucesso: Annotated[str | None, Query(description="Categoria de sucesso (binária)")] = None,
) -> Analise:
    return Analise.model_validate(servico.analisar(dataset_id, coluna, classes, sucesso))


@router.get("/posicao", summary='"Onde está meu valor?" (spec 06)')
def posicao(
    servico: Servico,
    dataset_id: str,
    coluna: str,
    valor: float,
    tipo: Literal["quartil", "decil", "percentil"] = "quartil",
) -> Posicao:
    return Posicao.model_validate(servico.posicao(dataset_id, coluna, valor, tipo))
```

`app/main.py` (substituir)
```python
"""Ponto de entrada: monta a aplicação FastAPI (monólito em camadas por domínio, ADR 0007)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import saude
from app.core.config import obter_configuracao
from app.core.handlers import registrar_handlers
from app.dominios.analise import router as analise
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
    app.include_router(analise.router, prefix=PREFIXO_API)
    return app


app = create_app()
```

**Passo 4: suíte toda**
```bash
ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest
```

**Passo 5: commit**
```bash
git add app/dominios/analise app/main.py tests/dominios/analise
git commit -m "feat(analise): expõe análise univariada e posição de valor na API"
```

---

### Tarefa 8: tipos do frontend, decisões, specs e CHANGELOG

**Passo 1: tipos** — `python scripts/exportar_openapi.py` e, em `frontend/`, `npm run gerar:tipos && npm run lint && npm run build`.

**Passo 2: `docs/decisions.md`** (próximo número livre; a visão geral não reserva um para isto):
```
| Dxx | DD/10/2026 | `Formula.chave` e `Medida.formula` ligam cada card à sua fórmula; `Figura.rotulo` dá o nome curto do gráfico | Casar pelo nome da fórmula no frontend | Chave estável, sem depender de texto de interface (lacuna apontada no plano do M1.7) | — |
| Dxx | DD/10/2026 | Posição percentil calculada com numpy pela fórmula da spec 06 | `scipy.stats.percentileofscore` | Mesmo resultado; o `mypy --strict` exigiria `scipy-stubs` | — |
```

**Passo 3: specs**
- `docs/specs/14-api.md`, contrato `Analise`: `formulas[]` com `chave`; cada medida com `formula`; `figuras` como lista `{id, rotulo, titulo, resumo, porque, recomendado, dados}`.
- `docs/specs/05-tendencia-central.md`: a proporção aceita `?sucesso=`.
- `docs/specs/06-separatrizes.md`: na saída, acrescentar `minimo`, `maximo`, `marcas` (3, 9 ou os 9 destaques) e `fora_da_faixa`.
- `docs/specs/07-dispersao.md`: texto exato de n < 2 ("{medida} não se aplica: precisa de pelo menos 2 valores.").

**Passo 4: `CHANGELOG.md`** — *Não lançado › Adicionado*:
```
- Análise univariada por coluna (`GET /api/datasets/{id}/colunas/{coluna}/analise`): tabela de frequências (com classes de Sturges), média, mediana, moda, moda de Czuber, proporção, quartis, decis, percentis, amplitude, variância, desvio padrão, IQR e CV, com motivo para o que não se aplica, cálculo passo a passo, interpretações e fórmulas.
- "Onde está meu valor?" (`GET /api/datasets/{id}/colunas/{coluna}/posicao`).
```

**Passo 5: commit**
```bash
git add ../frontend/src/shared/api/schema.d.ts ../docs ../CHANGELOG.md
git commit -m "docs: registra decisões da análise e atualiza specs 05, 06, 07 e 14"
```

---

### Tarefa 9: verificação final, teste manual e PR

**Passo 1: tudo verde** (backend, frontend e jscpd).

**Passo 2: teste manual pelo preview** — subir `backend`, `POST /api/datasets/exemplo` e conferir em `/docs`:
1. `altura_m/analise` → contínua, `k_sturges = 9`, classes "1,48 ⊢ …", cards com `calculo`; `classes=5` muda `k`.
2. `cidade/analise` → só frequências e moda; `nao_aplicavel` com separatrizes, posição e dispersão.
3. `satisfacao/analise` → mediana "bom", quartis em categorias, amplitude "de ruim a ótimo".
4. `sexo/analise` → proporção e `p(1 − p)`.
5. `peso_kg/posicao?valor=75&tipo=quartil` → frase no formato do print 4a.
6. `id/analise` → 400 `COLUNA_IGNORADA`.

**Passo 3: resumo e PR** — só com o ok do usuário:
```bash
git push -u origin feat/analise-descritiva
gh pr create --base develop --title "feat(analise): frequências, tendência, separatrizes e dispersão (M1.4)" --body "<resumo + specs 04–07 + checklist do padroes-codigo.md §8>"
```
Sem atribuição de IA. Merge só quando o usuário pedir, com os 3 checks verdes.

---

## Critérios de pronto do M1.4
- [ ] Specs 04–07 implementadas para os 5 tipos, com testes de exemplos calculados à mão
- [ ] Nada some: todo item não aplicável tem motivo; abas Separatrizes/Dispersão desabilitáveis pelo `aplicavel`
- [ ] `GET /analise` e `GET /posicao` com erros `COLUNA_IGNORADA`, `COLUNA_VAZIA`, `POSICAO_NAO_APLICAVEL`, `COLUNA_NAO_ENCONTRADA`
- [ ] Cobertura ≥ 80% em `dominios/` e `compartilhado/`; CI verde; `schema.d.ts` regenerado
