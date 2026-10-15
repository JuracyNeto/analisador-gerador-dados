import { describe, expect, it } from 'vitest';
import { chavesDataset } from '../../shared/api/dataset';
import { caminhoDetector, caminhoLinhas, chavesDetector } from './api';

describe('API do detector', () => {
  it('caminhos do resultado e das linhas', () => {
    expect(caminhoDetector('ds 1')).toBe('/datasets/ds%201/detector');
    expect(caminhoLinhas('ds1', { de: 117, ate: 141 })).toBe('/datasets/ds1/linhas?de=117&ate=141');
  });

  it('chaves sob as do dataset (limpeza, tipos e anexar invalidam o detector)', () => {
    const prefixo = chavesDataset.todas('ds1');
    for (const chave of [
      chavesDetector.resultado('ds1'),
      chavesDetector.linhas('ds1', { de: 1, ate: 4 }),
    ]) {
      expect(chave.slice(0, prefixo.length)).toEqual(prefixo);
    }
  });
});
