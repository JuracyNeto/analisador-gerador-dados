/** Tema Plotly a partir dos tokens CSS (docs/design/graficos-plotly.md). Funções puras, exceto lerTokensGrafico. */

type Objeto = Record<string, unknown>;

export interface TokensGrafico {
  texto: string;
  texto2: string;
  fundo: string;
  grade: string;
  eixo: string;
  series: readonly string[];
  fonte: string;
}

export interface FiguraPlotly {
  data: unknown[];
  layout: Objeto;
}

const VARIAVEIS_SERIES = [
  '--graf-1',
  '--graf-2',
  '--graf-3',
  '--graf-4',
  '--graf-5',
  '--graf-6',
  '--graf-7',
  '--graf-8',
] as const;

export const CONFIG_PLOTLY = {
  displaylogo: false,
  responsive: true,
  locale: 'pt-BR',
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
} as const;

export function lerTokensGrafico(raiz: Element = document.documentElement): TokensGrafico {
  const estilo = window.getComputedStyle(raiz);
  const ler = (variavel: string): string => estilo.getPropertyValue(variavel).trim();
  return {
    texto: ler('--cor-texto'),
    texto2: ler('--cor-texto-2'),
    fundo: ler('--graf-fundo'),
    grade: ler('--graf-grade'),
    eixo: ler('--graf-eixo'),
    series: VARIAVEIS_SERIES.map((variavel) => ler(variavel)),
    fonte: ler('--fonte-texto'),
  };
}

function criarEixo(tokens: TokensGrafico): Objeto {
  return {
    gridcolor: tokens.grade,
    linecolor: tokens.eixo,
    zeroline: false,
    ticks: '',
    title: { font: { size: 13, color: tokens.texto } },
  };
}

export function layoutTema(tokens: TokensGrafico): Objeto {
  return {
    font: { family: tokens.fonte, size: 12, color: tokens.texto2 },
    paper_bgcolor: tokens.fundo,
    plot_bgcolor: tokens.fundo,
    colorway: [...tokens.series],
    separators: ',.',
    margin: { l: 60, r: 16, t: 32, b: 48 },
    xaxis: criarEixo(tokens),
    yaxis: criarEixo(tokens),
    legend: { orientation: 'h', x: 0, y: 1.12, font: { size: 12, color: tokens.texto } },
    bargap: 0.04,
    hoverlabel: { font: { family: tokens.fonte } },
    autosize: true,
  };
}

function ehObjetoSimples(valor: unknown): valor is Objeto {
  return typeof valor === 'object' && valor !== null && !Array.isArray(valor);
}

function mesclarValor(daBase: unknown, daPrioridade: unknown): unknown {
  return ehObjetoSimples(daBase) && ehObjetoSimples(daPrioridade)
    ? mesclarProfundo(daBase, daPrioridade)
    : daPrioridade;
}

/** Mescla profunda; `prioridade` vence. Usa fromEntries (não atribuição) para não herdar __proto__ do JSON. */
export function mesclarProfundo(base: Objeto, prioridade: Objeto): Objeto {
  const chaves = new Set([...Object.keys(base), ...Object.keys(prioridade)]);
  return Object.fromEntries(
    [...chaves].map((chave) => [
      chave,
      Object.hasOwn(prioridade, chave) ? mesclarValor(base[chave], prioridade[chave]) : base[chave],
    ]),
  );
}

/** A figura do backend vence (títulos, barmode); o tema completa cores e fontes. */
export function mesclarLayout(figuraLayout: Objeto, tema: Objeto): Objeto {
  return mesclarProfundo(tema, figuraLayout);
}

export function extrairFigura(figura: Readonly<Objeto>): FiguraPlotly {
  const { data, layout } = figura;
  const traces: unknown[] = Array.isArray(data) ? structuredClone(data) : [];
  return { data: traces, layout: ehObjetoSimples(layout) ? layout : {} };
}

/** Papel de cada traço (`meta`, vindo do backend) → índice da série do tema (D83). */
const SERIE_DO_PAPEL: Readonly<Record<string, number>> = { principal: 0, referencia: 1 };
const PAPEL_DIVERGENTE = 'divergente';

/** Heatmap: `--graf-2` (−1) → fundo (0) → `--graf-1` (+1), igual ao tema do relatório (D103). */
export function escalaDivergente(tokens: TokensGrafico): [number, string][] {
  return [
    [0, tokens.series[1] ?? ''],
    [0.5, tokens.fundo],
    [1, tokens.series[0] ?? ''],
  ];
}

function temLinha(traco: Objeto): boolean {
  return traco.type === 'box' || (typeof traco.mode === 'string' && traco.mode.includes('lines'));
}

function objetoOuVazio(valor: unknown): Objeto {
  return ehObjetoSimples(valor) ? valor : {};
}

/** Pinta o traço com a série do seu papel; sem papel (pizza), fica o `colorway`. */
function pintarTraco(traco: unknown, tokens: TokensGrafico): unknown {
  if (!ehObjetoSimples(traco)) return traco;
  if (traco.meta === PAPEL_DIVERGENTE) return { ...traco, colorscale: escalaDivergente(tokens) };
  const { series } = tokens;
  const indice = SERIE_DO_PAPEL[String(traco.meta)];
  const cor = indice === undefined ? undefined : series[indice];
  if (cor === undefined) return traco;
  const pintado: Objeto = { ...traco, marker: { ...objetoOuVazio(traco.marker), color: cor } };
  if (temLinha(traco)) pintado.line = { ...objetoOuVazio(traco.line), color: cor };
  return pintado;
}

export function montarFigura(figura: Readonly<Objeto>, tokens: TokensGrafico): FiguraPlotly {
  const { data, layout } = extrairFigura(figura);
  return {
    data: data.map((traco) => pintarTraco(traco, tokens)),
    layout: mesclarLayout(layout, layoutTema(tokens)),
  };
}
