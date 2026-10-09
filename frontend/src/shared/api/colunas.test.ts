import { describe, expect, it } from 'vitest';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { filtrarAnalisaveis, filtrarNumericas } from './colunas';

describe('colunas', () => {
  it('deixa de fora as colunas identificador e data', () => {
    expect(filtrarAnalisaveis(colunasPesquisa).map((c) => c.coluna)).toEqual([
      'sexo',
      'peso_kg',
      'cidade',
    ]);
  });

  it('para a bivariada, só as numéricas', () => {
    expect(filtrarNumericas(colunasPesquisa).map((c) => c.coluna)).toEqual(['peso_kg']);
  });
});
