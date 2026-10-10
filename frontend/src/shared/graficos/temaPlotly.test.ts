import { describe, expect, it, vi } from 'vitest';
import {
  type TokensGrafico,
  extrairFigura,
  layoutTema,
  lerTokensGrafico,
  mesclarLayout,
  montarFigura,
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

describe('montarFigura', () => {
  it('pinta cada traço pelo papel (meta) com as séries do tema ativo', () => {
    const escuro: TokensGrafico = { ...TOKENS, series: ['#56b4e9', '#f08a3c'] };
    const figura = {
      data: [
        { type: 'bar', meta: 'principal', marker: { opacity: 0.85 } },
        { type: 'scatter', mode: 'lines+markers', meta: 'principal', line: { width: 2 } },
        { type: 'box', meta: 'principal' },
        { type: 'scatter', mode: 'markers', meta: 'referencia' },
        { type: 'pie', labels: ['a'], values: [1] },
      ],
      layout: {},
    };

    const { data } = montarFigura(figura, escuro);

    expect(data).toEqual([
      { type: 'bar', meta: 'principal', marker: { opacity: 0.85, color: '#56b4e9' } },
      {
        type: 'scatter',
        mode: 'lines+markers',
        meta: 'principal',
        line: { width: 2, color: '#56b4e9' },
        marker: { color: '#56b4e9' },
      },
      { type: 'box', meta: 'principal', marker: { color: '#56b4e9' }, line: { color: '#56b4e9' } },
      { type: 'scatter', mode: 'markers', meta: 'referencia', marker: { color: '#f08a3c' } },
      { type: 'pie', labels: ['a'], values: [1] },
    ]);
    expect(figura.data[0]).toEqual({ type: 'bar', meta: 'principal', marker: { opacity: 0.85 } });
  });
});

describe('papel divergente (heatmap)', () => {
  it('pinta a escala com graf-2, fundo e graf-1 do tema ativo', () => {
    const figura = { data: [{ type: 'heatmap', meta: 'divergente', z: [[1]] }], layout: {} };

    const [traco] = montarFigura(figura, TOKENS).data as Record<string, unknown>[];

    expect(traco?.colorscale).toEqual([
      [0, '#c4520a'],
      [0.5, '#ffffff'],
      [1, '#0b6aa8'],
    ]);
    expect(traco).not.toHaveProperty('marker');
    expect(traco?.textfont).toEqual({ color: '#161a20' });
  });
});
