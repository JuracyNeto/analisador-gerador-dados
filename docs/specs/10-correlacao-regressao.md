# 10 — Correlação e regressão linear simples
Domínio: `app/dominios/analise/` (`correlacao.py`, `regressao.py`) · Endpoints: `GET /api/datasets/{id}/bivariada?x=&y=`, `GET .../bivariada/prever?x=&y=&valor=` · Marco M2

## Pré-condições
X e Y discretas ou contínuas; usar apenas pares com ambos não faltantes; n ≥ 3. Caso contrário: "Escolha duas colunas numéricas."

## Correlação
- Pearson: **r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[Σ(xᵢ − x̄)² · Σ(yᵢ − ȳ)²]**
- Teste de significância: **t = r√(n − 2) / √(1 − r²)**, gl = n − 2
- Complementar: Spearman ρ (postos) — exibido ao lado, útil quando há outliers ou relação não linear
- Matriz de correlação de todas as numéricas (heatmap) na tela Bivariada

| \|r\| | Força |
|---|---|
| < 0,3 | fraca |
| 0,3 – 0,7 | moderada |
| ≥ 0,7 | forte |
Sinal: positiva (crescem juntas) / negativa (uma cresce, outra diminui).

## Regressão Ŷ = a + bX
- **b = Σ(xᵢ − x̄)(yᵢ − ȳ) / Σ(xᵢ − x̄)²** · **a = ȳ − b·x̄**
- Coeficiente de determinação: **R² = r²** ("{R²·100}% da variação de Y é explicada por X")
- Erro padrão da estimativa: **Sₑ = √[Σ(yᵢ − ŷᵢ)² / (n − 2)]**
- Resíduos: eᵢ = yᵢ − ŷᵢ (gráfico de resíduos × X)

## Previsão
Entrada: valor de X. Saída: **ŷ = a + b·x**, com frase: "Para X = 50, o valor previsto de Y é 123,4."
Se x fora de [mín X, máx X] → aviso: "Cuidado: 80 está fora da faixa observada de X (10 a 60). A previsão pode não ser confiável (extrapolação)."

## Saída
`{n, r, r_p_valor, spearman, forca, sentido, a, b, r2, se, equacao, interpretacao, figuras{dispersao, residuos}, formulas[]}`
