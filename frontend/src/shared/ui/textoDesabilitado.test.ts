/// <reference types="node" />
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

/**
 * `--cor-texto-desab` tem contraste abaixo de 4,5:1 (D153): só pode aparecer onde a WCAG dispensa
 * o contraste — controle desabilitado ou bloqueado — ou numa marca decorativa (`aria-hidden`).
 * Texto que informa algo ("não se aplica") usa `--cor-texto-2`.
 */
const DISPENSADOS = /disabled|desabilitad|bloqueada|cadeado|ausente/u;
const TOKEN = 'var(--cor-texto-desab)';
// O Vitest roda na pasta do frontend.
const PASTA = 'src';

interface Regra {
  arquivo: string;
  seletor: string;
  corpo: string;
}

function regrasDe(arquivo: string): Regra[] {
  const css = readFileSync(join(PASTA, arquivo), 'utf8');
  return css.split('}').map((bloco) => {
    const partes = bloco.split('{');
    return { arquivo, seletor: (partes.at(-2) ?? '').trim(), corpo: partes.at(-1) ?? '' };
  });
}

const ARQUIVOS = readdirSync(PASTA, { recursive: true, encoding: 'utf8' }).filter(
  (arquivo) => arquivo.endsWith('.css') && !arquivo.endsWith('tokens.css'),
);

describe('--cor-texto-desab', () => {
  it('só aparece em estados desabilitados ou decorativos', () => {
    const usos = ARQUIVOS.flatMap(regrasDe).filter((regra) => regra.corpo.includes(TOKEN));
    const fora = usos.filter((regra) => !DISPENSADOS.test(regra.seletor));

    expect(usos.length).toBeGreaterThan(0);
    expect(fora.map((regra) => `${regra.arquivo}: ${regra.seletor}`)).toEqual([]);
  });
});
