# M2.1 — Forma e distribuições (backend) — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, a spec 09, a spec 16 e os contratos em `docs/plans/2026-10-08-m2-visao-geral.md`.

**Objetivo:** para cada coluna numérica (e binária), calcular assimetria (G₁, As₁, As₂), curtose (G₂, K), ajustar Normal, Binomial ou Bernoulli com teste de aderência e frase de decisão, montar as figuras da forma (histograma + curva Normal, QQ-plot, bastões + curva, observado × esperado) e devolver tudo em `Analise.forma` no mesmo `GET /analise`, com `?tentativas=`.

**Arquitetura:** dois módulos puros no domínio `analise` — `forma.py` (momentos e coeficientes) e `distribuicoes.py` (ajustes e testes) — mais `pontos_forma.py` (curva, quantis do QQ-plot e comparação binomial, que alimentam as figuras). O montador `univariada.analisar_amostra` chama `forma_da_amostra(...)`. As figuras ficam no domínio `graficos` (`figuras_forma.py` + `figuras_forma(...)` na fábrica), chamadas pela fachada `ServicoAnalise`, como no M1.5. Textos em `textos_forma.py`. Utilitários sem regra de negócio em `compartilhado/` (`estatistica.py`, `formatar_p_valor`, `p_valor_em_palavras`).

**Stack:** Python 3.12, pandas 3, numpy, **scipy 1.18** (`scipy.stats`: `skew`, `kurtosis`, `shapiro`, `normaltest`, `norm`, `binom`, `chi2`), `scipy-stubs` (D93), FastAPI, Pydantic 2, pytest.

**Branch:** `feat/analise-forma` (sai de `develop`) → PR para `develop`. **Depende de:** nada. **Prazo sugerido:** 15/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | `scipy-stubs` e utilitários compartilhados | `pyproject.toml`, `compartilhado/estatistica.py`, `numeros.py`, `textos.py` |
| 2 | Value objects, fórmulas e textos da forma | `analise/resultados.py`, `formulas.py`, `textos_forma.py` |
| 3 | Assimetria e curtose | `analise/forma.py` |
| 4 | Ajuste Normal | `analise/distribuicoes.py` |
| 5 | Ajustes Binomial e Bernoulli | `analise/distribuicoes.py`, `analise/erros.py` |
| 6 | Pontos para as figuras (curva, QQ, binomial) | `analise/pontos_forma.py` |
| 7 | Montagem da forma na análise univariada | `analise/forma.py` (`forma_da_amostra`), `univariada.py` |
| 8 | Figuras da forma | `graficos/entradas.py`, `figuras_forma.py`, `fabrica.py`, `textos.py`, `servico.py` |
| 9 | Fachada, schemas e router | `analise/servico.py`, `schemas.py`, `router.py` |
| 10 | Tipos do frontend, specs, decisões e CHANGELOG | `schema.d.ts`, `docs/**`, `CHANGELOG.md` |
| 11 | Verificação final, conferência no Swagger, resumo e PR | — |

### Regras que o código implementa
- **Aplicabilidade por tipo** (tabela da visão geral). Nominal e ordinal: `forma = None` e item `forma` em `nao_aplicavel` com "Forma e distribuição não se aplica a qualitativas nominais: Distribuições Normal/Binomial exigem números." (o motivo da spec 09 dentro do molde da spec 16).
- **Mínimos** (spec 09): assimetria n ≥ 3, curtose n ≥ 4; desvio zero → "não há variação para medir a forma". Casos de borda nunca são erro: `Medida(aplicavel=False, motivo=…)`.
- **G₁** = `scipy.stats.skew(bias=False)`; **G₂** = `scipy.stats.kurtosis(fisher=True, bias=False)`; **As₁** = (x̄ − Mo)/s (Mo: Czuber na contínua; moda bruta na discreta, só se unimodal — D98); **As₂** = 3(x̄ − Md)/s; **K** = (Q3 − Q1)/[2(P90 − P10)] (as separatrizes já calculadas; P90 = P10 → não se aplica).
- **Classificação** (spec 09): |G₁| < 0,5 simétrica · 0,5–1 moderada · > 1 forte; sentido pelo sinal. |G₂| ≤ 0,5 mesocúrtica · G₂ > 0,5 leptocúrtica · G₂ < −0,5 platicúrtica.
- **Normal** (D97): n ≤ 5.000 → Shapiro-Wilk; n > 5.000 → D'Agostino-Pearson K² (`normaltest`). Complementar: qui-quadrado nas classes da tabela da spec 04 (primeira e última classes abertas até ±∞), agrupando vizinhas com esperado < 5, gl = k − 3; gl < 1 → `complementar = None`. Discreta só com n ≥ 30.
- **Binomial** (D96): valores inteiros ≥ 0; `tentativas` = máximo observado por padrão; `tentativas` < máximo → `TENTATIVAS_INVALIDAS`; todos zero → não se aplica. p̂ = x̄/n; esperados Eₖ = N·C(n,k)p̂ᵏ(1−p̂)ⁿ⁻ᵏ para k = 0..n; caudas agrupadas até esperado ≥ 5; gl = k − 2.
- **Bernoulli** (D95): parâmetros p̂ (a proporção da spec 05), E[X] = p, Var = p(1 − p); `teste = None`; frase "Com p estimado dos próprios dados, a Bernoulli repete as proporções observadas; não há teste de aderência."
- **Decisão** (α = 0,05): p ≥ α → "Os dados são compatíveis com a distribuição {Normal|Binomial}."; p < α → "Os dados se afastam da distribuição {d}.". `calculo`: "Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05".
- **Frase conjunta** (spec 09): "Distribuição aproximadamente simétrica e mesocúrtica; compatível com a Normal (p = 0,399)." Usa o ajuste Normal se aplicável; senão o Binomial; sem ajuste, só a primeira parte.
- **Figuras** (D94): ficam em `Forma.figuras`; QQ-plot com no máximo 500 pontos (D98); curva com 200 pontos, escalada para frequência (densidade × N × h na contínua; × N × 1 na discreta).

---

### Tarefa 1: `scipy-stubs` e utilitários compartilhados

**Arquivos:**
- Modificar: `backend/pyproject.toml` (grupo `dev`: `"scipy-stubs>=1.18,<1.19"`), `app/compartilhado/numeros.py`, `app/compartilhado/textos.py`
- Criar: `app/compartilhado/estatistica.py`, `tests/compartilhado/test_estatistica.py`
- Modificar: `tests/compartilhado/test_numeros.py`, `tests/compartilhado/test_textos.py`

**Passo 1: instalar** — `.venv/Scripts/python -m pip install -e ".[dev]"` e conferir que `mypy app` continua verde.

**Passo 2: testes (falham)**
```python
# tests/compartilhado/test_numeros.py
@pytest.mark.parametrize(
    ("p", "esperado"),
    [(0.0004, "p < 0,001"), (0.001, "p = 0,001"), (0.2134, "p = 0,213"), (0.05, "p = 0,05")],
)
def test_formatar_p_valor(p: float, esperado: str) -> None:
    assert formatar_p_valor(p) == esperado


# tests/compartilhado/test_textos.py
@pytest.mark.parametrize(
    ("p", "esperado"),
    [(0.0004, "menos de 1 em 1.000"), (0.02, "cerca de 1 em 50"), (0.21, "cerca de 1 em 5"),
     (0.7, "mais de 1 em 2")],
)
def test_p_valor_em_palavras(p: float, esperado: str) -> None:
    assert p_valor_em_palavras(p) == esperado


# tests/compartilhado/test_estatistica.py
def test_agrupar_junta_as_caudas_com_esperado_pequeno() -> None:
    observados, esperados = agrupar_esperados_pequenos([1, 3, 10, 12, 4, 1], [0.5, 2.5, 11, 11, 4, 2])
    assert observados == [14, 12, 5]
    assert esperados == pytest.approx([14.0, 11.0, 6.0])


def test_agrupar_sem_grupos_pequenos_nao_muda() -> None:
    assert agrupar_esperados_pequenos([6, 7], [6.5, 6.5]) == ([6, 7], [6.5, 6.5])
```

**Passo 3: implementar**
- `formatar_p_valor(p: float) -> str` — `"p < 0,001"` se p < 0,001; senão `f"p = {formatar_numero(p, 3)}"`.
- `p_valor_em_palavras(p: float) -> str` — limiar `P_MUITO_PEQUENO = 0.001`, `METADE = 0.5`; senão `f"cerca de 1 em {formatar_inteiro(round(1 / p))}"`. `textos.py` passa a importar `numeros` (os dois são de `compartilhado/`).
- `compartilhado/estatistica.py`:
  ```python
  """Utilitários estatísticos sem regra de negócio, usados por mais de um domínio (padroes §2)."""

  ALFA = 0.05  # nível de significância padrão (00-visao-geral.md)
  MINIMO_ESPERADO = 5.0


  def agrupar_esperados_pequenos(
      observados: Sequence[float], esperados: Sequence[float], minimo: float = MINIMO_ESPERADO
  ) -> tuple[list[float], list[float]]:
      """Junta grupos vizinhos das pontas para o meio até cada esperado ser ≥ mínimo (χ²)."""
  ```
  Algoritmo: acumular da esquerda até o esperado acumulado ≥ mínimo, depois o mesmo da direita; o meio fica como está; se sobrar um grupo do meio com esperado < mínimo, junta ao vizinho menor. Laço extraído em `_acumular_ponta(...)` (aninhamento ≤ 3).

**Passo 4:** `pytest tests/compartilhado --no-cov` verde; `ruff`, `mypy`.

**Commit:** `chore(backend): adiciona scipy-stubs e utilitários de p-valor e qui-quadrado`

---

### Tarefa 2: value objects, fórmulas e textos da forma

**Arquivos:**
- Modificar: `app/dominios/analise/resultados.py` (+ `Parametro`, `TesteAderencia`, `Ajuste`, `Forma`; `Analise.forma: Forma | None = None`), `formulas.py`
- Criar: `app/dominios/analise/textos_forma.py`, `tests/dominios/analise/test_textos_forma.py`

**Value objects** (`resultados.py`, campos exatamente como no contrato da visão geral):
```python
type Distribuicao = Literal["normal", "binomial", "bernoulli"]
type ClasseAssimetria = Literal["simetrica", "moderada", "forte"]
type Sentido = Literal["direita", "esquerda"]
type ClasseCurtose = Literal["mesocurtica", "leptocurtica", "platicurtica"]


@dataclass(frozen=True, slots=True)
class Parametro:
    simbolo: str
    nome: str
    valor: float


@dataclass(frozen=True, slots=True)
class TesteAderencia:
    nome: str
    estatistica: float
    gl: int | None
    p_valor: float
    compativel: bool


@dataclass(frozen=True, slots=True)
class Ajuste:
    distribuicao: Distribuicao
    aplicavel: bool = True
    motivo: str | None = None
    parametros: tuple[Parametro, ...] = ()
    teste: TesteAderencia | None = None
    complementar: TesteAderencia | None = None
    frase: str | None = None
    calculo: str | None = None
    formula: str | None = None


def ajuste_nao_aplicavel(distribuicao: Distribuicao, motivo: str) -> Ajuste:
    return Ajuste(distribuicao, aplicavel=False, motivo=motivo)


@dataclass(frozen=True, slots=True)
class Forma:
    assimetria: Medida
    assimetria_pearson_1: Medida
    assimetria_pearson_2: Medida
    curtose: Medida
    curtose_percentilica: Medida
    normal: Ajuste
    binomial: Ajuste
    classificacao_assimetria: ClasseAssimetria | None = None
    sentido_assimetria: Sentido | None = None
    classificacao_curtose: ClasseCurtose | None = None
    tentativas: int | None = None
    interpretacao: str | None = None
    figuras: tuple[Figura, ...] = ()
```
`resultados.py` fica com ~250 linhas (limite 500).

**Fórmulas** (`formulas.py`, chaves novas; texto Unicode igual ao da spec 09):
| chave | nome | texto |
|---|---|---|
| `assimetria` | Assimetria (Fisher) | G₁ = [√(n(n−1)) / (n−2)] · m₃ / m₂^(3/2) |
| `assimetria_pearson_1` | 1º coeficiente de Pearson | As₁ = (x̄ − Mo) / s |
| `assimetria_pearson_2` | 2º coeficiente de Pearson | As₂ = 3(x̄ − Md) / s |
| `curtose` | Curtose (excesso) | G₂ = curtose amostral − 3 (Normal = 0) |
| `curtose_percentilica` | Curtose percentílica | K = (Q3 − Q1) / [2(P90 − P10)] (Normal ≈ 0,263) |
| `normal` | Distribuição Normal | f(x) = (1 / (σ√(2π))) · e^(−(x−μ)² / (2σ²)) |
| `binomial` | Distribuição Binomial | P(X = k) = C(n,k) · pᵏ · (1−p)ⁿ⁻ᵏ |
| `bernoulli` | Distribuição de Bernoulli | P(X = 1) = p · E[X] = p · Var = p(1 − p) |
| `qui_quadrado` | Qui-quadrado de aderência | χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ |

(LaTeX correspondente em cada `_f(...)`; G₂ em LaTeX: `G_2 = \frac{(n+1)n(n-1)}{(n-2)(n-3)} \cdot \frac{\sum (x_i-\bar{x})^4}{(\sum (x_i-\bar{x})^2)^2} - \frac{3(n-1)^2}{(n-2)(n-3)}`.)

**Textos** (`textos_forma.py`): `MOTIVOS_FORMA` (`forma_categorica`, `poucos_3`, `poucos_4`, `sem_variacao`, `percentis_iguais`, `binomial_continua`, `binomial_nao_contagem`, `binomial_zeros`, `normal_poucos`, `normal_discreta_30`, `normal_binaria`, `moda_multipla`), `NOMES_FORMA`, `frase_assimetria(classe, sentido)`, `frase_curtose(classe)`, `frase_aderencia(nome_distribuicao, compativel)`, `calculo_teste(teste)`, `frase_conjunta(forma_parcial)`. Usa `textos.TIPO_LEGIVEL` e o molde `"{nome} não se aplica a {tipo}: {motivo}."`.

Frases (spec 16, ≤ 25 palavras):
- simétrica: "Aproximadamente simétrica: a cauda {direita|esquerda} é só um pouco mais longa." (G₁ = 0 → "Simétrica: as duas caudas têm o mesmo tamanho.")
- moderada: "Assimetria moderada à direita: há valores altos mais afastados do centro." / "… à esquerda: há valores baixos …"
- forte: "Assimetria forte à direita: poucos valores muito altos esticam a cauda." / "… à esquerda: poucos valores muito baixos …"
- mesocúrtica: "Mesocúrtica: caudas parecidas com as da Normal."
- leptocúrtica: "Leptocúrtica: pico mais alto e caudas mais pesadas que a Normal (mais valores extremos)."
- platicúrtica: "Platicúrtica: mais achatada que a Normal, com poucos valores extremos."
- Binomial em contínua (print 4e): "Binomial não se aplica a contínuas: precisa de contagens de sucessos em n tentativas."

**Testes** (`test_textos_forma.py`, parametrizados): cada classe × sentido gera a frase esperada; `frase_aderencia("Normal", True)` = "Os dados são compatíveis com a distribuição Normal."; `calculo_teste(TesteAderencia("Shapiro-Wilk", 0.99329, None, 0.399, True))` = "Shapiro-Wilk: W = 0,9933 · p = 0,399 ≥ 0,05"; com gl: "Qui-quadrado: χ² = 3,2 · gl = 4 · p = 0,525 ≥ 0,05"; `p < 0,001` vira "p < 0,001 < 0,05".

**Commit:** `feat(analise): value objects, fórmulas e textos da forma (spec 09)`

---

### Tarefa 3: assimetria e curtose (`forma.py`)

**Arquivos:** criar `app/dominios/analise/forma.py`, `tests/dominios/analise/test_forma.py`

**Testes (falham)** — amostra de livro `[2, 4, 4, 4, 5, 5, 7, 9]` (x̄ = 5, s = 2,1381, Md = 4,5, Mo = 4; valores conferidos com scipy 1.18):
```python
LIVRO = [2, 4, 4, 4, 5, 5, 7, 9]


def test_assimetria_de_fisher_amostral(criar_amostra: CriarAmostra) -> None:
    medida = assimetria(valores(LIVRO))
    assert medida.valor == pytest.approx(0.818488, rel=1e-5)
    assert medida.formula == "assimetria"


def test_classifica_assimetria_moderada_a_direita() -> None:
    assert classificar_assimetria(0.818) == ("moderada", "direita")
    assert classificar_assimetria(-0.3) == ("simetrica", "esquerda")
    assert classificar_assimetria(1.4) == ("forte", "direita")


def test_curtose_em_excesso() -> None:
    medida = curtose(valores(LIVRO))
    assert medida.valor == pytest.approx(0.940625, rel=1e-5)


@pytest.mark.parametrize(("g2", "classe"), [(0.94, "leptocurtica"), (-0.18, "mesocurtica"), (-0.9, "platicurtica")])
def test_classifica_curtose(g2: float, classe: str) -> None:
    assert classificar_curtose(g2) == classe


def test_coeficientes_de_pearson() -> None:
    as1, as2 = pearson(valores(LIVRO), moda=4.0, mediana=4.5)
    assert as1.valor == pytest.approx(0.467707, rel=1e-5)
    assert as2.valor == pytest.approx(0.701561, rel=1e-5)


def test_curtose_percentilica_usa_quartis_e_decis(criar_amostra: CriarAmostra) -> None:
    seps = separatrizes(criar_amostra(TipoVariavel.DISCRETA, LIVRO))
    assert curtose_percentilica(seps).valor == pytest.approx(0.178571, rel=1e-5)  # (5,5 − 4) / (2 · (7,6 − 3,4))


def test_poucos_valores_nao_se_aplica() -> None:
    assert not assimetria(valores([1, 2])).aplicavel
    assert not curtose(valores([1, 2, 3])).aplicavel


def test_valores_iguais_nao_tem_forma() -> None:
    medida = assimetria(valores([3, 3, 3, 3]))
    assert not medida.aplicavel
    assert "não há variação" in (medida.motivo or "")


def test_pearson_sem_moda_unica_nao_se_aplica() -> None:
    as1, _ = pearson(valores([1, 1, 2, 2, 3]), moda=None, mediana=2.0)
    assert not as1.aplicavel
```
(`valores(lista)` = helper local que devolve `np.ndarray` float64.)

**Implementar** — funções puras sobre `np.ndarray`:
- `assimetria(valores) -> Medida`, `curtose(valores) -> Medida` (guardas de n e de variação em `_motivo_minimo(valores, minimo)`), `classificar_assimetria(g1) -> tuple[ClasseAssimetria, Sentido | None]`, `classificar_curtose(g2) -> ClasseCurtose`, `pearson(valores, moda: float | None, mediana: float) -> tuple[Medida, Medida]`, `curtose_percentilica(seps: Separatrizes) -> Medida` (Q1/Q3 de `quartis`, P10/P90 de `decis[0]`/`decis[8]`).
- `calculo` de cada medida com os números: "G₁ = 0,8185 (n = 8)"; "As₁ = (5 − 4) / 2,138 = 0,4677"; "K = (5,5 − 4) / [2 · (7,6 − 3,4)] = 0,1786".
- Interpretação da medida = frase de `textos_forma` (para o card).
- Constantes: `LIMIAR_SIMETRIA = 0.5`, `LIMIAR_FORTE = 1.0`, `LIMIAR_CURTOSE = 0.5`, `MIN_ASSIMETRIA = 3`, `MIN_CURTOSE = 4`.

**Commit:** `feat(analise): assimetria (Fisher e Pearson) e curtose (excesso e percentílica)`

---

### Tarefa 4: ajuste Normal (`distribuicoes.py`)

**Arquivos:** criar `app/dominios/analise/distribuicoes.py`, `tests/dominios/analise/test_distribuicoes.py`

**Testes (falham)** — amostras com `np.random.default_rng(42)` (spec 17: Normal aderente, Exponencial não):
```python
def test_amostra_normal_e_compativel() -> None:
    dados = np.random.default_rng(42).normal(70, 11, 227)
    ajuste = ajuste_normal(dados, classes=None)
    assert ajuste.aplicavel and ajuste.teste is not None
    assert ajuste.teste.nome == "Shapiro-Wilk"
    assert ajuste.teste.p_valor == pytest.approx(0.39896, rel=1e-3)
    assert ajuste.teste.compativel
    assert ajuste.frase == "Os dados são compatíveis com a distribuição Normal."
    assert [p.simbolo for p in ajuste.parametros] == ["μ̂", "σ̂"]


def test_amostra_exponencial_se_afasta() -> None:
    rng = np.random.default_rng(42)
    rng.normal(70, 11, 227)  # mesma sequência do script de referência
    ajuste = ajuste_normal(rng.exponential(10, 227), classes=None)
    assert ajuste.teste is not None and not ajuste.teste.compativel
    assert ajuste.teste.p_valor < 1e-10


def test_mais_de_5000_valores_usa_dagostino() -> None:
    dados = np.random.default_rng(7).normal(0, 1, 6000)
    assert ajuste_normal(dados, classes=None).teste.nome == "D'Agostino-Pearson K²"


def test_qui_quadrado_complementar_nas_classes(criar_amostra: CriarAmostra) -> None:
    dados = np.random.default_rng(42).normal(70, 11, 227)
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, dados.tolist()), None)
    complementar = ajuste_normal(dados, classes=tabela).complementar
    assert complementar is not None and complementar.nome == "Qui-quadrado"
    assert complementar.gl is not None and 1 <= complementar.gl <= tabela.k - 3  # grupos ≤ classes
    assert 0 <= complementar.p_valor <= 1


def test_poucas_classes_ficam_sem_complementar(criar_amostra: CriarAmostra) -> None:
    dados = np.array([1.0, 2.0, 2.5, 3.0, 4.0])
    tabela = tabela_frequencia(criar_amostra(TipoVariavel.CONTINUA, dados.tolist()), 3)
    assert ajuste_normal(dados, classes=tabela).complementar is None  # gl = k − 3 < 1


@pytest.mark.parametrize("dados", [[1.0, 2.0], [5.0, 5.0, 5.0, 5.0]])
def test_normal_nao_se_aplica_em_borda(dados: list[float]) -> None:
    assert not ajuste_normal(np.array(dados), classes=None).aplicavel
```

**Implementar**
```python
def ajuste_normal(valores: np.ndarray, classes: TabelaFrequencia | None) -> Ajuste:
    """Normal com μ̂ = x̄ e σ̂ = s; Shapiro-Wilk (n ≤ 5.000) ou D'Agostino-Pearson (n > 5.000)."""
```
- `_teste_normalidade(valores) -> TesteAderencia` por tabela de despacho de faixa de n (`LIMITE_SHAPIRO = 5000`).
- `_qui_quadrado_normal(valores, tabela) -> TesteAderencia | None`: esperados por classe com `stats.norm.cdf`, primeira/última abertas; `agrupar_esperados_pequenos`; `stats.chi2.sf(chi2, gl)`.
- `_decidir(nome, estatistica, gl, p) -> TesteAderencia` (compativel = p ≥ `ALFA`).
- Converter tudo para `float` nativo (nada de `np.float64` saindo do domínio).

**Commit:** `feat(analise): ajuste Normal com Shapiro-Wilk/D'Agostino e qui-quadrado complementar`

---

### Tarefa 5: ajustes Binomial e Bernoulli

**Arquivos:** modificar `distribuicoes.py`, `analise/erros.py`, `tests/dominios/analise/test_distribuicoes.py`

**Testes (falham)**
```python
BINOMIAL = np.random.default_rng(42).binomial(10, 0.3, 300).astype("float64")  # máx. observado = 8


def test_binomial_com_tentativas_informadas_e_compativel() -> None:
    ajuste = ajuste_binomial(BINOMIAL, tentativas=10)
    assert ajuste.aplicavel and ajuste.teste is not None
    assert ajuste.teste.nome == "Qui-quadrado"
    assert ajuste.teste.compativel
    p = next(p for p in ajuste.parametros if p.simbolo == "p̂")
    assert p.valor == pytest.approx(0.299)


def test_binomial_sem_tentativas_usa_o_maximo() -> None:
    ajuste = ajuste_binomial(BINOMIAL, tentativas=None)
    n = next(p for p in ajuste.parametros if p.simbolo == "n")
    assert n.valor == 8


def test_tentativas_menor_que_o_maximo_e_erro() -> None:
    with pytest.raises(EntradaInvalida) as erro:
        ajuste_binomial(BINOMIAL, tentativas=5)
    assert erro.value.codigo == "TENTATIVAS_INVALIDAS"


@pytest.mark.parametrize("dados", [[1.5, 2.0, 3.0], [-1.0, 2.0, 3.0], [0.0, 0.0, 0.0]])
def test_binomial_exige_contagens(dados: list[float]) -> None:
    assert not ajuste_binomial(np.array(dados), tentativas=None).aplicavel


def test_binomial_com_poucos_grupos_fica_sem_teste() -> None:
    ajuste = ajuste_binomial(np.array([0.0, 1.0, 1.0, 0.0, 1.0]), tentativas=None)
    assert ajuste.aplicavel and ajuste.teste is None and ajuste.frase is not None  # gl < 1


def test_bernoulli_tem_parametros_e_nao_tem_teste() -> None:
    ajuste = ajuste_bernoulli(0.3)
    assert ajuste.distribuicao == "bernoulli" and ajuste.teste is None
    assert [round(p.valor, 4) for p in ajuste.parametros] == [0.3, 0.3, 0.21]
```

**Implementar**
- `ajuste_binomial(valores, tentativas: int | None) -> Ajuste` — guardas (`_eh_contagem`, todos zero), `n = tentativas or int(max)`, `p̂ = x̄ / n`, `esperados = N · stats.binom.pmf(k, n, p̂)` para k = 0..n, observados com `np.bincount(minlength=n+1)`, agrupamento, gl = k − 2. `parametros`: n, p̂, E[X] = np̂, Var = np̂(1 − p̂).
- `erros.tentativas_invalidas(maximo: int) -> EntradaInvalida` ("O número de tentativas precisa ser pelo menos o maior valor observado ({max})." / "Use um número igual ou maior que {max}.").
- `ajuste_bernoulli(p: float) -> Ajuste`.
- `distribuicoes.py` deve ficar < 300 linhas; se passar, separar `aderencia.py` (testes e agrupamento) de `distribuicoes.py` (ajustes).

**Commit:** `feat(analise): ajuste Binomial com qui-quadrado e Bernoulli para binárias`

---

### Tarefa 6: pontos para as figuras (`pontos_forma.py`)

**Arquivos:** criar `app/dominios/analise/pontos_forma.py`, `tests/dominios/analise/test_pontos_forma.py`

Dataclasses de saída (domínio `analise`; a fachada converte para as entradas de `graficos` na Tarefa 9):
```python
@dataclass(frozen=True, slots=True)
class Curva:
    x: tuple[float, ...]
    y: tuple[float, ...]
    media: float
    desvio: float


@dataclass(frozen=True, slots=True)
class PontosQQ:
    teoricos: tuple[float, ...]   # quantis da Normal padrão
    observados: tuple[float, ...]  # quantis da amostra
    media: float
    desvio: float                  # reta de referência y = μ + σ·z


@dataclass(frozen=True, slots=True)
class ComparacaoBinomial:
    k: tuple[int, ...]
    observados: tuple[int, ...]
    esperados: tuple[float, ...]
```
- `curva_normal(media, desvio, inicio, fim, escala, pontos=200) -> Curva` (`escala` = N·h na contínua, N na discreta).
- `pontos_qq(valores, maximo=500) -> PontosQQ`: probabilidades (i − 0,5)/m com m = min(n, 500); `stats.norm.ppf`; quantis observados com `np.quantile(method="linear")` quando n > 500, ordenados quando n ≤ 500.
- `comparacao_binomial(valores, n, p) -> ComparacaoBinomial` (sem agrupar: o gráfico mostra todos os k).

**Testes:** área da curva ≈ escala (soma trapezoidal, tolerância 2%, intervalo ±4σ); `pontos_qq` com 6.000 valores devolve 500 pontos crescentes; com 10 valores devolve 10 e `observados` = valores ordenados; `comparacao_binomial` soma dos esperados ≈ N.

**Commit:** `feat(analise): pontos da curva Normal, do QQ-plot e da comparação Binomial`

---

### Tarefa 7: montagem da forma na análise univariada

**Arquivos:** modificar `forma.py` (+ `forma_da_amostra`), `univariada.py`, `tests/dominios/analise/test_forma.py`, `test_univariada.py`

```python
def forma_da_amostra(
    amostra: Amostra, contexto: ContextoForma, tentativas: int | None
) -> Forma | None:
    """Forma por tipo (tabela de despacho): numéricas, binária; nominal e ordinal → None."""
```
`ContextoForma` (dataclass) junta `tabela`, `tendencia` e `separatrizes` (evita 6 parâmetros). Despacho `FORMAS: dict[TipoVariavel, Callable[...]]` com `_continua`, `_discreta`, `_binaria`. `_discreta` aplica a Normal só com n ≥ 30 (`MIN_NORMAL_DISCRETA = 30`). A frase conjunta vem de `textos_forma.frase_conjunta`.

`univariada.analisar_amostra(amostra, classes=None, sucesso=None, tentativas=None)`:
- `forma = forma_da_amostra(...)`;
- `aplicavel` ganha `forma`, `assimetria`, `curtose`, `normal`, `binomial`;
- `nao_aplicavel` ganha `forma` (categóricas) e os itens não aplicáveis da forma (`assimetria`, `curtose`, `normal`, `binomial`, …), sem repetir;
- `formulas` ganha as chaves das medidas e ajustes aplicáveis (e `qui_quadrado` quando houver teste ou complementar de qui-quadrado).

**Testes:** contínua → `forma` com `normal.aplicavel` e `binomial.motivo` = texto do print 4e; discreta com 40 contagens → Normal e Binomial aplicáveis; discreta com 10 valores → Normal não aplicável com "precisa de pelo menos 30 valores"; binária → Bernoulli e assimetria não aplicável; nominal → `forma is None`, `aplicavel["forma"] is False` e motivo da spec 09; `formulas` da contínua contém `assimetria`, `curtose`, `normal`.

**Commit:** `feat(analise): forma e distribuição na análise univariada`

---

### Tarefa 8: figuras da forma (domínio `graficos`)

**Arquivos:**
- Modificar: `graficos/entradas.py` (+ `CurvaFigura`, `QQFigura`, `BinomialFigura`, `DadosForma`), `fabrica.py` (+ `figuras_forma`), `textos.py` (rótulos, títulos, "por quê", resumos), `servico.py` (exporta)
- Criar: `graficos/figuras_forma.py`, `tests/dominios/graficos/test_figuras_forma.py`

Figuras (dicionários no formato Plotly, D77; traços com `meta` e `name`; `showlegend: true`, legenda horizontal do tema):
| id | rótulo | Traços | Título |
|---|---|---|---|
| `histograma_normal` | Histograma + Normal | barras das classes (`principal`, "Frequência observada") + linha (`referencia`, "Curva Normal (μ = 70,3; σ = 11,2)") | "Histograma de {col} com curva Normal (n = 227)" |
| `qqplot` | QQ-plot | pontos (`principal`, "Valores de {col}", tamanho 6, opacidade 0,7) + reta y = μ + σz (`referencia`, "Referência Normal") | "QQ-plot de {col} contra a Normal" |
| `bastoes_normal` | Bastões + Normal | hastes + pontos (`principal`) + linha (`referencia`) | "Distribuição de {col} com curva Normal (n = …)" |
| `binomial` | Observado × Binomial | barras observado (`principal`) + barras esperado (`referencia`, opacidade 0,55, `barmode: "group"`) | "{col}: observado × Binomial (n = 10; p = 0,299)" |

Resumos (texto ao lado, spec 08): histograma — "As barras acompanham a curva." / "As barras se afastam da curva em alguns trechos." pela decisão do ajuste; QQ — "Os pontos ficam perto da reta: os dados se comportam como uma Normal." / "Os pontos se afastam da reta nas pontas: as caudas fogem da Normal."; binomial — "As barras observadas acompanham as esperadas." / "Há diferenças entre o observado e o esperado.".

`figuras_forma(dados: DadosForma) -> tuple[FiguraPronta, ...]` monta só as figuras cujos dados vieram (curva, qq, binomial podem ser `None`).

**Testes** (validados com `plotly.graph_objects`, como em `test_figuras.py`): cada figura tem os ids/papéis esperados, `showlegend` verdadeiro, sem `template`; QQ com 500 pontos; `figuras_forma` de uma contínua devolve `("histograma_normal", "qqplot")`; de discreta com binomial e sem Normal, só `("binomial",)`.

**Commit:** `feat(graficos): histograma com curva Normal, QQ-plot e observado × Binomial`

---

### Tarefa 9: fachada, schemas e router

**Arquivos:** modificar `analise/servico.py`, `schemas.py`, `router.py`; testes `test_servico.py`, `test_router.py`

- `ServicoAnalise.analisar(dataset_id, coluna, classes=None, sucesso=None, tentativas=None)`: `analise = analisar_amostra(...)`; se `analise.forma` existe, `_figuras_forma(amostra, analise)` converte `Curva`/`PontosQQ`/`ComparacaoBinomial` em `DadosForma` e grava com `replace(forma, figuras=…)`. (Os pontos são calculados por `pontos_da_forma(amostra, analise)` em `pontos_forma.py`; a fachada só converte `Curva`/`PontosQQ`/`ComparacaoBinomial` nas entradas de `graficos`, como já faz com `_barras`. A conversão fica no `servico.py` porque módulo de domínio não importa outro domínio — `padroes-codigo.md` §2, conferido pelo verificador de arquitetura.)
- `schemas.py`: `Parametro`, `TesteAderencia`, `Ajuste`, `Forma` (Pydantic, `from_attributes`) e `Analise.forma: Forma | None`.
- `router.py`: `tentativas: Annotated[int | None, Query(ge=1, le=MAX_TENTATIVAS)] = None` (`MAX_TENTATIVAS = 10_000`).
- **Testes de serviço** com `pesquisa_saude.txt`: `peso_kg` → `forma.normal.teste.nome == "Shapiro-Wilk"`, figuras `histograma_normal` e `qqplot`; `cidade` → `forma is None`; `sexo` → Bernoulli.
- **Testes de API:** `GET …/peso_kg/analise` traz `forma.normal.frase`; `GET …/faltas/analise?tentativas=2` (com `notas_turma.csv`, máximo > 2) → 400 `TENTATIVAS_INVALIDAS`; `tentativas=0` → 422.

**Commit:** `feat(analise): forma no GET /analise com ?tentativas=`

---

### Tarefa 10: tipos do frontend, specs, decisões e CHANGELOG

- `python scripts/exportar_openapi.py` → `npm run gerar:tipos` → commit de `frontend/src/shared/api/schema.d.ts` (o frontend compila igual: os campos novos são só acrescentados).
- `docs/specs/09-distribuicoes-forma.md`: D95 (Bernoulli sem teste), D96 (Binomial só com contagens, tentativas), D97 (complementar gl = k − 3), D98 (As₁ e QQ-plot); seção "Saída" com o contrato `Forma`.
- `docs/specs/14-api.md`: `?tentativas=` no `GET /analise`, `forma` no contrato `Analise`, erro `TENTATIVAS_INVALIDAS`.
- `docs/specs/08-graficos.md`: linha "Contínua" aponta a curva Normal e o QQ-plot para a aba Forma (D94).
- `docs/decisions.md`: D93–D98 (próximos números livres). `CHANGELOG.md` › Não lançado › Adicionado: "Forma e distribuição de cada coluna numérica na API: assimetria, curtose, ajuste Normal/Binomial com teste de aderência e gráficos (histograma com curva Normal, QQ-plot, observado × esperado)."

**Commit:** `docs: forma e distribuições (spec 09, API, decisões D93–D98)`

---

### Tarefa 11: verificação final, conferência e PR

1. Verificação completa (backend, frontend, jscpd).
2. Preview `backend`: abrir `/docs` e conferir `GET /analise` de `peso_kg`, `idade`, `sexo`, `cidade` (exemplo) e `faltas` com e sem `?tentativas=` (`notas_turma.csv`); conferir que as figuras abrem no Plotly (colar o JSON numa página de teste não é necessário: os testes já validam com `graph_objects`).
3. Resumo ao usuário (o que entrou, números do exemplo, decisões) **antes do push**; com o ok, push e PR para `develop` com a spec citada e o checklist do §8. Pedir ao usuário para avisar quando os 3 checks passarem.

## Critérios de pronto do M2.1
- `GET /analise` de qualquer coluna numérica traz `forma` completa, com motivos em todo item não aplicável; nominal/ordinal com `forma = null` e motivo.
- Testes da spec 17 (Normal aderente, Exponencial não, Binomial conhecida) verdes; cobertura de `analise/` e `graficos/` ≥ 90% nos arquivos novos.
- `mypy --strict` verde com scipy, sem overrides.
