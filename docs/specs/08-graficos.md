# 08 — Gráficos por tipo de variável
Domínio: `app/dominios/graficos/` (`fabrica.py` + `tema.py`) · ADR 0003

## Matriz
| Tipo | Principal | Complementares | Por quê |
|---|---|---|---|
| Nominal | Barras **horizontais** ordenadas por frequência | Pizza **só se ≤ 5 categorias** | Comparar tamanhos é mais fácil em barras; pizza com muitas fatias confunde |
| Binária | Barras (2 categorias) com % no rótulo | — | Simples e direto |
| Ordinal | Barras verticais na **ordem da escala** | Barras de frequência acumulada | A ordem tem significado |
| Discreta | Gráfico de **bastões** (hastes) | Boxplot; acumulada em escada | Valores isolados, não intervalos |
| Contínua | **Histograma** (classes da spec 04); curva Normal ajustada no M2 (D56) | Boxplot, ogiva (Frᵢ); QQ-plot no M2 | Mostra forma, caudas e aderência |
| Par numérico | **Dispersão** com reta de regressão | Resíduos × X | Spec 10 |
| Separatriz | Régua com marcas e marcador do valor | — | Spec 06 |
| Detector | Gráficos específicos por regra (Benford: barras observado × esperado; último dígito: barras; blocos: linha da média por bloco com faixa total) | — | Spec 12 |

## Regras visuais
- Template Plotly único `analisador_tema` (cores/fontes alinhadas aos tokens do design; ver `docs/design/`).
- Paleta categórica acessível (daltonismo-safe), máx. 8 cores; acima disso, cor única.
- Títulos descritivos: "Distribuição de *idade* (n = 230)"; eixos com unidade quando houver.
- Rótulos de dados em barras com ≤ 12 categorias.
- Formato pt-BR (vírgula decimal, `separators=",."` no layout).
- Sem 3D, sem sombras, sem gradientes.
- Boxplot com estatísticas pré-calculadas; discrepantes como pontos (máx. 500). Nenhuma figura envia valores brutos (ADR 0003, D56).
- n > 5.000 → enviar bins agregados em vez de pontos brutos (ADR 0003).
