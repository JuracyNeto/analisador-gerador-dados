# 09 — Distribuições, assimetria e curtose
Domínio: `app/dominios/analise/` (`distribuicoes.py`, `forma.py`) · Marco M2

## Qual distribuição ajustar
| Tipo | Distribuição | Parâmetros estimados |
|---|---|---|
| Contínua | **Normal** | μ̂ = x̄, σ̂ = s |
| Binária | **Bernoulli** (Binomial com n = 1) | p̂ = proporção de sucesso; E[X] = p, Var = p(1 − p); sem teste de aderência (D95) |
| Discreta com todos os valores inteiros ≥ 0 (contagem de sucessos em n tentativas; usuário informa n em `?tentativas=`, padrão = máx observado; n < máx → erro `TENTATIVAS_INVALIDAS`) | **Binomial** | p̂ = x̄ / n (D96) |
| Discreta (demais) | **Normal** (aproximação), se n ≥ 30 | μ̂ = x̄, σ̂ = s |
| Nominal / ordinal | — | "Distribuições Normal/Binomial exigem números." |

## Testes de aderência
- Normal: **Shapiro-Wilk** (n ≤ 5.000) ou **D'Agostino-Pearson K²** (n > 5.000); complementar: qui-quadrado nas classes da spec 04, com a primeira e a última classes abertas até ±∞ e classes vizinhas agrupadas até esperado ≥ 5; gl = k − 3 (μ e σ estimados); gl < 1 → sem complementar (D97). Não se aplica com n < 3 ou desvio zero.
- Binomial: **qui-quadrado** observado × esperado, **χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ**, com as caudas agrupadas até esperado ≥ 5; gl = k − 1 − 1; gl < 1 → sem teste, com a frase "Há poucos grupos para testar a aderência…" (D96).
- Bernoulli (binária): com p estimado dos próprios dados, gl = 2 − 1 − 1 = 0 e o esperado repete o observado; não há teste (D95).
- Decisão com α = 0,05: p ≥ α → "Os dados são compatíveis com a distribuição {d}." ; p < α → "Os dados se afastam da distribuição {d}."

## Fórmulas
- Normal: **f(x) = (1 / (σ√(2π))) · e^(−(x−μ)² / (2σ²))**
- Binomial: **P(X = k) = C(n,k) · pᵏ · (1−p)ⁿ⁻ᵏ**, E[X] = np, Var = np(1−p)

## Assimetria
- Coeficiente de Fisher ajustado (amostral): **G₁ = [√(n(n−1)) / (n−2)] · m₃ / m₂^(3/2)**, com mₖ = Σ(xᵢ − x̄)ᵏ / n (`scipy.stats.skew(bias=False)`)
- 1º coeficiente de Pearson: **As₁ = (x̄ − Mo) / s** (Mo = moda de Czuber na contínua; moda bruta na discreta, só se unimodal — D98) · 2º: **As₂ = 3(x̄ − Md) / s**
- Interpretação (G₁): |G₁| < 0,5 → simétrica · 0,5–1 → moderada · > 1 → forte; sinal + → cauda à direita, − → cauda à esquerda

## Curtose
- Excesso de curtose (Fisher, amostral): **G₂ = scipy.stats.kurtosis(fisher=True, bias=False)** — referência Normal = 0
- Coeficiente percentílico: **K = (Q3 − Q1) / [2 (P90 − P10)]** — referência Normal ≈ 0,263
- Interpretação (G₂): |G₂| < 0,5 → **mesocúrtica** · G₂ > 0,5 → **leptocúrtica** (pico alto, caudas pesadas) · G₂ < −0,5 → **platicúrtica** (achatada)
- Mínimo: n ≥ 4 (curtose) e n ≥ 3 (assimetria)

## Visual
Histograma + curva teórica sobreposta; QQ-plot (contínua, no máximo 500 pontos — D98); barras observado × esperado (Binomial). As figuras ficam em `Forma.figuras` (ids `histograma_normal`, `qqplot`, `bastoes_normal`, `binomial`), fora do seletor da aba Gráficos (D94). Binária não tem figura de forma. Frase de interpretação conjunta: "Distribuição levemente assimétrica à direita e mesocúrtica; compatível com a Normal (p = 0,21)."

## Saída (`Analise.forma`, D94)
`Forma {assimetria, assimetria_pearson_1, assimetria_pearson_2, curtose, curtose_percentilica: Medida, classificacao_assimetria, sentido_assimetria, classificacao_curtose, normal: Ajuste, binomial: Ajuste, tentativas, interpretacao, figuras[]}` · `Ajuste {distribuicao: normal|binomial|bernoulli, aplicavel, motivo, parametros[{simbolo, nome, valor}], teste, complementar: TesteAderencia|None, frase, calculo, formula}` · `TesteAderencia {nome, estatistica, gl, p_valor, compativel}`. Nominal e ordinal: `forma = null` e item `forma` em `nao_aplicavel`. Chaves novas de `aplicavel`: `forma`, `assimetria`, `curtose`, `normal`, `binomial`.
