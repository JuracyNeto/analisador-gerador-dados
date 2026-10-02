# 0003 — Figuras Plotly geradas no backend
- **Status:** Aceito
- **Data:** 02/10/2026

## Contexto
A regra "melhor gráfico para cada tipo de variável" deve valer igualmente na tela e no relatório HTML.

## Decisão
`app/dominios/graficos/fabrica.py` monta figuras com `plotly.graph_objects` e as devolve como dicionário (`fig.to_plotly_json()`). A API envia esse JSON; o React renderiza com `react-plotly.js`; o relatório embute as mesmas figuras com `plotly.io.to_html`. Tema visual (cores, fontes) definido num template Plotly único, alinhado aos tokens do design.

## Consequências
- (+) Uma única fonte da regra de gráficos; relatório idêntico à tela.
- (−) Payloads maiores (histogramas com muitos pontos). Mitigação: enviar dados agregados (bins) em vez de valores brutos quando n > 5.000.
- (−) Personalização de interação fica limitada ao que o Plotly oferece. Aceitável.
