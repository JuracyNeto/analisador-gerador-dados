# M1.5 — Gráficos e mini relatório — plano de implementação

> **Para o agente:** use a skill `executing-plans` (ou `subagent-driven-development`) para executar tarefa por tarefa. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 08, 13 e 14, `docs/design/graficos-plotly.md`, `docs/design/telas.md` §8 e os contratos em `docs/plans/2026-10-03-m1-visao-geral.md`.

**Objetivo:** a análise de cada coluna passa a trazer as figuras do tipo (spec 08: principal + complementares, com título, resumo, "por que este gráfico" e rótulo curto), e `GET /api/datasets/{id}/relatorio` gera o mini relatório HTML do M1 (spec 13: leitura, tipos, limpeza e análise por coluna), autocontido, sempre no tema claro, com Plotly via CDN ou embutido (offline) e fórmulas em KaTeX com texto de reserva.

**Arquitetura:**
- `graficos` é um domínio folha (só depende de `compartilhado`): recebe `DadosUnivariados` (barras já agregadas + valores para o boxplot) e devolve `FiguraPronta`. As figuras são **dicionários no formato JSON do Plotly**, montados à mão: o pacote `plotly` não tem tipos e o `mypy --strict` recusaria o import. Os testes (fora do mypy) validam cada figura com `plotly.graph_objects.Figure`. O template padrão do Plotly não entra no JSON (o frontend aplica o tema dele; o relatório aplica `tema.layout_claro()`, que espelha o `tokens.css` e é conferido por teste — mitigação prevista na ADR 0008).
- `analise.servico` chama `graficos.servico.figuras_univariadas` (dependência num só sentido: analise → graficos).
- `relatorio` monta um `ConteudoRelatorio` só com textos já prontos (`servico.py` converte `Analise` → seções) e renderiza com Jinja2 (`templates/relatorio.html.j2` + `estilos.css` embutido).

**Stack:** Python 3.12, Jinja2, pandas/numpy, FastAPI; Plotly só nos testes e como fonte do `plotly.min.js` (lido do pacote com `importlib.resources`).

**Branch:** `feat/graficos-relatorio` (sai de `develop` **depois do merge do M1.3 e do M1.4**) → PR para `develop`.

**Prazo sugerido:** 22/10/2026. **Depende de:** M1.3 (log no relatório) e M1.4 (análise). As Tarefas 1–4 só dependem do M1.2 e podem começar antes.

**Código validado:** rodado num rascunho sobre M1.2 + M1.3 + M1.4 com ruff, mypy, complexipy, jscpd e pytest (317 testes, 99% de cobertura; `graficos/` e `relatorio/` entre 96% e 100%). O relatório gerado foi aberto no navegador: 7 gráficos Plotly via CDN, fórmulas KaTeX e impressão em A4.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Entradas e tema claro | `graficos/entradas.py`, `graficos/tema.py` |
| 2 | Construtores de figura | `graficos/figuras.py` |
| 3 | Textos e fábrica por tipo | `graficos/textos.py`, `graficos/fabrica.py` |
| 4 | Fachada do domínio graficos | `graficos/servico.py` |
| 5 | Figuras na análise | `analise/servico.py` |
| 6 | Conteúdo e textos do relatório | `relatorio/conteudo.py`, `relatorio/textos.py` |
| 7 | Template e montagem | `relatorio/templates/*`, `relatorio/montagem.py`, `pyproject.toml` |
| 8 | Fachada do relatório | `relatorio/servico.py` |
| 9 | Rota e registro no `main` | `relatorio/router.py`, `main.py` |
| 10 | Tipos do frontend, decisões, ADR 0003, specs e CHANGELOG | `schema.d.ts`, `docs/**` |
| 11 | Verificação final, teste manual e PR | — |

### Gráfico por tipo (spec 08, D56)
| Tipo | `principal` | Complementares |
|---|---|---|
| Nominal | Barras horizontais, maior no topo, rótulo "fᵢ (fr%)" até 12 barras | `pizza` (só com ≤ 5 categorias) |
| Binária | Barras verticais com percentual | — |
| Ordinal | Barras verticais na ordem da escala | `acumulada` (barras de Fr%) |
| Discreta | **Bastões** (haste fina + ponto) | `boxplot`, `acumulada` (escada) |
| Contínua | Histograma das classes da spec 04 (largura = h) | `boxplot`, `ogiva` |

Boxplot sempre com estatísticas pré-calculadas (`q1`, `median`, `q3`, cercas, média) e os discrepantes como pontos à parte (no máximo 500): nenhum gráfico envia valores brutos (ADR 0003, n > 5.000). A curva Normal sobre o histograma fica para o M2 (aba "Forma"), como no print 4b.

---

### Tarefa 1: entradas e tema claro

**Arquivos:**
- Criar: `backend/app/dominios/graficos/entradas.py`, `backend/app/dominios/graficos/tema.py`
- Teste: `backend/tests/dominios/graficos/__init__.py` (vazio), `backend/tests/dominios/graficos/test_tema.py`

**Passo 1: escrever os testes (falham)** — o primeiro compara os valores do tema com o `frontend/src/shared/ui/tokens.css` (bloco `:root, [data-tema='claro']`):
```python
import re

from app.core.config import RAIZ_REPOSITORIO
from app.dominios.graficos.tema import TOKENS_CLARO, layout_claro, mesclar

TOKENS_CSS = RAIZ_REPOSITORIO / "frontend" / "src" / "shared" / "ui" / "tokens.css"
_DECLARACAO = re.compile(r"(--[\w-]+):\s*([^;]+);")


def _tokens_do_tema_claro() -> dict[str, str]:
    """Primeiro bloco do tokens.css (`:root, [data-tema='claro'] { … }`)."""
    css = TOKENS_CSS.read_text(encoding="utf-8")
    bloco = css[css.index("{") + 1 : css.index("}")]
    return {nome: valor.strip().lower() for nome, valor in _DECLARACAO.findall(bloco)}


def test_tema_do_relatorio_espelha_o_tokens_css() -> None:
    # ADR 0008: os valores claros ficam duplicados em Python; este teste impede que divirjam.
    tokens = _tokens_do_tema_claro()

    assert {nome: tokens[nome] for nome in TOKENS_CLARO} == TOKENS_CLARO


def test_layout_claro_usa_virgula_decimal_e_a_paleta() -> None:
    layout = layout_claro()

    assert layout["separators"] == ",."
    assert layout["colorway"][0] == TOKENS_CLARO["--graf-1"]
    assert layout["paper_bgcolor"] == "#ffffff"


def test_mesclar_preserva_dicionarios_internos() -> None:
    base = {"xaxis": {"gridcolor": "#eee", "title": {"font": {"size": 13}}}, "bargap": 0.04}
    extra = {"xaxis": {"title": {"text": "peso_kg"}}, "bargap": 0}

    resultado = mesclar(base, extra)

    assert resultado == {
        "xaxis": {"gridcolor": "#eee", "title": {"font": {"size": 13}, "text": "peso_kg"}},
        "bargap": 0,
    }
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/graficos --no-cov`

**Passo 3: implementar**

`app/dominios/graficos/entradas.py`
```python
"""Entradas e saídas da fábrica de figuras (independentes do domínio analise)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app.compartilhado.tipos import TipoVariavel


@dataclass(frozen=True, slots=True)
class Barra:
    """Uma categoria, valor ou classe da tabela de frequências, já na ordem de exibição."""

    rotulo: str
    frequencia: int
    percentual: float
    acumulado_pct: float | None = None
    valor: float | None = None
    inferior: float | None = None
    superior: float | None = None


@dataclass(frozen=True, slots=True, eq=False)
class DadosUnivariados:
    coluna: str
    tipo: TipoVariavel
    n: int
    barras: tuple[Barra, ...]
    valores: pd.Series | None = None


@dataclass(frozen=True, slots=True)
class ResumoCaixa:
    """Estatísticas do boxplot pré-calculadas (ADR 0003: nada de pontos brutos)."""

    minimo: float
    q1: float
    mediana: float
    q3: float
    maximo: float
    media: float
    bigode_inferior: float
    bigode_superior: float
    discrepantes: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class FiguraPronta:
    id: str
    rotulo: str
    titulo: str
    resumo: str
    porque: str
    recomendado: bool
    dados: Mapping[str, Any] = field(default_factory=dict)
```

`app/dominios/graficos/tema.py`
```python
"""Tema claro do Plotly para o relatório (D45, D47, ADR 0008).

Espelha os tokens do tema claro de `frontend/src/shared/ui/tokens.css`; um teste compara os dois.
O frontend aplica o tema dele por cima da figura; o relatório usa sempre este.
"""

from typing import Any

TOKENS_CLARO = {
    "--cor-texto": "#161a20",
    "--cor-texto-2": "#4b5462",
    "--graf-1": "#0b6aa8",
    "--graf-2": "#c4520a",
    "--graf-3": "#0b7a5a",
    "--graf-4": "#b0548f",
    "--graf-5": "#8f6400",
    "--graf-6": "#5a4bb5",
    "--graf-7": "#3f8fc4",
    "--graf-8": "#4b5563",
    "--graf-grade": "#e6e9ee",
    "--graf-eixo": "#868f9c",
    "--graf-fundo": "#ffffff",
}
PALETA = tuple(TOKENS_CLARO[f"--graf-{i}"] for i in range(1, 9))
COR_PRINCIPAL = TOKENS_CLARO["--graf-1"]
COR_REFERENCIA = TOKENS_CLARO["--graf-2"]
FONTE = "Inter, system-ui, sans-serif"


def _eixo() -> dict[str, Any]:
    return {
        "gridcolor": TOKENS_CLARO["--graf-grade"],
        "linecolor": TOKENS_CLARO["--graf-eixo"],
        "zeroline": False,
        "ticks": "",
        "title": {"font": {"size": 13, "color": TOKENS_CLARO["--cor-texto"]}},
    }


def layout_claro() -> dict[str, Any]:
    """Mesmo layout do `layoutTema` de docs/design/graficos-plotly.md, com as cores claras."""
    return {
        "font": {"family": FONTE, "size": 12, "color": TOKENS_CLARO["--cor-texto-2"]},
        "paper_bgcolor": TOKENS_CLARO["--graf-fundo"],
        "plot_bgcolor": TOKENS_CLARO["--graf-fundo"],
        "colorway": list(PALETA),
        "separators": ",.",
        "margin": {"l": 60, "r": 16, "t": 32, "b": 48},
        "xaxis": _eixo(),
        "yaxis": _eixo(),
        "bargap": 0.04,
    }


def mesclar(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Junta dois layouts; dicionários internos são mesclados, o resto vem de `extra`."""
    resultado = dict(base)
    for chave, valor in extra.items():
        atual = resultado.get(chave)
        if isinstance(atual, dict) and isinstance(valor, dict):
            resultado[chave] = mesclar(atual, valor)
        else:
            resultado[chave] = valor
    return resultado
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/graficos/entradas.py app/dominios/graficos/tema.py tests/dominios/graficos
git commit -m "feat(graficos): adiciona entradas da fábrica e tema claro espelhado do tokens.css"
```

---

### Tarefa 2: construtores de figura

**Arquivos:**
- Criar: `backend/app/dominios/graficos/figuras.py`
- Teste: `backend/tests/dominios/graficos/test_figuras.py`

**Passo 1: escrever os testes (falham)** — `_valida` passa cada figura pelo `plotly.graph_objects.Figure`, que recusa propriedades inválidas:
```python
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import pytest

from app.dominios.graficos import figuras
from app.dominios.graficos.entradas import Barra

CATEGORIAS = (
    Barra("Goiânia", 87, 38.2),
    Barra("Anápolis", 38, 16.7),
    Barra("Trindade", 3, 1.3),
)
VALORES = (
    Barra("1", 2, 20.0, 20.0, valor=1.0),
    Barra("2", 5, 50.0, 70.0, valor=2.0),
    Barra("3", 3, 30.0, 100.0, valor=3.0),
)
CLASSES = (
    Barra("2,0 ⊢ 3,9", 2, 40.0, 40.0, inferior=2.0, superior=3.9),
    Barra("3,9 ⊢ 5,8", 3, 60.0, 100.0, inferior=3.9, superior=5.8),
)


def _valida(figura: dict[str, Any]) -> dict[str, Any]:
    """O Plotly recusa propriedades inválidas; é o que garante o formato sem tipos no app."""
    go.Figure(figura)
    assert "template" not in figura["layout"]
    return figura


def test_barras_horizontais_poem_a_maior_no_topo() -> None:
    figura = _valida(figuras.barras_horizontais(CATEGORIAS, "cidade"))

    traco = figura["data"][0]
    assert traco["orientation"] == "h"
    assert traco["y"] == ["Trindade", "Anápolis", "Goiânia"]
    assert traco["text"][-1] == "87 (38,2%)"


def test_sem_rotulos_com_mais_de_12_barras() -> None:
    muitas = tuple(Barra(str(i), 1, 1.0) for i in range(13))

    figura = _valida(figuras.barras_verticais(muitas, "x"))

    assert "text" not in figura["data"][0]


def test_bastoes_tem_hastes_finas_e_pontos() -> None:
    figura = _valida(figuras.bastoes(VALORES, "filhos"))

    hastes, pontos = figura["data"]
    assert hastes["width"] == figuras.LARGURA_BASTAO
    assert pontos["mode"] == "markers"
    assert hastes["x"] == [1.0, 2.0, 3.0]


def test_histograma_usa_as_classes() -> None:
    figura = _valida(figuras.histograma(CLASSES, "peso_kg"))

    traco = figura["data"][0]
    assert traco["x"] == pytest.approx([2.95, 4.85])
    assert traco["width"] == pytest.approx([1.9, 1.9])
    assert traco["customdata"] == ["2,0 ⊢ 3,9", "3,9 ⊢ 5,8"]
    assert figura["layout"]["bargap"] == 0


def test_resumo_caixa_e_boxplot_sem_pontos_brutos() -> None:
    valores = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 100.0])

    caixa = figuras.resumo_caixa(valores)
    figura = _valida(figuras.boxplot(caixa, "x"))

    assert (caixa.q1, caixa.mediana, caixa.q3) == (2.25, 3.5, 4.75)
    assert caixa.discrepantes == (100.0,)
    assert caixa.bigode_superior == 5.0
    assert "x" not in figura["data"][0]
    assert figura["data"][1]["x"] == [100.0]


def test_ogiva_comeca_no_zero() -> None:
    figura = _valida(figuras.ogiva(CLASSES, "peso_kg"))

    assert figura["data"][0]["x"] == [2.0, 3.9, 5.8]
    assert figura["data"][0]["y"] == [0.0, 40.0, 100.0]


def test_acumuladas_e_pizza() -> None:
    escada = _valida(figuras.acumulada_escada(VALORES, "filhos"))
    barras = _valida(figuras.acumulada_categorias(VALORES, "filhos"))
    pizza = _valida(figuras.pizza(CATEGORIAS))

    assert escada["data"][0]["line"]["shape"] == "hv"
    assert barras["data"][0]["y"] == [20.0, 70.0, 100.0]
    assert pizza["data"][0]["labels"] == ["Goiânia", "Anápolis", "Trindade"]
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar `app/dominios/graficos/figuras.py`**
```python
"""Figuras no formato JSON do Plotly ({"data": [...], "layout": {...}}) a partir de dados agregados.

Montadas como dicionários: o pacote `plotly` não tem tipos para o `mypy --strict` (ver
decisions.md). Os testes validam cada figura com `plotly.graph_objects`. Sem template: o tema é
aplicado depois (frontend ou relatório).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.compartilhado.numeros import formatar_percentual
from app.dominios.graficos.entradas import Barra, ResumoCaixa
from app.dominios.graficos.tema import COR_PRINCIPAL, COR_REFERENCIA

type Figura = dict[str, Any]

FATOR_IQR = 1.5
MAX_ROTULOS = 12
MAX_DISCREPANTES = 500
OPACIDADE_BARRA = 0.85
LARGURA_BASTAO = 0.08
LARGURA_LINHA = 2.5
QUARTIS = (0.25, 0.5, 0.75)
EIXO_FREQUENCIA = "Frequência (fᵢ)"
EIXO_ACUMULADA = "Frequência acumulada (%)"
MARCADOR_BARRA = {"color": COR_PRINCIPAL, "opacity": OPACIDADE_BARRA}


def _figura(tracos: list[dict[str, Any]], eixo_x: str, eixo_y: str) -> Figura:
    layout = {
        "xaxis": {"title": {"text": eixo_x}},
        "yaxis": {"title": {"text": eixo_y}},
        "showlegend": False,
        "separators": ",.",
    }
    return {"data": tracos, "layout": layout}


def _com_rotulos(traco: dict[str, Any], barras: tuple[Barra, ...]) -> dict[str, Any]:
    """Rótulo "fᵢ (fr%)" na ponta das barras, só com até 12 barras (spec 08)."""
    if len(barras) > MAX_ROTULOS:
        return traco
    rotulos = [f"{b.frequencia} ({formatar_percentual(b.percentual)})" for b in barras]
    return traco | {"text": rotulos, "textposition": "outside"}


def barras_horizontais(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Nominal: a maior categoria no topo."""
    invertidas = barras[::-1]
    traco = {
        "type": "bar",
        "orientation": "h",
        "x": [b.frequencia for b in invertidas],
        "y": [b.rotulo for b in invertidas],
        "marker": MARCADOR_BARRA,
    }
    return _figura([_com_rotulos(traco, invertidas)], EIXO_FREQUENCIA, coluna)


def barras_verticais(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Ordinal (na ordem da escala) e binária (com o percentual no rótulo)."""
    traco = {
        "type": "bar",
        "x": [b.rotulo for b in barras],
        "y": [b.frequencia for b in barras],
        "marker": MARCADOR_BARRA,
    }
    return _figura([_com_rotulos(traco, barras)], coluna, EIXO_FREQUENCIA)


def bastoes(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Discreta: uma haste fina por valor, com um ponto no topo."""
    x = [b.valor for b in barras]
    y = [b.frequencia for b in barras]
    hastes = {
        "type": "bar",
        "x": x,
        "y": y,
        "width": LARGURA_BASTAO,
        "marker": {"color": COR_PRINCIPAL},
    }
    pontos = {
        "type": "scatter",
        "mode": "markers",
        "x": x,
        "y": y,
        "marker": {"color": COR_PRINCIPAL, "size": 9},
    }
    return _figura([hastes, pontos], coluna, EIXO_FREQUENCIA)


def histograma(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Contínua: as classes da spec 04 como barras encostadas (largura = h)."""
    inferiores = [b.inferior or 0.0 for b in barras]
    larguras = [(b.superior or 0.0) - (b.inferior or 0.0) for b in barras]
    traco = {
        "type": "bar",
        "x": [i + w / 2 for i, w in zip(inferiores, larguras, strict=True)],
        "y": [b.frequencia for b in barras],
        "width": larguras,
        "customdata": [b.rotulo for b in barras],
        "hovertemplate": "%{customdata}: %{y}<extra></extra>",
        "marker": MARCADOR_BARRA,
    }
    figura = _figura([traco], coluna, EIXO_FREQUENCIA)
    figura["layout"]["bargap"] = 0
    return figura


def resumo_caixa(valores: pd.Series) -> ResumoCaixa:
    """Quartis por interpolação linear, bigodes até 1,5·IQR e os valores além deles."""
    numeros = valores.dropna().to_numpy(dtype="float64")
    q1, mediana, q3 = (float(q) for q in np.quantile(numeros, QUARTIS, method="linear"))
    inferior, superior = q1 - FATOR_IQR * (q3 - q1), q3 + FATOR_IQR * (q3 - q1)
    dentro = numeros[(numeros >= inferior) & (numeros <= superior)]
    fora = np.sort(numeros[(numeros < inferior) | (numeros > superior)])
    return ResumoCaixa(
        minimo=float(numeros.min()),
        q1=q1,
        mediana=mediana,
        q3=q3,
        maximo=float(numeros.max()),
        media=float(numeros.mean()),
        bigode_inferior=float(dentro.min()),
        bigode_superior=float(dentro.max()),
        discrepantes=tuple(float(v) for v in fora[:MAX_DISCREPANTES]),
    )


def boxplot(caixa: ResumoCaixa, coluna: str) -> Figura:
    """Boxplot horizontal com estatísticas prontas e média; discrepantes como pontos à parte."""
    caixa_traco = {
        "type": "box",
        "orientation": "h",
        "y": [coluna],
        "q1": [caixa.q1],
        "median": [caixa.mediana],
        "q3": [caixa.q3],
        "lowerfence": [caixa.bigode_inferior],
        "upperfence": [caixa.bigode_superior],
        "mean": [caixa.media],
        "boxmean": True,
        "marker": {"color": COR_PRINCIPAL},
        "line": {"color": COR_PRINCIPAL},
    }
    pontos = {
        "type": "scatter",
        "mode": "markers",
        "x": list(caixa.discrepantes),
        "y": [coluna] * len(caixa.discrepantes),
        "marker": {"color": COR_REFERENCIA, "size": 7},
    }
    return _figura([caixa_traco, pontos], coluna, "")


def _linha(x: list[float | None], y: list[float | None], forma: str = "linear") -> dict[str, Any]:
    linha = {"color": COR_PRINCIPAL, "width": LARGURA_LINHA, "shape": forma}
    return {"type": "scatter", "mode": "lines+markers", "x": x, "y": y, "line": linha}


def ogiva(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Fr% acumulada nos limites superiores das classes, partindo de 0."""
    x = [barras[0].inferior, *(b.superior for b in barras)]
    y: list[float | None] = [0.0, *(b.acumulado_pct for b in barras)]
    return _figura([_linha(x, y)], coluna, EIXO_ACUMULADA)


def acumulada_categorias(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Ordinal: barras da frequência acumulada na ordem da escala."""
    traco = {
        "type": "bar",
        "x": [b.rotulo for b in barras],
        "y": [b.acumulado_pct for b in barras],
        "marker": MARCADOR_BARRA,
    }
    return _figura([traco], coluna, EIXO_ACUMULADA)


def acumulada_escada(barras: tuple[Barra, ...], coluna: str) -> Figura:
    """Discreta: frequência acumulada em escada."""
    traco = _linha([b.valor for b in barras], [b.acumulado_pct for b in barras], forma="hv")
    return _figura([traco], coluna, EIXO_ACUMULADA)


def pizza(barras: tuple[Barra, ...]) -> Figura:
    """Só para até 5 categorias (spec 08)."""
    traco = {
        "type": "pie",
        "labels": [b.rotulo for b in barras],
        "values": [b.frequencia for b in barras],
        "sort": False,
        "textinfo": "label+percent",
    }
    return {"data": [traco], "layout": {"showlegend": False, "separators": ",."}}
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/graficos/figuras.py tests/dominios/graficos/test_figuras.py
git commit -m "feat(graficos): monta barras, bastões, histograma, boxplot, ogiva e pizza sem dados brutos"
```

---

### Tarefa 3: textos e fábrica por tipo

**Arquivos:**
- Criar: `backend/app/dominios/graficos/textos.py`, `backend/app/dominios/graficos/fabrica.py`
- Teste: `backend/tests/dominios/graficos/test_fabrica.py`

**Passo 1: escrever os testes (falham)**
```python
import pandas as pd
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.graficos.entradas import Barra, DadosUnivariados
from app.dominios.graficos.fabrica import figuras_univariadas

CATEGORIAS = tuple(Barra(f"c{i}", 10 - i, 10.0, 10.0 * (i + 1)) for i in range(6))
CLASSES = (
    Barra("2,0 ⊢ 3,9", 2, 40.0, 40.0, inferior=2.0, superior=3.9),
    Barra("3,9 ⊢ 5,8", 3, 60.0, 100.0, inferior=3.9, superior=5.8),
)
VALORES = pd.Series([2.0, 3.0, 4.0, 5.0, 5.5])


def _dados(
    tipo: TipoVariavel, barras: tuple[Barra, ...], valores: pd.Series | None = None
) -> DadosUnivariados:
    return DadosUnivariados("x", tipo, sum(b.frequencia for b in barras), barras, valores)


@pytest.mark.parametrize(
    ("tipo", "barras", "valores", "ids"),
    [
        (TipoVariavel.NOMINAL, CATEGORIAS, None, ["principal"]),
        (TipoVariavel.NOMINAL, CATEGORIAS[:3], None, ["principal", "pizza"]),
        (TipoVariavel.BINARIA, CATEGORIAS[:2], None, ["principal"]),
        (TipoVariavel.ORDINAL, CATEGORIAS, None, ["principal", "acumulada"]),
        (TipoVariavel.CONTINUA, CLASSES, VALORES, ["principal", "boxplot", "ogiva"]),
        (TipoVariavel.IDENTIFICADOR, CATEGORIAS, None, []),
    ],
)
def test_figuras_por_tipo(
    tipo: TipoVariavel, barras: tuple[Barra, ...], valores: pd.Series | None, ids: list[str]
) -> None:
    resultado = figuras_univariadas(_dados(tipo, barras, valores))

    assert [f.id for f in resultado] == ids


def test_discreta_tem_bastoes_boxplot_e_escada() -> None:
    barras = tuple(Barra(str(v), 1, 20.0, 20.0 * (i + 1), valor=v) for i, v in enumerate(VALORES))

    resultado = figuras_univariadas(_dados(TipoVariavel.DISCRETA, barras, VALORES))

    assert [f.rotulo for f in resultado] == ["Bastões", "Boxplot", "Acumulada"]


def test_principal_recomendada_com_titulo_resumo_e_porque() -> None:
    principal, *_ = figuras_univariadas(_dados(TipoVariavel.CONTINUA, CLASSES, VALORES))

    assert principal.recomendado is True
    assert principal.rotulo == "Histograma"
    assert principal.titulo == "Distribuição de x (n = 5)"
    assert principal.resumo == "A classe mais comum é 3,9 ⊢ 5,8, com 3 valores (60,0%)."
    assert principal.porque.startswith("Para números contínuos")


def test_complementares_nao_sao_recomendadas() -> None:
    _, boxplot, ogiva = figuras_univariadas(_dados(TipoVariavel.CONTINUA, CLASSES, VALORES))

    assert not boxplot.recomendado
    assert ogiva.resumo == "Metade dos valores chega até 3,9 ⊢ 5,8."
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar**

`app/dominios/graficos/textos.py` — títulos no formato do design ("Distribuição de peso_kg (n = 227)"), "Por que este gráfico?" da spec 08 e resumos com números:
```python
"""Títulos, "Por que este gráfico?" e resumos textuais das figuras (spec 08, spec 16)."""

from app.compartilhado.numeros import formatar_numero, formatar_percentual
from app.dominios.graficos.entradas import Barra, DadosUnivariados, ResumoCaixa

METADE_PCT = 50

ROTULOS = {
    "barras": "Barras",
    "bastoes": "Bastões",
    "histograma": "Histograma",
    "boxplot": "Boxplot",
    "ogiva": "Ogiva",
    "acumulada": "Acumulada",
    "pizza": "Pizza",
}

PORQUE = {
    "barras_nominal": (
        "Categorias sem ordem são comparadas pelo tamanho. Ordenamos da maior para a menor "
        "para facilitar a leitura."
    ),
    "barras_binaria": "Com só duas categorias, barras com o percentual mostram tudo de uma vez.",
    "barras_ordinal": "A ordem das categorias tem significado, então as barras seguem a escala.",
    "bastoes": "Valores inteiros são pontos isolados, não intervalos; cada haste é um valor.",
    "histograma": (
        "Para números contínuos, agrupar em classes mostra a forma da distribuição, "
        "onde fica o centro e como são as caudas."
    ),
    "boxplot": ("Mostra a mediana, os quartis e os valores muito afastados em um só desenho."),
    "ogiva": "A curva acumulada mostra quantos valores ficam abaixo de cada limite de classe.",
    "acumulada": "Mostra quanto dos dados já foi somado até cada categoria ou valor.",
    "pizza": "Com até 5 categorias, a pizza mostra bem a parte de cada uma no total.",
}


def titulo_distribuicao(dados: DadosUnivariados) -> str:
    return f"Distribuição de {dados.coluna} (n = {dados.n})"


def titulo_categorias(dados: DadosUnivariados) -> str:
    return f"Frequência de {dados.coluna} (n = {dados.n}), da maior para a menor"


def titulo_boxplot(dados: DadosUnivariados) -> str:
    return f"Boxplot de {dados.coluna}"


def titulo_ogiva(dados: DadosUnivariados) -> str:
    return f"Frequência acumulada (ogiva) de {dados.coluna}"


def titulo_acumulada(dados: DadosUnivariados) -> str:
    return f"Frequência acumulada de {dados.coluna}"


def titulo_pizza(dados: DadosUnivariados) -> str:
    return f"Parte de cada categoria de {dados.coluna}"


def _mais_frequente(barras: tuple[Barra, ...]) -> Barra:
    return max(barras, key=lambda b: b.frequencia)


def resumo_mais_frequente(dados: DadosUnivariados, nome: str) -> str:
    """ "A classe mais comum é 65,5 ⊢ 71,0, com 49 valores (21,6%)."."""
    barra = _mais_frequente(dados.barras)
    valores = "valor" if barra.frequencia == 1 else "valores"
    return (
        f"{nome} mais comum é {barra.rotulo}, com {barra.frequencia} {valores} "
        f"({formatar_percentual(barra.percentual)})."
    )


def resumo_caixa(caixa: ResumoCaixa) -> str:
    texto = (
        f"Metade dos valores fica entre {formatar_numero(caixa.q1)} e "
        f"{formatar_numero(caixa.q3)}; a mediana é {formatar_numero(caixa.mediana)}."
    )
    n = len(caixa.discrepantes)
    if n:
        texto += f" {n} {'valor fica' if n == 1 else 'valores ficam'} muito longe dos demais."
    return texto


def resumo_acumulada(dados: DadosUnivariados) -> str:
    """Onde a frequência acumulada chega a 50%."""
    metade = next(b for b in dados.barras if (b.acumulado_pct or 0) >= METADE_PCT)
    return f"Metade dos valores chega até {metade.rotulo}."
```

`app/dominios/graficos/fabrica.py` — tabela `FABRICA` (tipo → função), sem `if` por tipo:
```python
"""Fábrica: o melhor gráfico para cada tipo de variável, num só lugar (spec 08, ADR 0003)."""

from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from app.compartilhado.numeros import formatar_percentual
from app.compartilhado.tipos import TipoVariavel
from app.dominios.graficos import figuras, textos
from app.dominios.graficos.entradas import DadosUnivariados, FiguraPronta
from app.dominios.graficos.figuras import Figura

MAX_FATIAS_PIZZA = 5


@dataclass(frozen=True, slots=True)
class _Molde:
    id: str
    tipo_grafico: str
    porque: str
    recomendado: bool = False


MOLDES = {
    "barras_nominal": _Molde("principal", "barras", textos.PORQUE["barras_nominal"], True),
    "barras_binaria": _Molde("principal", "barras", textos.PORQUE["barras_binaria"], True),
    "barras_ordinal": _Molde("principal", "barras", textos.PORQUE["barras_ordinal"], True),
    "bastoes": _Molde("principal", "bastoes", textos.PORQUE["bastoes"], True),
    "histograma": _Molde("principal", "histograma", textos.PORQUE["histograma"], True),
    "boxplot": _Molde("boxplot", "boxplot", textos.PORQUE["boxplot"]),
    "ogiva": _Molde("ogiva", "ogiva", textos.PORQUE["ogiva"]),
    "acumulada": _Molde("acumulada", "acumulada", textos.PORQUE["acumulada"]),
    "pizza": _Molde("pizza", "pizza", textos.PORQUE["pizza"]),
}


def _pronta(molde: _Molde, titulo: str, resumo: str, figura: Figura) -> FiguraPronta:
    return FiguraPronta(
        id=molde.id,
        rotulo=textos.ROTULOS[molde.tipo_grafico],
        titulo=titulo,
        resumo=resumo,
        porque=molde.porque,
        recomendado=molde.recomendado,
        dados=figura,
    )


def _boxplot(dados: DadosUnivariados, valores: pd.Series) -> FiguraPronta:
    caixa = figuras.resumo_caixa(valores)
    return _pronta(
        MOLDES["boxplot"],
        textos.titulo_boxplot(dados),
        textos.resumo_caixa(caixa),
        figuras.boxplot(caixa, dados.coluna),
    )


def _pizza(dados: DadosUnivariados) -> FiguraPronta:
    maior = max(dados.barras, key=lambda b: b.frequencia)
    resumo = f"{maior.rotulo} representa {formatar_percentual(maior.percentual)} do total."
    return _pronta(MOLDES["pizza"], textos.titulo_pizza(dados), resumo, figuras.pizza(dados.barras))


def _nominal(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    principal = _pronta(
        MOLDES["barras_nominal"],
        textos.titulo_categorias(dados),
        textos.resumo_mais_frequente(dados, "A categoria"),
        figuras.barras_horizontais(dados.barras, dados.coluna),
    )
    if len(dados.barras) > MAX_FATIAS_PIZZA:
        return (principal,)
    return (principal, _pizza(dados))


def _binaria(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    principal = _pronta(
        MOLDES["barras_binaria"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "A categoria"),
        figuras.barras_verticais(dados.barras, dados.coluna),
    )
    return (principal,)


def _ordinal(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    principal = _pronta(
        MOLDES["barras_ordinal"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "A categoria"),
        figuras.barras_verticais(dados.barras, dados.coluna),
    )
    acumulada = _pronta(
        MOLDES["acumulada"],
        textos.titulo_acumulada(dados),
        textos.resumo_acumulada(dados),
        figuras.acumulada_categorias(dados.barras, dados.coluna),
    )
    return (principal, acumulada)


def _discreta(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    valores = dados.valores if dados.valores is not None else pd.Series(dtype="float64")
    principal = _pronta(
        MOLDES["bastoes"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "O valor"),
        figuras.bastoes(dados.barras, dados.coluna),
    )
    acumulada = _pronta(
        MOLDES["acumulada"],
        textos.titulo_acumulada(dados),
        textos.resumo_acumulada(dados),
        figuras.acumulada_escada(dados.barras, dados.coluna),
    )
    return (principal, _boxplot(dados, valores), acumulada)


def _continua(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    valores = dados.valores if dados.valores is not None else pd.Series(dtype="float64")
    principal = _pronta(
        MOLDES["histograma"],
        textos.titulo_distribuicao(dados),
        textos.resumo_mais_frequente(dados, "A classe"),
        figuras.histograma(dados.barras, dados.coluna),
    )
    ogiva = _pronta(
        MOLDES["ogiva"],
        textos.titulo_ogiva(dados),
        textos.resumo_acumulada(dados),
        figuras.ogiva(dados.barras, dados.coluna),
    )
    return (principal, _boxplot(dados, valores), ogiva)


FABRICA: dict[TipoVariavel, Callable[[DadosUnivariados], tuple[FiguraPronta, ...]]] = {
    TipoVariavel.NOMINAL: _nominal,
    TipoVariavel.BINARIA: _binaria,
    TipoVariavel.ORDINAL: _ordinal,
    TipoVariavel.DISCRETA: _discreta,
    TipoVariavel.CONTINUA: _continua,
}


def figuras_univariadas(dados: DadosUnivariados) -> tuple[FiguraPronta, ...]:
    """Gráfico principal + complementares do tipo; a 1ª figura é sempre a recomendada."""
    construir = FABRICA.get(dados.tipo)
    return construir(dados) if construir else ()
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/graficos/textos.py app/dominios/graficos/fabrica.py tests/dominios/graficos/test_fabrica.py
git commit -m "feat(graficos): escolhe o gráfico principal e os complementares por tipo de variável"
```

---

### Tarefa 4: fachada do domínio graficos

**Arquivos:**
- Criar: `backend/app/dominios/graficos/servico.py`
- Teste: `backend/tests/dominios/graficos/test_servico.py`

**Passo 1: escrever os testes (falham)**
```python
from app.dominios.graficos.servico import (
    codigo_plotlyjs,
    endereco_plotlyjs_cdn,
    figura_html,
)


def test_figura_html_aplica_o_tema_claro_e_escapa_o_script() -> None:
    dados = {"data": [{"type": "bar", "x": ["</script>"], "y": [1]}], "layout": {"bargap": 0}}

    html = figura_html("figura-1", dados)

    assert html.startswith('<div id="figura-1" class="grafico"></div>')
    assert "Plotly.newPlot(" in html
    assert '"separators": ",."' in html
    assert '"bargap": 0' in html
    assert '</script>"' not in html


def test_plotlyjs_embutido_e_cdn_da_mesma_versao() -> None:
    codigo = codigo_plotlyjs()
    endereco = endereco_plotlyjs_cdn()

    assert "plotly.js v" in codigo[:200]
    assert endereco.startswith("https://cdn.plot.ly/plotly-")
    versao = endereco.removeprefix("https://cdn.plot.ly/plotly-").removesuffix(".min.js")
    assert f"plotly.js v{versao}" in codigo[:200]
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar `app/dominios/graficos/servico.py`** — sem estado: funções (a classe da D54 vale para domínios com estado ou dependências; registrar isso na D54 na Tarefa 10):
```python
"""Fachada do domínio graficos: figuras por tipo e HTML para o relatório (spec 08).

Sem estado nem dependências: funções simples (a classe de fachada da D54 só vale para domínios
com estado ou que dependem de outros).
"""

import html
import json
import re
from collections.abc import Mapping
from importlib import resources
from typing import Any

from app.dominios.graficos.entradas import Barra, DadosUnivariados, FiguraPronta
from app.dominios.graficos.fabrica import figuras_univariadas
from app.dominios.graficos.tema import layout_claro, mesclar

__all__ = [
    "Barra",
    "DadosUnivariados",
    "FiguraPronta",
    "codigo_plotlyjs",
    "endereco_plotlyjs_cdn",
    "figura_html",
    "figuras_univariadas",
]

CONFIG_RELATORIO = {"displaylogo": False, "responsive": True}
ARQUIVO_PLOTLYJS = ("plotly", "package_data", "plotly.min.js")
_VERSAO = re.compile(r"plotly\.js v(\d+\.\d+\.\d+)")
ESCAPE_FECHAMENTO = r"<\/"


def figura_html(identificador: str, dados: Mapping[str, Any]) -> str:
    """<div> + <script> que desenha a figura com o tema claro (o plotly.js entra uma vez só)."""
    figura = {
        "data": list(dados.get("data", [])),
        "layout": mesclar(layout_claro(), dict(dados.get("layout", {}))),
    }
    argumentos = ", ".join(
        json.dumps(parte, ensure_ascii=False)
        for parte in (identificador, figura["data"], figura["layout"], CONFIG_RELATORIO)
    )
    # "</" dentro de um <script> fecharia a tag antes da hora.
    seguro = argumentos.replace("</", ESCAPE_FECHAMENTO)
    alvo = html.escape(identificador)
    return f'<div id="{alvo}" class="grafico"></div>\n<script>Plotly.newPlot({seguro});</script>'


def codigo_plotlyjs() -> str:
    """plotly.js que acompanha o pacote Python, para o relatório funcionar sem internet."""
    pasta, *resto = ARQUIVO_PLOTLYJS
    return resources.files(pasta).joinpath(*resto).read_text(encoding="utf-8")


def endereco_plotlyjs_cdn() -> str:
    """Endereço da mesma versão do plotly.js no CDN oficial."""
    casamento = _VERSAO.search(codigo_plotlyjs()[:200])
    versao = casamento.group(1) if casamento else "latest"
    return f"https://cdn.plot.ly/plotly-{versao}.min.js"
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/graficos/servico.py tests/dominios/graficos/test_servico.py
git commit -m "feat(graficos): expõe figuras por tipo e HTML das figuras para o relatório"
```

---

### Tarefa 5: figuras na análise

**Arquivos:**
- Modificar: `backend/app/dominios/analise/servico.py`, `backend/tests/dominios/analise/test_router.py`

**Passo 1: atualizar o teste (falha)** — em `tests/dominios/analise/test_router.py`, `test_analise_de_coluna_continua`, trocar `assert corpo["figuras"] == []` por:
```python
    assert [f["id"] for f in corpo["figuras"]] == ["principal", "boxplot", "ogiva"]
    assert corpo["figuras"][0]["rotulo"] == "Histograma"
    assert corpo["figuras"][0]["recomendado"] is True
```

**Passo 2: rodar e ver falhar** — `pytest tests/dominios/analise/test_router.py --no-cov`

**Passo 3: implementar** — `app/dominios/analise/servico.py` completo (`_barras` converte a tabela de frequências; `_figuras` pede as figuras ao domínio graficos; `analisar` devolve a análise com `figuras`):
```python
"""Fachada do domínio analise: análise univariada e "onde está meu valor?" (D54)."""

from dataclasses import replace

from app.compartilhado.tipos import TIPOS_NUMERICOS, TipoVariavel
from app.dominios.analise import erros
from app.dominios.analise.posicao import calcular_posicao
from app.dominios.analise.resultados import (
    Amostra,
    Analise,
    Figura,
    Posicao,
    TabelaFrequencia,
    TipoSeparatriz,
)
from app.dominios.analise.univariada import analisar_amostra
from app.dominios.datasets.servico import ServicoDatasets
from app.dominios.graficos.servico import Barra, DadosUnivariados, figuras_univariadas

__all__ = ["Analise", "Figura", "Posicao", "ServicoAnalise", "TipoSeparatriz"]


def _barras(tabela: TabelaFrequencia) -> tuple[Barra, ...]:
    return tuple(
        Barra(
            rotulo=linha.rotulo,
            frequencia=linha.fi,
            percentual=linha.fr_pct,
            acumulado_pct=linha.fr_acum_pct,
            valor=linha.valor if isinstance(linha.valor, float) else None,
            inferior=linha.limite_inferior,
            superior=linha.limite_superior,
        )
        for linha in tabela.linhas
    )


def _figuras(amostra: Amostra, analise: Analise) -> tuple[Figura, ...]:
    """Pede ao domínio graficos as figuras do tipo (spec 08) a partir da tabela já calculada."""
    numerica = amostra.tipo in TIPOS_NUMERICOS
    dados = DadosUnivariados(
        coluna=amostra.coluna,
        tipo=amostra.tipo,
        n=amostra.n,
        barras=_barras(analise.frequencias),
        valores=amostra.valores if numerica else None,
    )
    return tuple(
        Figura(f.id, f.rotulo, f.titulo, f.resumo, f.porque, f.recomendado, f.dados)
        for f in figuras_univariadas(dados)
    )


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
        """Frequências, tendência, separatrizes, dispersão e gráficos da coluna (specs 04–08)."""
        amostra = self.amostra(dataset_id, coluna)
        analise = analisar_amostra(amostra, classes, sucesso)
        return replace(analise, figuras=_figuras(amostra, analise))

    def posicao(self, dataset_id: str, coluna: str, valor: float, tipo: TipoSeparatriz) -> Posicao:
        """Em que separatriz o valor cai (spec 06)."""
        amostra = self.amostra(dataset_id, coluna)
        if amostra.tipo not in TIPOS_NUMERICOS:
            raise erros.posicao_nao_aplicavel()
        return calcular_posicao(amostra.valores.to_numpy(dtype="float64"), valor, tipo)
```

**Passo 4: rodar a suíte** — `pytest` (o teste de arquitetura confirma que `analise` só usa `graficos` pela fachada).

**Passo 5: commit**
```bash
git add app/dominios/analise/servico.py tests/dominios/analise/test_router.py
git commit -m "feat(analise): inclui as figuras do tipo na análise da coluna"
```

---

### Tarefa 6: conteúdo e textos do relatório

**Arquivos:**
- Criar: `backend/app/dominios/relatorio/conteudo.py`, `backend/app/dominios/relatorio/textos.py`
- Teste: `backend/tests/dominios/relatorio/__init__.py` (vazio), `backend/tests/dominios/relatorio/test_textos.py`

**Passo 1: escrever os testes (falham)**
```python
import pytest

from app.dominios.relatorio.conteudo import DadosLeitura
from app.dominios.relatorio.textos import descrever_leitura, subtitulo


def test_descrever_leitura_de_txt() -> None:
    dados = DadosLeitura("txt", ";", ",", "utf-8", True, 230, 8)

    assert descrever_leitura(dados) == (
        "Arquivo de texto separado por ponto e vírgula, decimal com vírgula, codificação UTF-8 "
        "e cabeçalho na primeira linha. Foram lidas 230 linhas e 8 colunas."
    )


def test_descrever_leitura_de_planilha() -> None:
    dados = DadosLeitura("xlsx", None, None, None, True, 1, 1)

    assert descrever_leitura(dados) == (
        "Planilha do Excel com cabeçalho na primeira linha. Foram lidas 1 linha e 1 coluna."
    )


@pytest.mark.parametrize(
    ("n", "original", "esperado"),
    [
        (227, 230, "pesquisa.txt · 227 linhas após limpeza × 8 colunas"),
        (230, 230, "pesquisa.txt · 230 linhas × 8 colunas"),
    ],
)
def test_subtitulo(n: int, original: int, esperado: str) -> None:
    assert subtitulo("pesquisa.txt", n, original, 8) == esperado
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar**

`app/dominios/relatorio/conteudo.py` — só textos prontos; a montagem não calcula nada:
```python
"""Conteúdo do mini relatório já em texto (spec 13); a montagem só encaixa no template."""

from dataclasses import dataclass
from typing import Literal

type Secao = Literal["leitura", "tipos", "limpeza", "analises"]

SECOES_M1: tuple[Secao, ...] = ("leitura", "tipos", "limpeza", "analises")


@dataclass(frozen=True, slots=True)
class DadosLeitura:
    formato: str
    separador: str | None
    decimal: str | None
    codificacao: str | None
    tem_cabecalho: bool | None
    n_linhas: int
    n_colunas: int


@dataclass(frozen=True, slots=True)
class LinhaTipo:
    coluna: str
    tipo: str
    motivo: str


@dataclass(frozen=True, slots=True)
class ItemMedida:
    rotulo: str
    valor: str


@dataclass(frozen=True, slots=True)
class FormulaTexto:
    nome: str
    latex: str
    texto: str


@dataclass(frozen=True, slots=True)
class FiguraRelatorio:
    titulo: str
    resumo: str
    html: str


@dataclass(frozen=True, slots=True)
class SecaoColuna:
    coluna: str
    tipo: str
    n: int
    n_faltantes: int
    cabecalho_tabela: tuple[str, ...]
    linhas_tabela: tuple[tuple[str, ...], ...]
    medidas: tuple[ItemMedida, ...]
    separatrizes: str | None
    interpretacoes: tuple[str, ...]
    figura: FiguraRelatorio | None
    formulas: tuple[FormulaTexto, ...]


@dataclass(frozen=True, slots=True)
class ConteudoRelatorio:
    nome_arquivo: str
    gerado_em: str
    subtitulo: str
    script_plotly: str
    leitura: str | None = None
    tipos: tuple[LinhaTipo, ...] | None = None
    limpeza: tuple[str, ...] | None = None
    colunas: tuple[SecaoColuna, ...] | None = None
```

`app/dominios/relatorio/textos.py`
```python
"""Frases do relatório (spec 13 e 16)."""

from app.compartilhado.numeros import formatar_inteiro
from app.compartilhado.textos import juntar_lista, pluralizar
from app.dominios.relatorio.conteudo import DadosLeitura

FORMATOS = {
    "txt": "Arquivo de texto",
    "csv": "Arquivo CSV",
    "tsv": "Arquivo TSV",
    "xlsx": "Planilha do Excel",
    "json": "Arquivo JSON",
}
SEPARADORES = {
    ";": "ponto e vírgula",
    ",": "vírgula",
    "\t": "tabulação",
    "|": "barra vertical",
    r"\s{2,}": "espaços",
}
DECIMAIS = {",": "decimal com vírgula", ".": "decimal com ponto"}
TIPOS_LEGIVEIS = {
    "nominal": "Qualitativa nominal",
    "ordinal": "Qualitativa ordinal",
    "discreta": "Quantitativa discreta",
    "continua": "Quantitativa contínua",
    "binaria": "Binária",
    "identificador": "Identificador (ignorada)",
}
SEM_LIMPEZA = "Nenhuma ação de limpeza foi aplicada."
TITULOS_SECOES = {
    "leitura": "Leitura do arquivo",
    "tipos": "Tipos de variável",
    "limpeza": "Limpeza",
}


def _quantidade(n: int, singular: str, plural: str) -> str:
    return f"{formatar_inteiro(n)} {pluralizar(n, singular, plural)}"


def descrever_leitura(dados: DadosLeitura) -> str:
    """Ex.: "Arquivo de texto separado por ponto e vírgula, decimal com vírgula, …"."""
    partes = []
    if dados.separador:
        partes.append(f"separado por {SEPARADORES.get(dados.separador, dados.separador)}")
    if dados.decimal:
        partes.append(DECIMAIS.get(dados.decimal, f"decimal {dados.decimal}"))
    if dados.codificacao:
        partes.append(f"codificação {dados.codificacao.upper()}")
    if dados.tem_cabecalho is not None:
        partes.append("cabeçalho na primeira linha" if dados.tem_cabecalho else "sem cabeçalho")
    if partes and not partes[0].startswith("separado"):
        partes[0] = f"com {partes[0]}"
    inicio = FORMATOS.get(dados.formato, "Arquivo")
    descricao = f"{inicio} {juntar_lista(partes)}." if partes else f"{inicio}."
    linhas = _quantidade(dados.n_linhas, "linha", "linhas")
    colunas = _quantidade(dados.n_colunas, "coluna", "colunas")
    return f"{descricao} Foram lidas {linhas} e {colunas}."


def subtitulo(nome_arquivo: str, n_linhas: int, n_linhas_original: int, n_colunas: int) -> str:
    """Ex.: "pesquisa_saude.txt · 227 linhas após limpeza × 8 colunas"."""
    linhas = _quantidade(n_linhas, "linha", "linhas")
    if n_linhas != n_linhas_original:
        linhas += " após limpeza"
    return f"{nome_arquivo} · {linhas} × {_quantidade(n_colunas, 'coluna', 'colunas')}"
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/relatorio/conteudo.py app/dominios/relatorio/textos.py tests/dominios/relatorio
git commit -m "feat(relatorio): define o conteúdo do mini relatório e as frases de leitura"
```

---

### Tarefa 7: template e montagem

**Arquivos:**
- Criar: `backend/app/dominios/relatorio/templates/relatorio.html.j2`, `backend/app/dominios/relatorio/templates/estilos.css`, `backend/app/dominios/relatorio/montagem.py`
- Modificar: `backend/pyproject.toml`
- Teste: `backend/tests/dominios/relatorio/test_montagem.py`

**Passo 1: escrever o teste (falha)**
```python
from app.dominios.relatorio.conteudo import ConteudoRelatorio, LinhaTipo
from app.dominios.relatorio.montagem import renderizar


def test_renderizar_escapa_textos_e_numera_secoes() -> None:
    conteudo = ConteudoRelatorio(
        nome_arquivo="a.csv",
        gerado_em="03/10/2026 10:00",
        subtitulo="a.csv · 3 linhas × 1 coluna",
        script_plotly="<script>/* plotly */</script>",
        leitura="Arquivo CSV.",
        tipos=(LinhaTipo("<b>x</b>", "Binária", "Tem só dois valores."),),
    )

    html = renderizar(conteudo)

    assert "<h2>1. Leitura do arquivo</h2>" in html
    assert "<h2>2. Tipos de variável</h2>" in html
    assert "&lt;b&gt;x&lt;/b&gt;" in html
    assert "<script>/* plotly */</script>" in html
    assert "Limpeza" not in html
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar**

`templates/relatorio.html.j2` — estrutura do print 8a: régua no cabeçalho, título 22/700, seções numeradas, tabelas com régua, "Figura N · título", rodapé. Textos escapados; só o HTML das figuras e o script do Plotly entram com `| safe`. KaTeX pelo CDN troca o texto das fórmulas quando estiver disponível; sem internet, fica o texto (spec 13):
```jinja
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relatório estatístico · {{ c.nome_arquivo }}</title>
  <style>
{% include "estilos.css" %}
  </style>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"></script>
  {{ c.script_plotly | safe }}
</head>
<body>
  <header class="cabecalho">
    <div class="marca"><span>Analisador e Gerador de Dados</span><span>{{ c.gerado_em }}</span></div>
    <h1>Relatório estatístico</h1>
    <p class="subtitulo">{{ c.subtitulo }}</p>
  </header>
  {% set numero = namespace(secao=0, figura=0) %}

  {% if c.leitura is not none %}
  {% set numero.secao = numero.secao + 1 %}
  <section>
    <h2>{{ numero.secao }}. {{ titulos.leitura }}</h2>
    <p>{{ c.leitura }}</p>
  </section>
  {% endif %}

  {% if c.tipos is not none %}
  {% set numero.secao = numero.secao + 1 %}
  <section>
    <h2>{{ numero.secao }}. {{ titulos.tipos }}</h2>
    <table>
      <thead><tr><th scope="col">Coluna</th><th scope="col">Tipo</th><th scope="col">Motivo</th></tr></thead>
      <tbody>
      {% for t in c.tipos %}
        <tr><td class="mono">{{ t.coluna }}</td><td>{{ t.tipo }}</td><td>{{ t.motivo }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </section>
  {% endif %}

  {% if c.limpeza is not none %}
  {% set numero.secao = numero.secao + 1 %}
  <section>
    <h2>{{ numero.secao }}. {{ titulos.limpeza }}</h2>
    <p>{{ c.limpeza | join(" ") }}</p>
  </section>
  {% endif %}

  {% for col in c.colunas or [] %}
  {% set numero.secao = numero.secao + 1 %}
  <section class="coluna">
    <h2>{{ numero.secao }}. Análise de <span class="mono">{{ col.coluna }}</span></h2>
    <p class="nota">{{ col.tipo }} · {{ col.n }} valores válidos{% if col.n_faltantes %} · {{ col.n_faltantes }} faltantes{% endif %}</p>
    {% if col.medidas %}
    <dl class="medidas">
      {% for m in col.medidas %}<div><dt>{{ m.rotulo }}</dt><dd class="mono">{{ m.valor }}</dd></div>{% endfor %}
    </dl>
    {% endif %}
    {% if col.separatrizes %}<p class="mono">{{ col.separatrizes }}</p>{% endif %}
    <table class="frequencias">
      <thead><tr>{% for titulo in col.cabecalho_tabela %}<th scope="col">{{ titulo }}</th>{% endfor %}</tr></thead>
      <tbody>
      {% for linha in col.linhas_tabela %}
        <tr>{% for celula in linha %}<td{% if not loop.first %} class="numero"{% endif %}>{{ celula }}</td>{% endfor %}</tr>
      {% endfor %}
      </tbody>
    </table>
    {% if col.figura %}
    {% set numero.figura = numero.figura + 1 %}
    <figure>
      <figcaption>Figura {{ numero.figura }} · {{ col.figura.titulo }}</figcaption>
      {{ col.figura.html | safe }}
      <p class="nota">{{ col.figura.resumo }}</p>
    </figure>
    {% endif %}
    {% for frase in col.interpretacoes %}<p>{{ frase }}</p>{% endfor %}
    {% if col.formulas %}
    <h3>Fórmulas usadas</h3>
    <ul class="formulas">
      {% for f in col.formulas %}<li>{{ f.nome }}: <span class="formula" data-latex="{{ f.latex }}">{{ f.texto }}</span></li>{% endfor %}
    </ul>
    {% endif %}
  </section>
  {% endfor %}

  <footer class="rodape">Disciplina de Estatística · gerado pelo Analisador e Gerador de Dados</footer>
  <script>
    window.addEventListener("load", function () {
      if (!window.katex) return;
      document.querySelectorAll(".formula[data-latex]").forEach(function (el) {
        try { window.katex.render(el.dataset.latex, el, { throwOnError: false }); } catch (e) { /* mantém o texto */ }
      });
    });
  </script>
</body>
</html>
```

`templates/estilos.css` — sempre claro (D47); `@media print` com quebra por coluna analisada e A4:
```css
/* Relatório sempre no tema claro (D47); valores de docs/design/tokens.md e telas.md §8. */
:root { --texto: #161a20; --texto-2: #4b5462; --borda: #dadee4; --borda-forte: #868f9c; --fundo-2: #f0f2f5; --zebra: #f7f8fa; }
* { box-sizing: border-box; }
body { margin: 0 auto; max-width: 820px; padding: 48px 52px; background: #fff; color: var(--texto); font: 11pt/1.55 Inter, system-ui, sans-serif; }
.mono { font-family: "JetBrains Mono", ui-monospace, monospace; }
.cabecalho { border-bottom: 1.5px solid var(--texto); padding-bottom: 12px; margin-bottom: 24px; }
.marca { display: flex; justify-content: space-between; font: 600 8pt/1.4 "JetBrains Mono", monospace; text-transform: uppercase; letter-spacing: .04em; }
h1 { font-size: 22pt; font-weight: 700; margin: 16px 0 4px; }
.subtitulo, .nota { color: var(--texto-2); font-size: 9.5pt; margin: 4px 0; }
h2 { font-size: 13pt; font-weight: 700; margin: 24px 0 8px; }
h3 { font-size: 11pt; margin: 16px 0 6px; }
table { width: 100%; border-collapse: collapse; font-size: 10.5pt; margin: 8px 0 16px; }
th { text-align: left; font-weight: 600; border-bottom: 1px solid var(--borda-forte); padding: 4px 8px; }
td { border-bottom: 1px solid var(--borda); padding: 4px 8px; }
tbody tr:nth-child(even) { background: var(--zebra); }
td.numero { text-align: right; font-variant-numeric: tabular-nums; }
.medidas { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 0; border: 1px solid var(--borda); margin: 8px 0; }
.medidas div { padding: 6px 10px; border-right: 1px solid var(--borda); }
.medidas dt { font-size: 8pt; color: var(--texto-2); }
.medidas dd { margin: 0; font-size: 12pt; font-weight: 600; }
figure { margin: 16px 0; break-inside: avoid; }
figcaption { font-weight: 600; font-size: 10.5pt; margin-bottom: 4px; }
.grafico { width: 100%; height: 320px; }
.formulas { font-size: 10pt; padding-left: 18px; }
.rodape { margin-top: 32px; padding-top: 8px; border-top: 1px solid var(--borda); color: var(--texto-2); font: 8pt/1.4 "JetBrains Mono", monospace; }
@page { size: A4 portrait; margin: 18mm; }
@media print {
  body { padding: 0; max-width: none; }
  section.coluna { break-before: page; }
  .grafico { width: 100% !important; }
}
```

`app/dominios/relatorio/montagem.py`
```python
"""Monta o HTML do relatório com Jinja2 (spec 13): arquivo único, CSS embutido."""

from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.dominios.relatorio.conteudo import ConteudoRelatorio
from app.dominios.relatorio.textos import TITULOS_SECOES

PASTA_TEMPLATES = Path(__file__).parent / "templates"
TEMPLATE = "relatorio.html.j2"


@lru_cache
def _ambiente() -> Environment:
    return Environment(
        loader=FileSystemLoader(PASTA_TEMPLATES),
        autoescape=select_autoescape(enabled_extensions=("html", "j2"), default=True),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def renderizar(conteudo: ConteudoRelatorio) -> str:
    """HTML completo; textos são escapados, só figuras e o script do Plotly entram como estão."""
    return _ambiente().get_template(TEMPLATE).render(c=conteudo, titulos=TITULOS_SECOES)
```

`backend/pyproject.toml` — os templates precisam ir junto do pacote numa instalação não editável. Acrescentar depois de `[tool.setuptools.packages.find]`:
```toml
[tool.setuptools.package-data]
"app.dominios.relatorio" = ["templates/*"]
```

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/relatorio/templates app/dominios/relatorio/montagem.py pyproject.toml tests/dominios/relatorio/test_montagem.py
git commit -m "feat(relatorio): adiciona template HTML do mini relatório com estilo de impressão"
```

---

### Tarefa 8: fachada do relatório

**Arquivos:**
- Criar: `backend/app/dominios/relatorio/servico.py`
- Teste: `backend/tests/dominios/relatorio/test_servico.py`

**Passo 1: escrever os testes (falham)** — usam o `pesquisa_saude.txt` com as duplicatas removidas:
```python
import pytest

from app.compartilhado.tipos import TipoVariavel
from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import AcaoLimpeza, ServicoDatasets
from app.dominios.relatorio.servico import PedidoRelatorio, ServicoRelatorio


@pytest.fixture
def servico(servico_datasets: ServicoDatasets) -> ServicoRelatorio:
    return ServicoRelatorio(servico_datasets, ServicoAnalise(servico_datasets))


@pytest.fixture
def dataset_id(servico_datasets: ServicoDatasets) -> str:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.limpar(dataset_id, [AcaoLimpeza("duplicados", "remover")])
    return dataset_id


def test_mini_relatorio_completo(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio())

    assert "Relatório estatístico" in html
    assert "pesquisa_saude.txt · 227 linhas após limpeza × 8 colunas" in html
    assert "1. Leitura do arquivo" in html
    assert "separado por ponto e vírgula, decimal com vírgula" in html
    assert "Removemos 3 linhas duplicadas." in html
    assert 'Análise de <span class="mono">peso_kg</span>' in html
    assert "Figura 1 · " in html
    assert html.count("Plotly.newPlot(") == 7
    assert "cdn.plot.ly/plotly-" in html
    assert "inteligência artificial" not in html.lower()


def test_identificador_fica_fora(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("analises",)))

    assert 'Análise de <span class="mono">id</span>' not in html
    assert "Leitura do arquivo" not in html


def test_colunas_escolhidas_e_offline(servico: ServicoRelatorio, dataset_id: str) -> None:
    html = servico.gerar(
        dataset_id, PedidoRelatorio(secoes=("analises",), colunas=("idade",), offline=True)
    )

    assert html.count("Plotly.newPlot(") == 1
    assert 'src="https://cdn.plot.ly' not in html
    assert "plotly.js v" in html


def test_sem_limpeza_avisa(servico: ServicoRelatorio, servico_datasets: ServicoDatasets) -> None:
    dataset_id = servico_datasets.importar_exemplo().dataset_id
    servico_datasets.alterar_tipo(dataset_id, "idade", TipoVariavel.DISCRETA)

    html = servico.gerar(dataset_id, PedidoRelatorio(secoes=("limpeza", "tipos")))

    assert "Nenhuma ação de limpeza foi aplicada." in html
    assert "Tipo escolhido por você." in html
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar `app/dominios/relatorio/servico.py`**
```python
"""Fachada do domínio relatorio: junta leitura, tipos, limpeza e análises num HTML (spec 13)."""

from dataclasses import dataclass
from datetime import datetime

from app.compartilhado.numeros import formatar_numero, formatar_percentual
from app.compartilhado.tipos import TipoVariavel
from app.core.erros import EntradaInvalida
from app.dominios.analise.servico import Analise, ServicoAnalise
from app.dominios.datasets.servico import Resumo, ServicoDatasets
from app.dominios.graficos.servico import codigo_plotlyjs, endereco_plotlyjs_cdn, figura_html
from app.dominios.relatorio import textos
from app.dominios.relatorio.conteudo import (
    SECOES_M1,
    ConteudoRelatorio,
    DadosLeitura,
    FiguraRelatorio,
    FormulaTexto,
    ItemMedida,
    LinhaTipo,
    Secao,
    SecaoColuna,
)
from app.dominios.relatorio.montagem import renderizar

__all__ = ["SECOES_M1", "PedidoRelatorio", "Secao", "ServicoRelatorio"]

FORMATO_DATA = "%d/%m/%Y %H:%M"
ESCAPE_FECHAMENTO = r"<\/script"
CABECALHOS_PRIMEIRA_COLUNA = {
    TipoVariavel.CONTINUA: "Classe",
    TipoVariavel.DISCRETA: "Valor",
}


@dataclass(frozen=True, slots=True)
class PedidoRelatorio:
    """O que entra no relatório; sem colunas = todas as analisáveis."""

    secoes: tuple[Secao, ...] = SECOES_M1
    colunas: tuple[str, ...] | None = None
    offline: bool = False


def _script_plotly(offline: bool) -> str:
    if offline:
        return f"<script>{codigo_plotlyjs().replace('</script', ESCAPE_FECHAMENTO)}</script>"
    return f'<script src="{endereco_plotlyjs_cdn()}"></script>'


def _leitura(resumo: Resumo) -> str:
    m = resumo.metadados
    dados = DadosLeitura(
        m.formato, m.separador, m.decimal, m.codificacao, m.tem_cabecalho, m.n_linhas, m.n_colunas
    )
    return textos.descrever_leitura(dados)


def _valor(valor: float | str | None, sufixo: str = "") -> str:
    return f"{formatar_numero(valor)}{sufixo}" if isinstance(valor, float) else str(valor)


def _medidas(analise: Analise) -> tuple[ItemMedida, ...]:
    tend, disp = analise.tendencia, analise.dispersao
    candidatas = [("Média", tend.media, ""), ("Mediana", tend.mediana, "")]
    candidatas += [("Moda de Czuber", tend.moda_czuber, ""), ("Proporção", tend.proporcao, "")]
    if disp is not None:
        candidatas += [
            ("Desvio padrão", disp.desvio_padrao, ""),
            ("Variância", disp.variancia, ""),
            ("CV", disp.cv, "%"),
            ("IQR", disp.iqr, ""),
            ("Amplitude", disp.amplitude, ""),
        ]
    itens = [ItemMedida(r, _valor(m.valor, s)) for r, m, s in candidatas if m.aplicavel]
    modas = ", ".join(_valor(v) for v in tend.moda.valores) or "não há (amodal)"
    return (*itens[:2], ItemMedida("Moda", modas), *itens[2:])


def _tabela(analise: Analise) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    tabela = analise.frequencias
    primeira = CABECALHOS_PRIMEIRA_COLUNA.get(analise.tipo, "Categoria")
    cabecalho = (primeira, "fᵢ", "fr%") + (("Fr%",) if tabela.acumulada_aplicavel else ())
    acumular = tabela.acumulada_aplicavel
    linhas = tuple(
        (linha.rotulo, str(linha.fi), formatar_percentual(linha.fr_pct))
        + ((formatar_percentual(linha.fr_acum_pct or 0.0),) if acumular else ())
        for linha in tabela.linhas
    )
    return cabecalho, linhas


def _separatrizes(analise: Analise) -> str | None:
    if analise.separatrizes is None:
        return None
    return " · ".join(f"{q.rotulo} = {_valor(q.valor)}" for q in analise.separatrizes.quartis)


def _figura(analise: Analise, ordem: int) -> FiguraRelatorio | None:
    if not analise.figuras:
        return None
    principal = analise.figuras[0]
    html = figura_html(f"figura-{ordem}", principal.dados)
    return FiguraRelatorio(principal.titulo, principal.resumo, html)


def _secao_coluna(analise: Analise, ordem: int) -> SecaoColuna:
    cabecalho, linhas = _tabela(analise)
    return SecaoColuna(
        coluna=analise.coluna,
        tipo=textos.TIPOS_LEGIVEIS[analise.tipo],
        n=analise.n,
        n_faltantes=analise.n_faltantes,
        cabecalho_tabela=cabecalho,
        linhas_tabela=linhas,
        medidas=_medidas(analise),
        separatrizes=_separatrizes(analise),
        interpretacoes=analise.interpretacoes,
        figura=_figura(analise, ordem),
        formulas=tuple(FormulaTexto(f.nome, f.latex, f.texto) for f in analise.formulas),
    )


class ServicoRelatorio:
    """Mini relatório do M1 (spec 13): leitura, tipos, limpeza e análise por coluna."""

    def __init__(self, datasets: ServicoDatasets, analise: ServicoAnalise) -> None:
        self._datasets = datasets
        self._analise = analise

    def _colunas(self, dataset_id: str, pedido: PedidoRelatorio) -> tuple[SecaoColuna, ...]:
        tipos = self._datasets.colunas(dataset_id)
        nomes = pedido.colunas or tuple(
            t.coluna for t in tipos if t.tipo != TipoVariavel.IDENTIFICADOR
        )
        secoes: list[SecaoColuna] = []
        for nome in nomes:
            try:
                analise = self._analise.analisar(dataset_id, nome)
            except EntradaInvalida:
                continue  # identificador ou coluna vazia: fica fora, como na tela
            secoes.append(_secao_coluna(analise, len(secoes) + 1))
        return tuple(secoes)

    def gerar(self, dataset_id: str, pedido: PedidoRelatorio) -> str:
        """HTML autocontido; `offline` embute o plotly.js (cerca de 4,8 MB)."""
        resumo = self._datasets.resumo(dataset_id)
        secoes = set(pedido.secoes)
        tipos = self._datasets.colunas(dataset_id)
        conteudo = ConteudoRelatorio(
            nome_arquivo=resumo.nome_arquivo,
            gerado_em=datetime.now().strftime(FORMATO_DATA),
            subtitulo=textos.subtitulo(
                resumo.nome_arquivo, resumo.n_linhas, resumo.n_linhas_original, resumo.n_colunas
            ),
            script_plotly=_script_plotly(pedido.offline),
            leitura=_leitura(resumo) if "leitura" in secoes else None,
            tipos=tuple(LinhaTipo(t.coluna, textos.TIPOS_LEGIVEIS[t.tipo], t.motivo) for t in tipos)
            if "tipos" in secoes
            else None,
            limpeza=(tuple(e.frase for e in resumo.log_limpeza) or (textos.SEM_LIMPEZA,))
            if "limpeza" in secoes
            else None,
            colunas=self._colunas(dataset_id, pedido) if "analises" in secoes else None,
        )
        return renderizar(conteudo)
```

> Colunas `identificador` e vazias ficam fora do relatório, como na tela 4. Uma coluna pedida que não existe devolve 404 (`COLUNA_NAO_ENCONTRADA`).

**Passo 4: rodar e ver passar**

**Passo 5: commit**
```bash
git add app/dominios/relatorio/servico.py tests/dominios/relatorio/test_servico.py
git commit -m "feat(relatorio): monta leitura, tipos, limpeza e análise por coluna no relatório"
```

---

### Tarefa 9: rota e registro no `main`

**Arquivos:**
- Criar: `backend/app/dominios/relatorio/router.py`
- Modificar: `backend/app/main.py`
- Teste: `backend/tests/dominios/relatorio/test_router.py`

**Passo 1: escrever os testes (falham)**
```python
from fastapi.testclient import TestClient


def _exemplo(cliente: TestClient) -> str:
    return str(cliente.post("/api/datasets/exemplo").json()["dataset_id"])


def test_relatorio_em_html(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(
        f"/api/datasets/{dataset_id}/relatorio",
        params={"secoes": ["leitura", "analises"], "colunas": ["altura_m", "sexo"]},
    )

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "1. Leitura do arquivo" in resposta.text
    assert "Tipos de variável" not in resposta.text
    assert resposta.text.count("Plotly.newPlot(") == 2


def test_secao_desconhecida(cliente: TestClient) -> None:
    dataset_id = _exemplo(cliente)

    resposta = cliente.get(f"/api/datasets/{dataset_id}/relatorio", params={"secoes": ["gerador"]})

    assert resposta.status_code == 422


def test_dataset_inexistente(cliente: TestClient) -> None:
    assert cliente.get("/api/datasets/nao-existe/relatorio").status_code == 404
```

**Passo 2: rodar e ver falhar**

**Passo 3: implementar**

`app/dominios/relatorio/router.py` — `secoes` e `colunas` como parâmetros repetidos na query (`?secoes=leitura&secoes=tipos`); seção fora das 4 do M1 → 422 (D57):
```python
"""Rota do relatório HTML (spec 13, spec 14). Sem lógica: valida → serviço → HTML."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.dominios.analise.servico import ServicoAnalise
from app.dominios.datasets.servico import ServicoDatasets, obter_servico_datasets
from app.dominios.relatorio.servico import SECOES_M1, PedidoRelatorio, Secao, ServicoRelatorio

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["relatorio"])


def _servico(
    datasets: Annotated[ServicoDatasets, Depends(obter_servico_datasets)],
) -> ServicoRelatorio:
    return ServicoRelatorio(datasets, ServicoAnalise(datasets))


def _pedido(
    secoes: Annotated[list[Secao] | None, Query(description="Seções do mini relatório")] = None,
    colunas: Annotated[list[str] | None, Query(description="Colunas analisadas")] = None,
    offline: Annotated[
        bool, Query(description="Embute o plotly.js (funciona sem internet)")
    ] = False,
) -> PedidoRelatorio:
    return PedidoRelatorio(
        secoes=tuple(secoes) if secoes else SECOES_M1,
        colunas=tuple(colunas) if colunas else None,
        offline=offline,
    )


@router.get("/relatorio", response_class=HTMLResponse, summary="Mini relatório em HTML")
def gerar_relatorio(
    servico: Annotated[ServicoRelatorio, Depends(_servico)],
    dataset_id: str,
    pedido: Annotated[PedidoRelatorio, Depends(_pedido)],
) -> HTMLResponse:
    return HTMLResponse(servico.gerar(dataset_id, pedido))
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
from app.dominios.relatorio import router as relatorio

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
    app.include_router(relatorio.router, prefix=PREFIXO_API)
    return app


app = create_app()
```

**Passo 4: suíte toda**
```bash
ruff check . && ruff format --check . && mypy app && complexipy app --max-complexity-allowed 15 && pytest
```

**Passo 5: commit**
```bash
git add app/dominios/relatorio/router.py app/main.py tests/dominios/relatorio/test_router.py
git commit -m "feat(relatorio): expõe o mini relatório em HTML na API"
```

---

### Tarefa 10: tipos do frontend, decisões, ADR 0003, specs e CHANGELOG

**Passo 1: tipos** — `python scripts/exportar_openapi.py` e, em `frontend/`, `npm run gerar:tipos && npm run lint && npm run build`. Conferir que `Figura` tem `rotulo` e `dados: { [key: string]: unknown }`.

**Passo 2: `docs/decisions.md`**
```
| D56 | DD/10/2026 | Discreta em bastões (spec 08); histograma montado das classes da spec 04; boxplot com estatísticas pré-calculadas (nunca pontos brutos); curva Normal no histograma fica para o M2 | Barras (graficos-plotly.md); `go.Histogram` com dados brutos | Fiel à spec; payload pequeno para qualquer n (ADR 0003) | [0003](adr/0003-figuras-plotly-no-backend.md) |
| D57 | DD/10/2026 | Relatório do M1 aceita só as seções leitura, tipos, limpeza e analises | Aceitar e ignorar as demais | O resto entra nos marcos seguintes; 422 deixa claro | — |
| Dxx | DD/10/2026 | Figuras montadas como dicionários no formato do Plotly e validadas nos testes com `plotly.graph_objects`; `plotly.min.js` lido do pacote | `plotly.graph_objects` no app; override do mypy | O pacote `plotly` não tem tipos e o `mypy --strict` recusaria; sem afrouxar o mypy | [0003](adr/0003-figuras-plotly-no-backend.md) |
```
E, na linha da D54, acrescentar: "Domínios sem estado nem dependências (graficos) expõem funções."

**Passo 3: ADR 0003** — em "Decisão", trocar "monta figuras com `plotly.graph_objects`" por "monta figuras no formato JSON do Plotly (dicionários validados nos testes com `plotly.graph_objects`)", e "embute as mesmas figuras com `plotly.io.to_html`" por "embute as mesmas figuras com `Plotly.newPlot` e o tema claro".

**Passo 4: specs**
- `docs/specs/08-graficos.md`: na matriz, Discreta → "Bastões"; complementares conforme a tabela acima; em "Regras visuais", acrescentar "Boxplot com estatísticas pré-calculadas; discrepantes como pontos (máx. 500)".
- `docs/specs/13-relatorio.md`: em "Mini relatório", acrescentar "parâmetros `secoes` (leitura, tipos, limpeza, analises), `colunas` e `offline`; colunas identificador e vazias ficam fora".
- `docs/specs/14-api.md`: no contrato `Analise`, `figuras` como lista de `{id, rotulo, titulo, resumo, porque, recomendado, dados}`.

**Passo 5: `CHANGELOG.md`** — *Não lançado › Adicionado*:
```
- Gráficos por tipo de variável na análise (barras, bastões, histograma, boxplot, ogiva, acumulada e pizza), com título, resumo e "por que este gráfico".
- Mini relatório HTML (`GET /api/datasets/{id}/relatorio`): leitura, tipos, limpeza e análise por coluna, com gráficos, fórmulas e opção de funcionar sem internet.
```

**Passo 6: commit**
```bash
git add ../frontend/src/shared/api/schema.d.ts ../docs ../CHANGELOG.md
git commit -m "docs: registra D56, D57 e atualiza ADR 0003 e specs 08, 13 e 14"
```

---

### Tarefa 11: verificação final, teste manual e PR

**Passo 1: tudo verde** (backend, frontend e jscpd).

**Passo 2: teste manual pelo preview** — subir `backend`:
1. `POST /api/datasets/exemplo`; `POST .../limpeza` com remover duplicados.
2. `GET .../colunas/peso_kg/analise` → 3 figuras (`Histograma`, `Boxplot`, `Ogiva`), sem `template` no `layout`.
3. `GET .../colunas/cidade/analise` → só `principal` (10 categorias); depois de unificar as grafias continua só `principal` (7 categorias > 5).
4. Abrir `http://localhost:8000/api/datasets/{id}/relatorio` no navegador do preview: seções 1–3, uma seção por coluna com tabela, medidas, "Figura N", fórmulas renderizadas; imprimir (Ctrl+P) e conferir A4 com quebra por coluna.
5. `.../relatorio?offline=true` salvo em arquivo e aberto sem internet → gráficos aparecem; fórmulas ficam em texto.

**Passo 3: resumo e PR** — só com o ok do usuário:
```bash
git push -u origin feat/graficos-relatorio
gh pr create --base develop --title "feat(graficos,relatorio): figuras por tipo e mini relatório HTML (M1.5)" --body "<resumo + specs 08, 13, 14 + checklist do padroes-codigo.md §8>"
```
Sem atribuição de IA. Merge só quando o usuário pedir, com os 3 checks verdes.

---

## Critérios de pronto do M1.5
- [ ] Cada tipo devolve o gráfico principal da spec 08 e os complementares, sem dados brutos
- [ ] Tema do relatório igual ao `tokens.css` (teste)
- [ ] Mini relatório com as 4 seções do M1, offline opcional, impressão em A4, sem seção sobre IA
- [ ] Cobertura ≥ 80%; CI verde; `schema.d.ts` regenerado
