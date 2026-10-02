# 09 — Distribuições, assimetria e curtose
Domínio: `app/dominios/analise/` (`distribuicoes.py`, `forma.py`) · Marco M2

## Qual distribuição ajustar
| Tipo | Distribuição | Parâmetros estimados |
|---|---|---|
| Contínua | **Normal** | μ̂ = x̄, σ̂ = s |
| Binária | **Binomial** (n = 1, Bernoulli) | p̂ = proporção de sucesso |
| Discreta (contagem de sucessos em n tentativas; usuário informa n, padrão = máx observado) | **Binomial** | p̂ = x̄ / n |
| Discreta (demais) | **Normal** (aproximação), se n ≥ 30 | μ̂ = x̄, σ̂ = s |
| Nominal / ordinal | — | "Distribuições Normal/Binomial exigem números." |

## Testes de aderência
- Normal: **Shapiro-Wilk** (n ≤ 5.000) ou **D'Agostino-Pearson K²** (n > 5.000); complementar: qui-quadrado nas classes da spec 04 (agrupar classes com esperado < 5).
- Binomial: **qui-quadrado** observado × esperado, **χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ**, gl = k − 1 − 1.
- Decisão com α = 0,05: p ≥ α → "Os dados são compatíveis com a distribuição {d}." ; p < α → "Os dados se afastam da distribuição {d}."

## Fórmulas
- Normal: **f(x) = (1 / (σ√(2π))) · e^(−(x−μ)² / (2σ²))**
- Binomial: **P(X = k) = C(n,k) · pᵏ · (1−p)ⁿ⁻ᵏ**, E[X] = np, Var = np(1−p)

## Assimetria
- Coeficiente de Fisher ajustado (amostral): **G₁ = [√(n(n−1)) / (n−2)] · m₃ / m₂^(3/2)**, com mₖ = Σ(xᵢ − x̄)ᵏ / n (`scipy.stats.skew(bias=False)`)
- 1º coeficiente de Pearson: **As₁ = (x̄ − Mo) / s** · 2º: **As₂ = 3(x̄ − Md) / s**
- Interpretação (G₁): |G₁| < 0,5 → simétrica · 0,5–1 → moderada · > 1 → forte; sinal + → cauda à direita, − → cauda à esquerda

## Curtose
- Excesso de curtose (Fisher, amostral): **G₂ = scipy.stats.kurtosis(fisher=True, bias=False)** — referência Normal = 0
- Coeficiente percentílico: **K = (Q3 − Q1) / [2 (P90 − P10)]** — referência Normal ≈ 0,263
- Interpretação (G₂): |G₂| < 0,5 → **mesocúrtica** · G₂ > 0,5 → **leptocúrtica** (pico alto, caudas pesadas) · G₂ < −0,5 → **platicúrtica** (achatada)
- Mínimo: n ≥ 4 (curtose) e n ≥ 3 (assimetria)

## Visual
Histograma + curva teórica sobreposta; QQ-plot (contínua); barras observado × esperado (Binomial). Frase de interpretação conjunta: "Distribuição levemente assimétrica à direita e mesocúrtica; compatível com a Normal (p = 0,21)."
