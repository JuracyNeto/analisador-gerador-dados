import { describe, expect, it } from 'vitest';
import { formatarCelula } from './formatarCelula';

describe('formatarCelula', () => {
  it.each([
    [58.2, '58,2'],
    [1234.5, '1.234,5'],
    [null, '—'],
    [undefined, '—'],
    [true, 'Sim'],
    [false, 'Não'],
    ['Goiânia', 'Goiânia'],
  ])('%s → %s', (valor, esperado) => {
    expect(formatarCelula(valor)).toBe(esperado);
  });

  it('inteiros saem como no arquivo, sem ponto de milhar (códigos, anos)', () => {
    expect(formatarCelula(2026001)).toBe('2026001');
    expect(formatarCelula(2026)).toBe('2026');
  });

  it('negativos usam o sinal de menos (D107)', () => {
    expect(formatarCelula(-3.5)).toBe('−3,5');
    expect(formatarCelula(-2)).toBe('−2');
  });
});
