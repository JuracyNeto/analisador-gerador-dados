import { describe, expect, it } from 'vitest';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { filtrarAnalisaveis } from './colunas';

describe('colunas', () => {
  it('deixa de fora as colunas identificador e data', () => {
    expect(filtrarAnalisaveis(colunasPesquisa).map((c) => c.coluna)).toEqual([
      'sexo',
      'peso_kg',
      'cidade',
    ]);
  });
});
