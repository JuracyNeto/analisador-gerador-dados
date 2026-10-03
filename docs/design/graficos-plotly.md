# Gráficos — tema Plotly

ADR 0003: as figuras vêm do backend como JSON. O **frontend aplica o tema** por cima (`layout` mesclado) no wrapper `shared/graficos/Grafico.tsx`, lendo os tokens com `getComputedStyle(document.documentElement)`. Ao trocar o tema, refazer o layout (`Plotly.react`). O relatório HTML usa sempre o tema claro (valores hex de `tokens.md`), aplicado em `dominios/graficos/tema.py`.

```ts
const layoutTema = (t: Tokens): Partial<Layout> => ({
  font: { family: 'Inter, system-ui, sans-serif', size: 12, color: t.texto2 },
  paper_bgcolor: t.grafFundo, plot_bgcolor: t.grafFundo,
  colorway: [t.graf1, t.graf2, t.graf3, t.graf4, t.graf5, t.graf6, t.graf7, t.graf8],
  separators: ',.',
  margin: { l: 60, r: 16, t: 32, b: 48 },
  xaxis: { gridcolor: t.grafGrade, linecolor: t.grafEixo, zeroline: false, ticks: '', title: { font: { size: 13, color: t.texto } } },
  yaxis: { gridcolor: t.grafGrade, linecolor: t.grafEixo, zeroline: false, ticks: '', title: { font: { size: 13, color: t.texto } } },
  legend: { orientation: 'h', x: 0, y: 1.12, font: { size: 12, color: t.texto } },
  bargap: 0.04, hoverlabel: { font: { family: 'Inter' } },
});
const config = { displaylogo: false, responsive: true, locale: 'pt-BR', modeBarButtonsToRemove: ['lasso2d', 'select2d'] };
```
Regras: sem 3D, sombras ou gradientes. Barras com opacidade 0,85 (0,55 quando sobrepostas, `barmode: 'overlay'`). Linhas de referência (curva Normal, reta de regressão, média no boxplot) em `--graf-2`, largura 2–2,5; média tracejada `dash: 'dash'`. Pontos de dispersão tamanho 6, opacidade 0,7. Heatmap divergente: `--graf-2` (−1) → fundo (0) → `--graf-1` (+1), intensidade máx. 60%, valores anotados em mono 14/600 na cor de texto.

O título fica **fora** do Plotly (`<figcaption>` 14/600, descritivo: "Distribuição de peso_kg (n = 227)"), e o resumo textual aparece ao lado ou abaixo (13,5 texto-2). O wrapper recebe `titulo` e `resumo` e define `aria-label`.

## Gráfico por tipo (spec 08)
| Tipo | Principal | Também |
|---|---|---|
| Contínua | Histograma (classes de Sturges) | Boxplot horizontal com média, ogiva (Fr% acumulada), histograma + curva Normal, QQ-plot |
| Discreta | Barras verticais por valor | Boxplot |
| Ordinal | Barras na ordem da escala | — |
| Nominal | Barras horizontais ordenadas da maior para a menor, rótulo "fi (fr%)" na ponta | — |
| Binária | Barras (2 categorias) | — |
| Par numérico | Dispersão + reta | Resíduos × previsto com linha zero tracejada; heatmap da matriz |
A tela mostra uma nota "Por que este gráfico?" explicando a escolha em linguagem simples.
