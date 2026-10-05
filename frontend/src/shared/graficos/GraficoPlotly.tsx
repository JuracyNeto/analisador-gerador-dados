import Plotly from 'plotly.js-dist-min';
import { useMemo } from 'react';
import criarComponentePlotly from 'react-plotly.js/factory';
import { CONFIG_PLOTLY, lerTokensGrafico, montarFigura } from './temaPlotly';

/** Bundle mínimo do Plotly (D63). Este módulo só é carregado por React.lazy em Grafico.tsx. */
const Plot = criarComponentePlotly(Plotly);

interface PropsGraficoPlotly {
  figura: Readonly<Record<string, unknown>>;
  altura: number;
}

export default function GraficoPlotly({ figura, altura }: Readonly<PropsGraficoPlotly>) {
  // Tokens lidos na montagem; Grafico remonta este componente (key = tema) quando o tema muda.
  const { data, layout } = useMemo(() => montarFigura(figura, lerTokensGrafico()), [figura]);
  return (
    <Plot
      data={data}
      layout={layout}
      config={CONFIG_PLOTLY}
      useResizeHandler
      style={{ width: '100%', height: altura }}
    />
  );
}
