# M3.0 — Gerador (backend) — plano de implementação

> **Para o agente:** execute tarefa por tarefa, em TDD. Antes de escrever código, leia `CLAUDE.md`, `docs/padroes-codigo.md`, as specs 08, 11, 14 e 16, `docs/design/graficos-plotly.md` e os contratos em `docs/plans/2026-10-10-m3-visao-geral.md`.

**Objetivo:** gerar X valores de uma coluna (preservando as estatísticas) ou com novos parâmetros, e pares (X, Y) com médias, desvios e correlação alvo; comparar original × gerado, explicar o método em linguagem simples, baixar o CSV e adotar o resultado como novo dataset ou anexá-lo ao atual.

**Arquitetura:** domínio `gerador` (spec 11):
```
gerador/
├── estrategias/        base.py (Protocol + ResultadoEstrategia) · continua.py · discreta.py · binaria.py · categorica.py
├── reescala.py         reescalar exato, casas decimais, limitar à faixa (D112)
├── univariado.py       registro tipo → estratégia (Strategy) e montagem
├── bivariado.py        Cholesky + Gram-Schmidt
├── comparacao.py       linhas Original × Gerado
├── textos.py           métodos, explicações, parâmetros
├── resultados.py       value objects (Geracao, LinhaComparacao, Parametro)
├── repositorio.py      RepositorioGerados (memória, FIFO, max_gerados)
├── erros.py · servico.py · schemas.py · router.py
```
`ServicoGerador(datasets, analise, repositorio)` usa `ServicoAnalise.amostra` (valores válidos e tipo), `ServicoAnalise.analisar` (teste de Normalidade e sucesso da binária), `ServicoAnalise.par` (pares do bivariado) e `ServicoAnalise.resumo_numerico` (novo, D108); `ServicoDatasets.importar` e `anexar_linhas` (novo) no adotar. Figuras no domínio `graficos` (`figuras_gerador.py` + fábrica).

**Branch:** `feat/gerador-backend` (sai de `develop`) → PR para `develop`. **Prazo sugerido:** 17/10/2026.

---

## Visão geral das tarefas

| # | Tarefa | Arquivos principais |
|---|---|---|
| 1 | Estatística compartilhada e `resumo_numerico` | `compartilhado/estatistica.py`, `analise/servico.py` |
| 2 | Reescala, casas e faixa | `gerador/reescala.py` |
| 3 | Estratégias univariadas | `gerador/estrategias/*`, `univariado.py` |
| 4 | Bivariado (Cholesky) | `gerador/bivariado.py` |
| 5 | Comparação, textos e value objects | `gerador/comparacao.py`, `textos.py`, `resultados.py` |
| 6 | Figuras: sobreposição e dispersão gerada | `graficos/entradas.py`, `figuras_gerador.py`, `fabrica.py`, `servico.py` |
| 7 | Repositório, fachada, erros, schemas, router | `gerador/repositorio.py`, `servico.py`, `erros.py`, `schemas.py`, `router.py`, `main.py`, `config.py` |
| 8 | CSV e adotar (novo/anexar) | `gerador/servico.py`, `datasets/servico.py` (`anexar_linhas`) |
| 9 | Tipos do frontend, specs, decisões e CHANGELOG | `schema.d.ts`, `docs/**` |
| 10 | Verificação, conferência no Swagger, resumo e PR | — |

### Regras que o código implementa
- **Contínua, preservar:** se `analisar(...).forma.normal.teste.compativel` → Normal(x̄, s); senão KDE (`stats.gaussian_kde(valores).resample(x, seed=rng)`). Depois **reescala** zᵢ = (gᵢ − ḡ)/s_g → gᵢ' = x̄ + s·zᵢ; arredonda nas casas do original (maior nº de casas observado, até 6). Método "Normal com reescala" / "KDE com reescala".
- **Contínua, parâmetros:** Normal(média, desvio) + reescala exata; 2 casas sem origem, as do original com origem.
- **Discreta, preservar:** x̄ > 0 e |x̄ − s²|/x̄ < 0,2 → Poisson(x̄); senão empírica (sorteio com as frequências relativas). **Parâmetros:** Normal + reescala, arredonda para inteiro; ≥ 0 se o original não tinha negativos (sem origem, sem limite).
- **Binária:** Bernoulli(p̂) com os rótulos do original e o sucesso da análise (`sucesso_padrao`); parâmetros: Bernoulli(p) com `rotulos` (padrão ["0", "1"], sucesso = o 2º).
- **Nominal/Ordinal:** só preservar (sorteio pelas frequências); `modo = parametros` → 400 `MODO_NAO_APLICAVEL`.
- **Limitar à faixa** (só origem numérica, D112): após a reescala, valores fora de [mín, máx] são sorteados de novo pelo mesmo método e a reescala é refeita, até 20 rodadas; o que sobrar é recortado. Explicação ganha "Valores fora de {mín} a {máx} foram sorteados de novo."
- **Bivariado** (Cholesky, spec 11): Z₁, Z₂ ~ N(0, 1); com `ajuste_exato`, centrar Z₁ e Z₂, Gram-Schmidt (Z₂ ⟂ Z₁) e normalizar (DP amostral 1); X = μx + σx·Z₁; Y = μy + σy·(ρZ₁ + √(1 − ρ²)Z₂). Com origem, parâmetros omitidos vêm do par (médias e DPs amostrais, r de Pearson); casas decimais das colunas de origem (sem origem, 2).
- **Semente** (D109): `semente or int(np.random.SeedSequence().entropy % 2**32)`; o mesmo pedido com a mesma semente dá o mesmo resultado.
- **Explicação** (exemplos, spec 11 e print 6a): "Sorteamos 500 valores de uma curva Normal com a mesma média (70,3) e desvio (11,2) de peso_kg, usando a semente 42, e ajustamos para bater exatamente essas medidas. Arredondamos com 1 casa decimal, como no original." · KDE: "Os dados de {col} não seguem uma curva Normal, então sorteamos valores parecidos com os originais (estimativa de densidade, KDE) e ajustamos a média e o desvio." · Poisson/empírica/Bernoulli/categórica/Cholesky com o mesmo tom (≤ 3 frases, primeira pessoa do plural).

---

### Tarefa 1: estatística compartilhada e `resumo_numerico`

**Arquivos:** `compartilhado/estatistica.py` (+ testes), `analise/servico.py` (`resumo_numerico`), `analise/resultados.py` (`ResumoNumerico`), `tests/dominios/analise/test_resumo_numerico.py`.

`ResumoNumerico {n, media, mediana, desvio_padrao, minimo, maximo, assimetria, curtose}` (floats ou `None`). G₁ e G₂ com as mesmas funções de `forma.py` (sem duplicar: a fachada chama o módulo da análise). Os testes estatísticos (`teste_binomial_unilateral`, `teste_qui_quadrado`, `teste_runs`, `autocorrelacao_lag1`) entram no M3.2, que os usa.

**Testes (falham):** `resumo_numerico(np.array([1, 2, 3, 4, 10.0]))` confere média 4, mediana 3, DP = `np.std(ddof=1)`, G₁ igual ao de `Analise.forma` para a mesma coluna; n = 2 → `assimetria is None`.

**Commit:** `feat(analise): resumo numérico na fachada para outros domínios (D108)`

### Tarefa 2: `reescala.py`

Funções puras: `reescalar(valores, media, desvio) -> np.ndarray`; `casas_decimais(valores) -> int` (maior nº de casas, até 6, olhando o texto pt-BR); `arredondar(valores, casas)`; `limitar_faixa(sortear: Callable[[int], np.ndarray], valores, minimo, maximo, alvo: tuple[float, float]) -> tuple[np.ndarray, bool]` (resorteio + reescala, até 20 rodadas; devolve se recortou).

**Testes (falham):** reescala dá média e DP exatos (`pytest.approx(rel=1e-12)`); `casas_decimais([1.5, 2.25, 3]) == 2`; com faixa [40, 100] e alvo (70, 11) nenhum valor fica fora e |média − 70| < 1%.

**Commit:** `feat(gerador): reescala exata, casas decimais e limite de faixa`

### Tarefa 3: estratégias univariadas

`estrategias/base.py`: `class Estrategia(Protocol): def gerar(self, pedido: EntradaEstrategia, rng: np.random.Generator) -> ResultadoEstrategia` com `EntradaEstrategia {x, modo, valores_originais | None, media, desvio, p, rotulos, sucesso, normal_compativel, limitar_faixa, casas}` e `ResultadoEstrategia {valores: pd.Series, metodo, chave_explicacao, recortou}`. `univariado.py`: `ESTRATEGIAS: dict[TipoVariavel, Estrategia]` (tabela de despacho, sem `if tipo`).

**Testes (falham)** — um arquivo por estratégia (`tests/dominios/gerador/estrategias/test_*.py`):
- contínua Normal: média e DP exatos (spec 11: dentro de 1%; com reescala, `rel=1e-9`), casas do original; não Normal (Exponencial(1), n = 300, semente 1) → método "KDE com reescala";
- discreta: média 3, variância 3,2 → "Poisson"; média 3, variância 9 → "Empírica" (só valores observados); parâmetros → inteiros, ≥ 0 quando o original não tem negativos;
- binária: p̂ ≈ proporção do sucesso da análise (n = 10.000, ±0,02); rótulos iguais;
- categórica: só categorias observadas; frequências ± 0,02 com n = 10.000;
- mesma semente → `np.array_equal`.

**Commit:** `feat(gerador): estratégias univariadas por tipo (spec 11)`

### Tarefa 4: `bivariado.py`

`gerar_pares(parametros: ParametrosBivariado, rng) -> tuple[np.ndarray, np.ndarray]`.

**Testes (falham):** ajuste exato, ρ = 0,7, n = 50 → |r − 0,7| < 1e-9, médias e DPs exatos; sem ajuste, n = 10.000 → |r − 0,7| < 0,03; ρ = ±1 → Y é função linear de X; ρ = 0 com ajuste exato → r = 0 (1e-9).

**Commit:** `feat(gerador): pares com correlação alvo por Cholesky (spec 11)`

### Tarefa 5: comparação, textos e value objects

`resultados.py`: `Parametro`, `LinhaComparacao`, `Geracao {id, tipo, colunas, dados: pd.DataFrame, semente, origem, metodo, explicacao, parametros, comparacao, figuras}` (o repositório guarda a `Geracao` inteira). `comparacao.py`: `comparar_numericos(original: ResumoNumerico | None, gerado: ResumoNumerico)`, `comparar_categoricos(original: pd.Series | None, gerado: pd.Series)`, `comparar_pares(...)`. `textos.py`: nomes das estatísticas, métodos, `explicacao(chave, contexto)`.

**Testes (falham):** linhas na ordem n, Média, Mediana, Desvio padrão, Mínimo, Máximo, Assimetria, Curtose; diferença = gerado − original; sem origem, `original is None`; categórica "fr% · F"; explicação da Normal com semente 42 = texto do exemplo acima.

**Commit:** `feat(gerador): comparação original × gerado e explicações`

### Tarefa 6: figuras

`graficos/entradas.py`: `DadosSobreposicao {coluna, numerica: bool, original: np.ndarray | pd.Series | None, gerado, n_original, n_gerado}` e `DadosParesGerados {x_nome, y_nome, x, y, x_original, y_original}`. `figuras_gerador.py`: `sobreposicao` (numérica: classes de Sturges sobre a união, fr% em barras `overlay` com opacidade 0,55, original `principal`, gerado `referencia`, `name` "Original (n = 227)" / "Gerado (n = 500)"; qualitativa: barras agrupadas por categoria) e `dispersao_gerada` (até 5.000 pontos por série, D101; original e gerado). Títulos: "peso_kg: original e gerado sobrepostos" · "Pares gerados (n = 500)". Resumo em frase ("As duas distribuições têm formas parecidas." quando a diferença máxima entre as barras < 5 p.p.; senão "As distribuições diferem em alguns trechos.").

**Testes (falham):** com 1.000.000 valores a figura tem só as barras (payload < 50 kB); papéis `principal`/`referencia`; `barmode == "overlay"`; qualitativa com uma barra por categoria em cada série.

**Commit:** `feat(graficos): sobreposição original × gerado e dispersão dos pares`

### Tarefa 7: repositório, fachada, erros, schemas, router

- `config.py`: `max_gerados: int = 20`, `limite_geracao: int = 1_000_000`, `tamanho_amostra_gerada: int = 50`.
- `RepositorioGerados` (como o de datasets) + `obter_repositorio_gerados()`/`obter_servico_gerador()` com `lru_cache` (ADR 0009); `tests/conftest.py` ganha o override.
- `ServicoGerador.univariado(pedido)`, `.bivariado(pedido)`, `.obter(gid)`; origem identificador/data → `COLUNA_NAO_GERAVEL`; numéricas exigidas no bivariado reaproveitam `COLUNA_NAO_NUMERICA` da análise; campos faltando → `PARAMETROS_INCOMPLETOS`.
- `schemas.py` com validações (`x` 1..1.000.000, `desvio > 0`, `p` 0..1, `rho` −1..1); `router.py` com prefixo `/gerador`, `summary`/`tags`.

**Testes (falham)** — `test_router.py` com `TestClient`: univariado de `peso_kg` (exemplo) → 201, 50 linhas na amostra, comparação com 8 linhas; mesma semente → mesmo `amostra`; nominal + parâmetros → 400 `MODO_NAO_APLICAVEL`; sem origem e sem `media` → 400 `PARAMETROS_INCOMPLETOS`; bivariado `altura_m × peso_kg` com ajuste exato → linha "Correlação (r)" com gerado = original (1e-9); `GET /gerador/xyz` → 404; 21 gerações → a 1ª some.

**Commit:** `feat(gerador): API do gerador univariado e bivariado`

### Tarefa 8: CSV e adotar

- `GET /gerador/{gid}/csv`: `;` como separador, vírgula decimal, UTF-8, `Content-Disposition` com `gerado-peso_kg.csv` (bivariado: `gerado-x-y.csv`).
- `POST /gerador/{gid}/adotar`: "novo" → `ServicoDatasets.importar(csv, nome, OpcoesLeitura())`; "anexar" → `ServicoDatasets.anexar_linhas(dataset_id, dados, frase)`: valida colunas (`COLUNAS_INCOMPATIVEIS`), converte para o formato bruto da coluna (texto com o decimal do arquivo quando a coluna foi lida como texto), concatena no fim de `atual` com índices novos, registra `EntradaLog` e atualiza contagens dos tipos (sem reclassificar).

**Testes (falham):** CSV relido pelo app dá a mesma coluna; "novo" → dataset com n linhas e tipo contínua; "anexar" de 500 valores em `peso_kg` no exemplo sem limpeza → `n_linhas` 730, log com "Anexamos 500 linhas geradas em peso_kg.", demais colunas faltantes nas linhas novas; `desfazer_limpeza` volta a 230 linhas; coluna inexistente → 400.

**Commit:** `feat(gerador): CSV e adotar como novo dataset ou anexar`

### Tarefa 9: tipos do frontend e documentação
- `exportar_openapi.py` → `gerar:tipos` → commit do `schema.d.ts`.
- Specs 11 (diferença absoluta, semente devolvida, limitar à faixa, endpoints `GET /gerador/{gid}`), 14 (rotas, erros), 17 (tolerâncias); `decisions.md` D108–D113 (próximos números livres); CHANGELOG › Adicionado: "API do gerador: dados univariados (preservando as estatísticas ou com novos parâmetros) e pares com correlação alvo, comparação com o original, explicação do método, CSV e uso como novo dataset ou anexado ao atual."

**Commit:** `docs: gerador de dados (spec 11, API, decisões)`

### Tarefa 10: verificação e PR
1. Verificação completa (backend, frontend, jscpd, tipos sem diferença).
2. Swagger (`http://localhost:8000/docs`): os 5 endpoints com o exemplo limpo; conferir explicações e comparação.
3. Resumo ao usuário antes do push; com o ok, push e PR.

## Critérios de pronto do M3.0
- Tolerâncias da spec 11 cobertas; nenhuma estratégia com `if tipo` fora da tabela de despacho.
- Figuras leves com 1.000.000 valores; adotar e anexar conferidos no Swagger.
