# 08 — Gráficos por tipo de variável
Domínio: `app/dominios/graficos/` (`fabrica.py` + `tema.py`) · ADR 0003

## Matriz
| Tipo | Principal | Complementares | Por quê |
|---|---|---|---|
| Nominal | Barras **horizontais** ordenadas por frequência | Pizza **só se ≤ 5 categorias** | Comparar tamanhos é mais fácil em barras; pizza com muitas fatias confunde |
| Binária | Barras (2 categorias) com % no rótulo | — | Simples e direto |
| Ordinal | Barras verticais na **ordem da escala** | Barras de frequência acumulada | A ordem tem significado |
| Discreta | Gráfico de **bastões** (hastes) | Boxplot; acumulada em escada; na aba Forma: bastões + curva Normal e observado × Binomial | Valores isolados, não intervalos |
| Contínua | **Histograma** (classes da spec 04) | Boxplot, ogiva (Frᵢ); na aba Forma: histograma + curva Normal e QQ-plot (D56, D94) | Mostra forma, caudas e aderência |
| Par numérico | **Dispersão** com reta de regressão (até 5.000 pontos, D101) | Resíduos × X com linha zero tracejada (D102); heatmap da matriz com escala divergente (D103) | Spec 10 |
| Separatriz | Régua com marcas e marcador do valor | — | Spec 06 |
| Detector | Nos detalhes técnicos do alerta (D123): R1 linha da média de cada bloco de k linhas, com a média geral, a faixa x̄ ± s tracejada e o bloco alinhado em destaque; R8 barras do 1º dígito × Lei de Benford; R9 barras do último dígito × esperado (10%) | — | Spec 12; só valores agregados (uma média por bloco, uma barra por dígito) |

## Regras visuais
- Template Plotly único `analisador_tema` (cores/fontes alinhadas aos tokens do design; ver `docs/design/`).
- Paleta categórica acessível (daltonismo-safe), máx. 8 cores; acima disso, cor única.
- Títulos descritivos: "Distribuição de *idade* (n = 230)"; eixos com unidade quando houver.
- Rótulos de dados em barras com ≤ 12 categorias.
- Formato pt-BR (vírgula decimal, `separators=",."` no layout).
- Sem 3D, sem sombras, sem gradientes.
- Boxplot com estatísticas pré-calculadas; discrepantes como pontos (máx. 500).
- Cada traço traz o seu papel (`meta`: principal, referencia ou divergente — o heatmap, com escala `--graf-2` → fundo → `--graf-1`, D103), sem cor fixa: quem desenha pinta com o tema dele (relatório sempre claro; tela com o tema ativo) (D83). Nenhuma figura envia valores brutos (ADR 0003, D56).
- n > 5.000 → enviar bins agregados em vez de pontos brutos (ADR 0003).
