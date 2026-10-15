import { describe, expect, it } from 'vitest';
import { avisoR2, avisoR4, avisoR5 } from '../../testes/fixtures/detector';
import { exportarLinhas, nomeDoCsv } from './exportarLinhas';

describe('exportarLinhas', () => {
  it('CSV com ;, vírgula decimal, número da linha e a marca das destacadas', () => {
    const csv = exportarLinhas(
      [
        { linha: 119, valores: { cidade: 'Goiânia', peso_kg: 58.7, idade: 36 } },
        { linha: 120, valores: { cidade: 'Rio; Verde', peso_kg: -70, idade: null } },
        { linha: 121, valores: { cidade: 'Diz "oi"', peso_kg: 1234.5, idade: true } },
      ],
      ['cidade', 'peso_kg', 'idade'],
      new Set([120, 121]),
    );

    expect(csv).toBe(
      [
        'linha;cidade;peso_kg;idade;destacada',
        '119;Goiânia;58,7;36;não',
        '120;"Rio; Verde";-70;;sim',
        '121;"Diz ""oi""";1234,5;Sim;sim',
        '',
      ].join('\n'),
    );
  });
});

describe('nomeDoCsv', () => {
  it.each([
    [avisoR4, 'linhas-R4-peso_kg.csv'],
    [avisoR2, 'linhas-R2-altura_m-peso_kg.csv'],
    [avisoR5, 'linhas-R5.csv'],
  ])('%#: %s', (aviso, nome) => {
    expect(nomeDoCsv(aviso)).toBe(nome);
  });
});
