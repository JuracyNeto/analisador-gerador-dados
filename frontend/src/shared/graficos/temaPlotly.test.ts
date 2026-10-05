import { describe, expect, it, vi } from 'vitest';
import {
  type TokensGrafico,
  extrairFigura,
  layoutTema,
  lerTokensGrafico,
  mesclarLayout,
} from './temaPlotly';

const TOKENS: TokensGrafico = {
  texto: '#161a20',
  texto2: '#4b5462',
  fundo: '#ffffff',
  grade: '#e6e9ee',
  eixo: '#868f9c',
  series: ['#0b6aa8', '#c4520a'],
  fonte: 'Inter, system-ui, sans-serif',
};

describe('layoutTema', () => {
  it('aplica cores, separadores pt-BR e paleta', () => {
    const layout = layoutTema(TOKENS);

    expect(layout).toMatchObject({
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      separators: ',.',
      colorway: ['#0b6aa8', '#c4520a'],
      font: { family: 'Inter, system-ui, sans-serif', size: 12, color: '#4b5462' },
      xaxis: { gridcolor: '#e6e9ee', linecolor: '#868f9c', zeroline: false },
    });
  });

  it('não compartilha objetos entre os eixos', () => {
    const layout = layoutTema(TOKENS);

    expect(layout.xaxis).not.toBe(layout.yaxis);
  });
});

describe('mesclarLayout', () => {
  it('mantém o que a figura define e completa com o tema', () => {
    const figura = {
      xaxis: { title: { text: 'peso_kg' } },
      barmode: 'overlay',
      colorway: ['#000000'],
    };

    const layout = mesclarLayout(figura, layoutTema(TOKENS));

    expect(layout).toMatchObject({
      barmode: 'overlay',
      colorway: ['#000000'],
      xaxis: {
        gridcolor: '#e6e9ee',
        title: { text: 'peso_kg', font: { size: 13, color: '#161a20' } },
      },
    });
  });
});

describe('extrairFigura', () => {
  it('extrai data e layout e copia os traces', () => {
    const traces = [{ type: 'bar', x: [1, 2], y: [3, 4] }];
    const figura = { data: traces, layout: { title: 'x' } };

    const extraida = extrairFigura(figura);

    expect(extraida).toEqual({ data: traces, layout: { title: 'x' } });
    expect(extraida.data).not.toBe(traces);
  });

  it('usa vazios quando o formato não confere', () => {
    expect(extrairFigura({ data: 'x', layout: [1] })).toEqual({ data: [], layout: {} });
  });
});

describe('lerTokensGrafico', () => {
  it('lê as variáveis CSS do documento', () => {
    vi.spyOn(window, 'getComputedStyle').mockReturnValue({
      getPropertyValue: (nome: string) => ` valor${nome} `,
    } as CSSStyleDeclaration);

    const tokens = lerTokensGrafico();

    expect(tokens.fundo).toBe('valor--graf-fundo');
    expect(tokens.series).toHaveLength(8);
    expect(tokens.series[0]).toBe('valor--graf-1');
  });
});
