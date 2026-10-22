import { describe, expect, it } from 'vitest';
import { TEXTOS_DETECTOR as T } from './textos';

describe('toast de "Analisar de novo"', () => {
  it.each([
    [5, ['a', 'b', 'c'], 'Análise refeita: 5 alertas em 3 colunas.'],
    [1, ['a'], 'Análise refeita: 1 alerta em 1 coluna.'],
    [1, [], 'Análise refeita: 1 alerta.'],
    [0, [], 'Análise refeita: nenhum alerta.'],
  ])('%i alertas em %j → %s', (total, colunas, esperado) => {
    expect(T.analisadoDeNovo({ total, colunas_afetadas: colunas })).toBe(esperado);
  });
});
