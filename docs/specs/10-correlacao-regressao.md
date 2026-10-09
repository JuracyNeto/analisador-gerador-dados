# 10 — Correlação e regressão linear simples
Domínio: `app/dominios/analise/` (`correlacao.py`, `regressao.py`) · Endpoints: `GET /api/datasets/{id}/bivariada?x=&y=`, `GET .../bivariada/prever?x=&y=&valor=` · Marco M2

## Pré-condições
X e Y discretas ou contínuas e diferentes; usar apenas pares com ambos não faltantes (`n_descartados` conta os outros); n ≥ 3; X e Y com variação. Caso contrário, erro 400: `COLUNA_NAO_NUMERICA` ("Escolha duas colunas numéricas: {col} não é numérica."), `COLUNAS_IGUAIS`, `POUCOS_PARES` ou `SEM_VARIACAO` (D100).

## Correlação
- Pearson: **r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[Σ(xᵢ − x̄)² · Σ(yᵢ − ȳ)²]**
- Teste de significância: **t = r√(n − 2) / √(1 − r²)**, gl = n − 2
- Complementar: Spearman ρ (postos) — exibido ao lado, útil quando há outliers ou relação não linear
- Matriz de correlação de todas as numéricas (heatmap) na tela Bivariada: Pearson par a par, só com as linhas em que as duas colunas têm valor (mínimo 3); célula sem pares suficientes = vazia. Resumo: o par mais forte e as colunas que quase não se relacionam com as outras (todos os |r| < 0,3)

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
- Resíduos: eᵢ = yᵢ − ŷᵢ (gráfico de resíduos × X, D102)
- Gráficos com no máximo 5.000 pontos: acima disso, amostra com semente fixa e aviso no resumo (D101)

## Previsão
Entrada: valor de X. Saída: **ŷ = a + b·x**, com frase: "Para X = 50, o valor previsto de Y é 123,4."
Se x fora de [mín X, máx X] (os limites contam como dentro) → `extrapolacao: true` e o aviso de `telas.md` (tela 5), com o título "Fora da faixa observada." no banner: "Os valores de altura_m vão de 1,48 a 1,96. Prever fora disso (extrapolar) pode dar resultados pouco confiáveis."

## Saída
- `GET /bivariada?x=&y=` → `Bivariada {x, y, n, n_descartados, pearson, teste_t, spearman: Medida, forca, sentido, regressao: {a, b, equacao, reta, r2, se}, faixa_x: {minimo, maximo}, interpretacoes[], formulas[], figuras[dispersao, residuos]}` — `teste_t.valor` é o p-valor; `regressao.r2.valor` em % (0–100).
- `GET /bivariada/prever?x=&y=&valor=` → `Previsao {x, y_previsto, extrapolacao, faixa_x, frase, aviso}`.
- `GET /correlacoes` → `MatrizCorrelacao {colunas[], valores[][], resumo, figura}` (heatmap com o papel `divergente`, D103).
