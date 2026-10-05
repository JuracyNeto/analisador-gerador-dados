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
});
