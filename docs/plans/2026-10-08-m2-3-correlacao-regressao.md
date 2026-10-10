# M2.3 — Correlação e regressão (backend) — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 08, 10, 14 e 16, `docs/design/graficos-plotly.md` (heatmap) e os contratos em `docs/plans/2026-10-08-m2-visao-geral.md`.

**Objetivo:** para duas colunas numéricas, calcular Pearson (com teste t), Spearman, força e sentido, a reta Ŷ = a + bX, R², erro padrão da estimativa e resíduos, prever Y para um X (com aviso de extrapolação) e montar a matriz de correlação de todas as numéricas, com figuras (dispersão + reta, resíduos × X, heatmap), em três endpoints.

**Arquitetura:** domínio `analise` (spec 10): `correlacao.py` (Pearson, teste t, Spearman, classificação, matriz), `regressao.py` (coeficientes, R², Sₑ, resíduos, previsão), `bivariada.py` (montador do value object `Bivariada`, como o `univariada.py`), `textos_bivariada.py`. A fachada `ServicoAnalise` ganha `bivariada`, `prever` e `correlacoes`, montando os pares a partir de `ServicoDatasets.coluna_para_analise` (nenhum método novo no domínio `datasets`). Figuras no domínio `graficos` (`figuras_bivariadas.py` + fábrica). O router do domínio passa a ter prefixo `/datasets/{dataset_id}` (D99).

**Branch:** `feat/analise-bivariada` (sai de `develop` depois do merge do M2.2) → PR para `develop`. **Prazo sugerido:** 24/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Value objects, fórmulas e textos | `analise/resultados_bivariada.py`, `formulas.py`, `textos_bivariada.py` |
| 2 | Correlação (Pearson, teste t, Spearman) | `analise/correlacao.py` |
| 3 | Regressão e previsão | `analise/regressao.py` |
| 4 | Matriz de correlação | `analise/correlacao.py` (`matriz_correlacao`) |
| 5 | Montador da bivariada | `analise/bivariada.py` |
| 6 | Figuras: dispersão, resíduos, heatmap; papel `divergente` | `graficos/entradas.py`, `figuras_bivariadas.py`, `fabrica.py`, `tema.py`, `textos.py`, `servico.py` |
| 7 | Fachada, erros, schemas, router | `analise/servico.py`, `erros.py`, `schemas.py`, `router.py` |
| 8 | Tipos do frontend, specs, decisões e CHANGELOG | `schema.d.ts`, `docs/**` |
| 9 | Verificação, conferência no Swagger, resumo e PR | — |

### Regras que o código implementa
- **Pré-condições** (spec 10): X e Y discretas ou contínuas, diferentes; só linhas com X e Y válidos (`n_descartados` = linhas com faltante em um dos dois); n ≥ 3; X e Y com variação. Falhas viram erros 400 (D99) — tabela de códigos na visão geral.
- **Pearson:** r = Sxy / √(Sxx·Syy); `calculo` = "r = Sxy / √(Sxx · Syy) = 2,4 / √(10 · 1,2) = 0,7746". **Teste t:** t = r√(n − 2)/√(1 − r²), gl = n − 2, p bilateral com `stats.t.sf`; |r| = 1 → p = 0. Frase: "A correlação é significativa (chance de acontecer por acaso: {p_valor_em_palavras})." / "A correlação não é significativa: pode ter aparecido por acaso ({…})." **Spearman** com `stats.spearmanr` (interpretação: "Útil quando há valores extremos ou relação que não é uma reta.").
- **Força** por |r|: < 0,3 fraca · 0,3–0,7 moderada · ≥ 0,7 forte. **Sentido:** r > 0 positiva, r < 0 negativa, r = 0 nula. Interpretação do r: "Quando {x} aumenta, {y} tende a aumentar." / "… tende a diminuir." / fraca: "{x} e {y} quase não andam juntas." Selo (frontend): "Correlação positiva forte".
- **Regressão:** b = Sxy/Sxx, a = ȳ − b·x̄; `equacao` = "Ŷ = −98,4 + 98,1·X" (sinal pt-BR com "−"); `reta.interpretacao` = "A cada 1 a mais em {x}, o valor previsto de {y} {sobe|cai} cerca de {|b|}."; `r2.valor` em % (0–100): "{61}% da variação de {y} é explicada por {x}."; Sₑ = √[Σ(yᵢ − ŷᵢ)²/(n − 2)] com "Em média, as previsões erram cerca de {Sₑ} para mais ou para menos.".
- **Previsão:** ŷ = a + b·x; frase "Para {x} = 50, o valor previsto de {y} é 123,4."; fora de [mín X, máx X] → `extrapolacao = True` e `aviso` = "Fora da faixa observada. Os valores de {x} vão de 1,48 a 1,96. Prever fora disso (extrapolar) pode dar resultados pouco confiáveis." (texto de `telas.md`, D104). Nos limites (x = mín ou máx) não é extrapolação.
- **Matriz:** todas as colunas discretas e contínuas (ordem do arquivo), Pearson par a par só com as linhas em que as duas têm valor (`DataFrame.corr(min_periods=3)`); célula sem pares suficientes ou sem variação → `None`. Resumo: "O par mais forte é {a} × {b} ({r})." + "{col} quase não se relaciona com as outras." para colunas com todos os |r| < 0,3 (fora a diagonal). Menos de 2 colunas numéricas → `colunas` com 0–1 nome, `figura = None` e resumo "Precisa de pelo menos duas colunas numéricas para montar a matriz.".
- **Figuras** (D100–D102): dispersão (pontos `principal` tamanho 6, opacidade 0,7, `name` "Pontos (n = 227)"; reta `referencia` largura 2,5 com `name` = equação); resíduos × X (pontos `principal`; linha zero `referencia` tracejada `dash: "dash"`); n > 5.000 → amostra de 5.000 pontos com `np.random.default_rng(SEMENTE_AMOSTRA)` e resumo "Mostramos 5.000 dos {n} pontos."; heatmap com `meta: "divergente"`, `zmin −1`, `zmax 1`, valores anotados com 2 casas (`texttemplate: "%{text}"`, `text` formatado pt-BR), `colorbar` com marcas −1, 0, 1.

---

### Tarefa 1: value objects, fórmulas e textos

**Arquivos:** criar `analise/resultados_bivariada.py`, `analise/textos_bivariada.py`, `tests/dominios/analise/test_textos_bivariada.py`; modificar `formulas.py`

Value objects (campos do contrato da visão geral): `Par` (entrada do montador: `x: str`, `y: str`, `valores_x: np.ndarray`, `valores_y: np.ndarray`, `n_descartados: int`), `Faixa`, `Regressao`, `Bivariada`, `Previsao`, `MatrizCorrelacao`. `Bivariada.figuras` e `MatrizCorrelacao.figura` começam vazios (a fachada preenche, como no M1.5). Um arquivo novo em vez de crescer `resultados.py` (que chega a ~250 linhas no M2.1).

Fórmulas novas:
| chave | nome | texto |
|---|---|---|
| `pearson` | Correlação de Pearson | r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[Σ(xᵢ − x̄)² · Σ(yᵢ − ȳ)²] |
| `teste_t_correlacao` | Teste de significância de r | t = r√(n − 2) / √(1 − r²), gl = n − 2 |
| `spearman` | Correlação de Spearman | ρ = Pearson dos postos de X e de Y |
| `regressao` | Reta de regressão | Ŷ = a + bX · b = Σ(xᵢ − x̄)(yᵢ − ȳ) / Σ(xᵢ − x̄)² · a = ȳ − b·x̄ |
| `r2` | Coeficiente de determinação | R² = r² |
| `erro_padrao_estimativa` | Erro padrão da estimativa | Sₑ = √[Σ(yᵢ − ŷᵢ)² / (n − 2)] |
| `residuo` | Resíduo | eᵢ = yᵢ − ŷᵢ |

`textos_bivariada.py`: `formatar_equacao(a, b)`, `frase_forca(forca, sentido, x, y)`, `frase_significancia(p)`, `frase_r2(r2_pct, x, y)`, `frase_reta(b, x, y)`, `frase_se(se)`, `frase_previsao(x_nome, valor, y_nome, previsto)`, `aviso_extrapolacao(x_nome, faixa)`, `resumo_matriz(...)`.

**Testes (falham):** `formatar_equacao(-98.4, 98.1) == "Ŷ = −98,4 + 98,1·X"`; `formatar_equacao(2.2, -0.6) == "Ŷ = 2,2 − 0,6·X"`; `frase_reta(98.1, "altura_m", "peso_kg")` = "A cada 1 a mais em altura_m, o valor previsto de peso_kg sobe cerca de 98,1."; `aviso_extrapolacao("altura_m", Faixa(1.48, 1.96))` = texto acima; `frase_significancia(0.0004)` contém "menos de 1 em 1.000".

**Commit:** `feat(analise): value objects, fórmulas e textos da bivariada (spec 10)`

---

### Tarefa 2: correlação (`correlacao.py`)

**Arquivos:** criar `analise/correlacao.py`, `tests/dominios/analise/test_correlacao.py`

**Testes (falham)** — exemplo de livro X = [1, 2, 3, 4, 5], Y = [2, 4, 5, 4, 5] (conferido com scipy 1.18: r = 0,774597, p = 0,124027, ρ = 0,737865):
```python
X = np.array([1, 2, 3, 4, 5.0])
Y = np.array([2, 4, 5, 4, 5.0])


def test_pearson_do_exemplo() -> None:
    medida = pearson(X, Y)
    assert medida.valor == pytest.approx(0.774597, rel=1e-5)
    assert medida.formula == "pearson"


def test_teste_t_do_exemplo() -> None:
    medida = teste_t(0.774597, n=5)
    assert medida.valor == pytest.approx(0.124027, rel=1e-4)  # p-valor
    assert "não é significativa" in (medida.interpretacao or "")


def test_spearman_do_exemplo() -> None:
    assert spearman(X, Y).valor == pytest.approx(0.737865, rel=1e-5)


@pytest.mark.parametrize(
    ("y", "r", "sentido"),
    [(2 * X + 1, 1.0, "positiva"), (-3 * X + 10, -1.0, "negativa")],
)
def test_relacoes_perfeitas(y: np.ndarray, r: float, sentido: str) -> None:
    assert pearson(X, y).valor == pytest.approx(r)
    assert teste_t(r, n=5).valor == 0.0
    assert classificar(r) == ("forte", sentido)


def test_sem_relacao_e_fraca() -> None:
    rng = np.random.default_rng(3)
    x, y = rng.normal(size=500), rng.normal(size=500)
    forca, _ = classificar(float(pearson(x, y).valor))
    assert forca == "fraca"


@pytest.mark.parametrize(("r", "forca"), [(0.29, "fraca"), (0.3, "moderada"), (0.69, "moderada"), (0.7, "forte")])
def test_limites_de_forca(r: float, forca: str) -> None:
    assert classificar(r)[0] == forca
```
**Implementar:** `pearson(x, y) -> Medida`, `teste_t(r, n) -> Medida`, `spearman(x, y) -> Medida`, `classificar(r) -> tuple[Forca, Sentido]`. Somas Sxx, Syy, Sxy num helper `somas(x, y) -> Somas` (dataclass) reaproveitado pela regressão. Constantes `LIMIAR_MODERADA = 0.3`, `LIMIAR_FORTE = 0.7`.

**Commit:** `feat(analise): correlação de Pearson com teste t e Spearman`

---

### Tarefa 3: regressão e previsão (`regressao.py`)

**Arquivos:** criar `analise/regressao.py`, `tests/dominios/analise/test_regressao.py`

**Testes (falham)** — mesmo exemplo (b = 0,6; a = 2,2; R² = 60%; Sₑ = √0,8 = 0,894427; resíduos −0,8, 0,6, 1,0, −0,6, −0,2):
```python
def test_coeficientes_da_reta() -> None:
    reg = regressao(X, Y, nomes=("x", "y"))
    assert (reg.a, reg.b) == (pytest.approx(2.2), pytest.approx(0.6))
    assert reg.equacao == "Ŷ = 2,2 + 0,6·X"
    assert reg.r2.valor == pytest.approx(60.0)
    assert reg.se.valor == pytest.approx(0.894427, rel=1e-5)


def test_residuos() -> None:
    assert residuos(X, Y, a=2.2, b=0.6) == pytest.approx([-0.8, 0.6, 1.0, -0.6, -0.2])


def test_previsao_dentro_da_faixa() -> None:
    prev = prever(2.2, 0.6, valor=3.5, faixa=Faixa(1, 5), nomes=("x", "y"))
    assert prev.y_previsto == pytest.approx(4.3)
    assert not prev.extrapolacao and prev.aviso is None
    assert prev.frase == "Para x = 3,5, o valor previsto de y é 4,3."


@pytest.mark.parametrize("valor", [0.5, 8.0])
def test_previsao_fora_da_faixa_avisa(valor: float) -> None:
    prev = prever(2.2, 0.6, valor=valor, faixa=Faixa(1, 5), nomes=("x", "y"))
    assert prev.extrapolacao and prev.aviso is not None


@pytest.mark.parametrize("valor", [1.0, 5.0])
def test_limites_da_faixa_nao_sao_extrapolacao(valor: float) -> None:
    assert not prever(2.2, 0.6, valor=valor, faixa=Faixa(1, 5), nomes=("x", "y")).extrapolacao
```
**Implementar:** `regressao(x, y, nomes) -> Regressao`, `residuos(x, y, a, b) -> np.ndarray`, `prever(a, b, valor, faixa, nomes) -> Previsao`. `nomes` = `tuple[str, str]` (x, y). `calculo` da reta: "b = Sxy / Sxx = 2,4 / 4 = 0,6 · a = ȳ − b·x̄ = 4 − 0,6 · 3 = 2,2".

**Commit:** `feat(analise): regressão linear simples, resíduos e previsão com aviso de extrapolação`

---

### Tarefa 4: matriz de correlação

**Arquivos:** `correlacao.py` (+ `matriz_correlacao(tabela: pd.DataFrame) -> MatrizCorrelacao`), testes

**Testes (falham):** DataFrame com `a = [1..10]`, `b = 2a`, `c = ruído` (semente fixa), `d` com 2 valores e o resto `NaN` → `colunas == ["a", "b", "c", "d"]`, `valores[0][1] == 1.0`, diagonal 1,0, `valores[0][3] is None`; resumo cita "a × b (1)" e "c quase não se relaciona com as outras."; DataFrame com 1 coluna → resumo de "pelo menos duas colunas".

**Implementar:** `tabela.corr(method="pearson", min_periods=MIN_PARES)`; `NaN` → `None` (nada de `np.float64` saindo); resumo com `textos_bivariada.resumo_matriz`.

**Commit:** `feat(analise): matriz de correlação das colunas numéricas`

---

### Tarefa 5: montador da bivariada (`bivariada.py`)

**Arquivos:** criar `analise/bivariada.py`, `tests/dominios/analise/test_bivariada.py`

```python
def analisar_par(par: Par) -> Bivariada:
    """Correlação, regressão, faixa de X, interpretações e fórmulas do par (spec 10)."""
```
- `interpretacoes` = frase da força, frase da significância, frase do R² (para o relatório e o resumo da tela).
- `formulas` = `formulas_usadas([...])` com as chaves da bivariada.
- Testes: exemplo de livro → `n == 5`, `forca == "forte"`, `sentido == "positiva"`, `regressao.b == 0.6`, `faixa_x == Faixa(1, 5)`, chaves de fórmula esperadas; `n_descartados` repassado.

**Commit:** `feat(analise): montagem da análise bivariada`

---

### Tarefa 6: figuras da bivariada e papel `divergente`

**Arquivos:**
- Modificar: `graficos/entradas.py` (+ `DadosBivariados {x_nome, y_nome, x, y, a, b, equacao, n}`, `DadosMatriz {colunas, valores}`), `fabrica.py` (+ `figuras_bivariadas`, `figura_matriz`), `textos.py`, `tema.py`, `servico.py`
- Criar: `graficos/figuras_bivariadas.py`, `tests/dominios/graficos/test_figuras_bivariadas.py`; modificar `tests/dominios/graficos/test_tema.py`

| id | rótulo | título | resumo |
|---|---|---|---|
| `dispersao` | Dispersão | "{y} em função de {x} (n = 227)" | "Os pontos sobem da esquerda para a direita e ficam perto da reta." / "… descem …" / "Os pontos não seguem uma direção clara." (pela força e sentido) + aviso de amostra quando houver |
| `residuos` | Resíduos | "Resíduos da regressão" | "Resíduo é a diferença entre o {y} real e o previsto. Os pontos se espalham em volta do zero sem formar curva: a reta resume bem a relação." (texto de "Como ler os resíduos" do print 5a, com o nome da coluna; sem análise automática de padrão no M2) |
| `matriz` | Matriz | "Matriz de correlação (Pearson)" | resumo da matriz |

- `tema.py`: `PAPEL_DIVERGENTE = "divergente"`; `colorir` dá ao traço divergente `colorscale = [[0, --graf-2], [0.5, --graf-fundo], [1, --graf-1]]` e `opacity = 0.6`; `PAPEIS` inclui o novo papel.
- `figuras_bivariadas.py`: `dispersao(dados)`, `residuos(dados)`, `heatmap(dados)`; amostragem em `_amostrar(x, y, maximo=MAX_PONTOS)` (`MAX_PONTOS = 5000`, `SEMENTE_AMOSTRA = 20261008`), determinística.
- **Testes:** cada figura validada com `go.Figure`; dispersão com 2 traços (`principal` e `referencia`) e a reta passando por (mín X, a + b·mín X) e (máx X, …); resíduos com linha zero tracejada; 6.000 pontos → 5.000 no traço e resumo com "Mostramos 5.000 dos 6.000 pontos."; heatmap com `meta == "divergente"`, `zmin == -1`, `text` em pt-BR ("0,78"); `colorir` aplica a escala divergente e a opacidade (test_tema).

**Commit:** `feat(graficos): dispersão com reta, resíduos × X e heatmap da matriz`

---

### Tarefa 7: fachada, erros, schemas e router

**Arquivos:** modificar `analise/servico.py`, `erros.py`, `schemas.py`, `router.py`; testes `test_servico_bivariada.py`, `test_router_bivariada.py`

- `ServicoAnalise`:
  ```python
  def par(self, dataset_id: str, x: str, y: str) -> Par: ...          # valida tipos, iguais, n, variação
  def bivariada(self, dataset_id: str, x: str, y: str) -> Bivariada: ...
  def prever(self, dataset_id: str, x: str, y: str, valor: float) -> Previsao: ...
  def correlacoes(self, dataset_id: str) -> MatrizCorrelacao: ...
  ```
  `par` usa `coluna_para_analise` duas vezes, junta as séries pelo índice (número da linha, D49) e descarta linhas com faltante. As conversões de resultado → entradas de `graficos` ficam no `servico.py` (módulo de domínio não importa outro domínio, §2); se o arquivo passar de ~350 linhas, as conversões viram funções privadas agrupadas no fim do arquivo e os cálculos que sobrarem na fachada descem para `bivariada.py` (puro).
- `erros.py`: `coluna_nao_numerica(coluna, tipo)`, `colunas_iguais()`, `poucos_pares(n, x, y)`, `sem_variacao(coluna)` (mensagens da visão geral + sugestões: "Escolha colunas discretas ou contínuas.", "Escolha outra coluna para Y.", "Confira os faltantes na etapa Limpeza.", "Escolha outra coluna.").
- `schemas.py`: `Faixa`, `Regressao`, `Bivariada`, `Previsao`, `MatrizCorrelacao` (o arquivo fica perto de 300 linhas, abaixo do limite de 500).
- `router.py`: `APIRouter(prefix="/datasets/{dataset_id}", tags=["analise"])`; rotas `/colunas/{coluna}/analise`, `/colunas/{coluna}/posicao`, `/bivariada`, `/bivariada/prever`, `/correlacoes` (`summary` em português).
- **Testes de serviço** (`pesquisa_saude.txt`): `altura_m × peso_kg` → `forca == "forte"`, `sentido == "positiva"`, `n + n_descartados == 230` (sem limpeza), figuras `dispersao` e `residuos`; `cidade × peso_kg` → `COLUNA_NAO_NUMERICA`; `peso_kg × peso_kg` → `COLUNAS_IGUAIS`; `correlacoes` → `colunas == ["idade", "altura_m", "peso_kg"]` (as numéricas do exemplo), figura `matriz`.
- **Testes de API:** fluxo feliz dos 3 endpoints; `prever` fora da faixa com `extrapolacao: true`; 404 de dataset; `x` ausente → 422; rotas antigas da univariada continuam respondendo (regressão do prefixo).

**Commit:** `feat(analise): endpoints da bivariada, previsão e matriz de correlação`

---

### Tarefa 8: tipos do frontend, specs, decisões e CHANGELOG
- `exportar_openapi.py` → `gerar:tipos` → commit do `schema.d.ts`.
- `docs/specs/10-correlacao-regressao.md`: seção "Saída" com os contratos reais, erros, aviso de extrapolação de `telas.md`, resíduos × X (D101), amostragem (D100).
- `docs/specs/14-api.md`: respostas `Bivariada`, `Previsao`, `MatrizCorrelacao`; erros novos.
- `docs/specs/08-graficos.md` e `docs/design/graficos-plotly.md`: resíduos × X; papel `divergente` (D102).
- `docs/decisions.md`: D99–D102. `CHANGELOG.md` › Adicionado: "API da análise bivariada: correlação de Pearson (com teste t) e Spearman, regressão linear simples, resíduos, previsão de Y por X com aviso de extrapolação e matriz de correlação."

**Commit:** `docs: correlação e regressão (spec 10, API, decisões D99–D102)`

### Tarefa 9: verificação, conferência e PR
1. Verificação completa.
2. Preview `backend` → `/docs`: `GET /bivariada?x=altura_m&y=peso_kg` (exemplo), `prever` com `valor=2,1` (extrapolação) e `1,7`, `GET /correlacoes`; `notas_turma.csv`: `nota_p1 × nota_p2`. Conferir os números com uma conta à parte (scipy) no scratchpad.
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M2.3
- Os três endpoints respondem com os contratos da visão geral; erros com mensagem e sugestão.
- Testes da spec 17 (r = 1, r = −1, r ≈ 0, extrapolação) verdes; cobertura ≥ 90% nos arquivos novos.
- Rotas da univariada inalteradas (mesmo OpenAPI para elas).
