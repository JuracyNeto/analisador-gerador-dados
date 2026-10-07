import { describe, expect, it } from 'vitest';
import { contarColunas, contarLinhas, escolherForma, pluralizar } from './pluralizar';

describe('pluralizar', () => {
  it.each([
    [0, '0 linhas'],
    [1, '1 linha'],
    [2, '2 linhas'],
    [1234, '1.234 linhas'],
  ])('%i → %s', (n, esperado) => {
    expect(pluralizar(n, 'linha', 'linhas')).toBe(esperado);
  });

  it('escolhe só a forma, sem o número', () => {
    expect(escolherForma(1, 'grupo', 'grupos')).toBe('grupo');
    expect(escolherForma(3, 'grupo', 'grupos')).toBe('grupos');
  });

  it('tem atalhos para linhas e colunas', () => {
    expect(`${contarLinhas(230)} × ${contarColunas(1)}`).toBe('230 linhas × 1 coluna');
  });
});
