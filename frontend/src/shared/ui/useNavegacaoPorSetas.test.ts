import { describe, expect, it } from 'vitest';
import { idDestino } from './useNavegacaoPorSetas';

const IDS = ['a', 'b', 'c'] as const;

describe('idDestino', () => {
  it.each([
    ['a', 'ArrowRight', 'b'],
    ['c', 'ArrowRight', 'a'],
    ['a', 'ArrowLeft', 'c'],
    ['b', 'ArrowDown', 'c'],
    ['b', 'ArrowUp', 'a'],
    ['b', 'Home', 'a'],
    ['a', 'End', 'c'],
  ])('de %s com %s vai para %s', (atual, tecla, esperado) => {
    expect(idDestino(IDS, atual, tecla)).toBe(esperado);
  });

  it('ignora outras teclas', () => {
    expect(idDestino(IDS, 'a', 'Enter')).toBeUndefined();
  });
});
