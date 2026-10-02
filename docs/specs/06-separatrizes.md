# 06 — Separatrizes (quartis, decis, percentis)
Domínio: `app/dominios/analise/` (`separatrizes.py`) · Endpoint: `GET /api/datasets/{id}/colunas/{col}/posicao?valor=&tipo=`

## Aplicabilidade
Discreta e contínua: ✔ (numéricas). Ordinal: quartis como **categoria** (posição na ordem da escala). Nominal/binária: —.

## Cálculo
- Método: interpolação linear (`numpy.quantile(x, p, method="linear")`). Posição: **h = (n − 1)·p**; Qp = x₍⌊h⌋₎ + (h − ⌊h⌋)·(x₍⌊h⌋+1₎ − x₍⌊h⌋₎) (índices a partir de 0)
- Quartis: Q1, Q2, Q3 (p = 0,25; 0,50; 0,75)
- Decis: D1..D9 (p = 0,1..0,9)
- Percentis: P1..P99 (p = 0,01..0,99) — tela mostra P1, P5, P10, P25, P50, P75, P90, P95, P99 + tabela completa recolhida
- Ordinal: categoria cuja frequência relativa acumulada atinge p

## "Onde está meu valor?"
Entrada: `valor` (número) e `tipo` ∈ {quartil, decil, percentil}.
1. Posição percentil: **PR = 100 · (nº de xᵢ < v + 0,5 · nº de xᵢ = v) / n** (`scipy.stats.percentileofscore(kind="mean")`)
2. Região:
   - quartil: v ≤ Q1 → "1º quartil (até Q1)"; Q1 < v ≤ Q2 → "2º quartil (entre Q1 e Q2)"; …; v > Q3 → "4º quartil (acima de Q3)"
   - decil: entre Dₖ₋₁ e Dₖ → "k-ésimo decil"
   - percentil: ⌈PR⌉ limitado a 1..100 → "percentil k"
3. Fora do intervalo observado: avisar "O valor está abaixo do menor dado observado ({mín})" / acima do maior.

Saída: `{valor, tipo, regiao, indice, limite_inferior, limite_superior, posicao_percentil, frase}`.
Frase exemplo: "O valor 37 está no **2º quartil** (entre Q1 = 30 e Q2 = 41). Cerca de 42% dos dados são menores que ele."

## Visual
Régua horizontal (mín → máx) com marcas das separatrizes escolhidas e um marcador no valor informado.
