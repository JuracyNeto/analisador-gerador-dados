import { describe, expect, it } from 'vitest';
import {
  AVISOS,
  avisoR1,
  avisoR2,
  avisoR4,
  avisoR5,
  avisoR7,
  avisoR9,
  criarAviso,
} from '../../testes/fixtures/detector';
import { agrupar } from './agrupamento';
import { filtrarPorSeveridade } from './filtros';

describe('agrupar por coluna', () => {
  it('um grupo por coluna, par e linhas inteiras, na ordem em que aparecem', () => {
    const grupos = agrupar(AVISOS, 'coluna');

    expect(grupos.map((grupo) => [grupo.titulo, grupo.mono])).toEqual([
      ['altura_m', true],
      ['altura_m × peso_kg', true],
      ['Linhas inteiras', false],
      ['peso_kg', true],
      ['idade', true],
    ]);
    expect(grupos[1]?.avisos).toEqual([avisoR2]);
    expect(grupos[2]?.avisos).toEqual([avisoR5]);
  });

  it('dentro do grupo mantém a ordem da API', () => {
    const idade = agrupar(AVISOS, 'coluna').find((grupo) => grupo.titulo === 'idade');

    expect(idade?.avisos).toEqual([avisoR9, avisoR7]);
  });
});

describe('agrupar por regra', () => {
  it('título "R4 · Valores redondos" e avisos da mesma regra juntos', () => {
    const outroR7 = criarAviso({
      regra: 'R7',
      nome_regra: 'Valores distantes',
      colunas: ['peso_kg'],
    });

    const grupos = agrupar([avisoR1, avisoR7, avisoR4, outroR7], 'regra');

    expect(grupos.map((grupo) => grupo.titulo)).toEqual([
      'R1 · Bloco alinhado',
      'R7 · Valores distantes',
      'R4 · Valores redondos',
    ]);
    expect(grupos[1]?.avisos).toEqual([avisoR7, outroR7]);
    expect(grupos.every((grupo) => !grupo.mono)).toBe(true);
  });
});

describe('filtrarPorSeveridade', () => {
  it('fica só com as severidades marcadas, na mesma ordem', () => {
    expect(filtrarPorSeveridade(AVISOS, new Set(['alta', 'info'] as const))).toEqual([
      avisoR1,
      avisoR2,
      avisoR5,
      avisoR7,
    ]);
  });
});
