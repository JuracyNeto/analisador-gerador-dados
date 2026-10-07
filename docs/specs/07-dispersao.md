# 07 — Medidas de dispersão
Domínio: `app/dominios/analise/` (`dispersao.py`)

## Aplicabilidade
Discreta e contínua: todas. Binária: variância p(1−p) e DP √(p(1−p)). Ordinal: amplitude em categorias ("de *baixo* a *muito alto*") e IQR em categorias. Nominal: —.

## Fórmulas
- Amplitude: **A = xₘₐₓ − xₘᵢₙ**
- Variância amostral: **s² = Σ(xᵢ − x̄)² / (n − 1)** · populacional: **σ² = Σ(xᵢ − μ)² / n**
- Desvio padrão: **s = √s²**
- Amplitude interquartil: **IQR = Q3 − Q1**
- Coeficiente de variação: **CV = (s / x̄) · 100%**
- Binária: **Var = p(1 − p)**

## Casos de borda
- n < 2 → variância/DP: "{medida} não se aplica: precisa de pelo menos 2 valores."
- x̄ = 0 → CV indefinido: "O CV não pode ser calculado porque a média é zero."
- Dados com valores negativos → CV calculado com |x̄| e aviso "CV pouco interpretável com valores negativos".
- s = 0 → "Todos os valores são iguais; não há dispersão."

## Interpretação automática do CV
| CV | Classificação | Frase |
|---|---|---|
| < 15% | baixa | "Os dados são homogêneos (pouca variação em relação à média)." |
| 15–30% | média | "Variação moderada em relação à média." |
| > 30% | alta | "Os dados são heterogêneos (muita variação em relação à média)." |
