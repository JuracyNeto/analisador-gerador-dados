/// <reference types="node" />
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

/**
 * Contraste WCAG 2.1 dos pares de tokens nos dois temas (D153): o jsdom não calcula cores, então
 * o axe dos testes não mede contraste. Texto: 4,5:1 (1.4.3); bordas de campos, foco e marcas dos
 * gráficos: 3:1 (1.4.11). `--cor-texto-desab` fica de fora: só vale em controles desabilitados,
 * que a WCAG dispensa. O arquivo é lido do disco: no Vitest, `import './tokens.css?raw'` vem
 * vazio.
 */
// O Vitest roda na pasta do frontend.
const CSS = readFileSync('src/shared/ui/tokens.css', 'utf8');
const TEXTO = 4.5;
const GRAFICO = 3;
const PRETO = '#000000';
const HEXADECIMAL = /^#[0-9a-f]{6}$/u;

function tokensDe(seletor: string): Record<string, string> {
  const inicio = CSS.indexOf(seletor);
  const corpo = CSS.slice(CSS.indexOf('{', inicio) + 1, CSS.indexOf('}', inicio));
  const declaracoes = corpo
    .split(';')
    .map((linha) => linha.split(':').map((parte) => parte.trim()));
  return Object.fromEntries(
    declaracoes
      .filter(([nome = '', valor = '']) => nome.startsWith('--') && HEXADECIMAL.test(valor))
      .map(([nome = '', valor = '']) => [nome.slice(2), valor]),
  );
}

const CLARO = tokensDe(':root,');
const TEMAS = { claro: CLARO, escuro: { ...CLARO, ...tokensDe("[data-tema='escuro']") } };

function canal(valor: number): number {
  return valor <= 0.03928 ? valor / 12.92 : ((valor + 0.055) / 1.055) ** 2.4;
}

function luminancia(hex: string): number {
  const [r = 0, g = 0, b = 0] = [1, 3, 5].map((i) =>
    canal(Number.parseInt(hex.slice(i, i + 2), 16) / 255),
  );
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function razao(frente: string, fundo: string): number {
  const [clara = 0, escura = 0] = [luminancia(frente), luminancia(fundo)].toSorted((a, b) => b - a);
  return (clara + 0.05) / (escura + 0.05);
}

const FUNDOS = ['cor-fundo', 'cor-superficie', 'cor-superficie-2', 'cor-zebra'];
const TEXTOS_SOBRE_FUNDOS = ['cor-texto', 'cor-texto-2', 'cor-primaria', 'cor-sucesso', 'cor-erro'];
const SEVERIDADES = ['info', 'atencao', 'alta'];
const TIPOS = ['nominal', 'ordinal', 'discreta', 'continua', 'binaria', 'identificador', 'data'];

type Par = readonly [frente: string, fundo: string, minimo: number];

const PARES: readonly Par[] = [
  ...[...TEXTOS_SOBRE_FUNDOS, ...SEVERIDADES.map((s) => `sev-${s}`)].flatMap((frente) =>
    FUNDOS.map((fundo): Par => [frente, fundo, TEXTO]),
  ),
  ['cor-texto-2', 'cor-primaria-suave', TEXTO],
  ['cor-primaria', 'cor-primaria-suave', TEXTO],
  ['cor-texto', 'cor-destaque-linha', TEXTO],
  ['cor-sobre-primaria', 'cor-primaria', TEXTO],
  ['cor-sobre-primaria', 'cor-primaria-hover', TEXTO],
  ['cor-sucesso', 'cor-sucesso-suave', TEXTO],
  ['cor-erro', 'cor-erro-suave', TEXTO],
  ...SEVERIDADES.map((s): Par => [`sev-${s}`, `sev-${s}-suave`, TEXTO]),
  ...TIPOS.map((t): Par => [`tipo-${t}`, `tipo-${t}-suave`, TEXTO]),
  ...['cor-foco', 'cor-borda-forte'].flatMap((frente) =>
    ['cor-fundo', 'cor-superficie', 'cor-superficie-2'].map((fundo): Par => [
      frente,
      fundo,
      GRAFICO,
    ]),
  ),
  ...[1, 2, 3, 4, 5, 6, 7, 8].map((i): Par => [`graf-${String(i)}`, 'graf-fundo', GRAFICO]),
  ['graf-eixo', 'graf-fundo', GRAFICO],
];

describe.each(Object.entries(TEMAS))('tokens do tema %s', (_tema, tokens) => {
  it('tem todas as cores dos pares', () => {
    const faltando = PARES.flatMap(([frente, fundo]) => [frente, fundo]).filter(
      (nome) => !(nome in tokens),
    );

    expect(faltando).toEqual([]);
  });

  it('cada par passa do contraste mínimo', () => {
    const medidos = PARES.map(([frente, fundo, minimo]) => ({
      par: `${frente} sobre ${fundo}`,
      minimo,
      valor: razao(tokens[frente] ?? PRETO, tokens[fundo] ?? PRETO),
    }));

    const abaixo = medidos
      .filter(({ valor, minimo }) => valor < minimo)
      .map(({ par, valor, minimo }) => `${par}: ${valor.toFixed(2)} (mínimo ${String(minimo)})`);

    expect(abaixo).toEqual([]);
  });
});
