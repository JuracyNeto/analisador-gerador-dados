import { describe, expect, it } from 'vitest';
import { ETAPAS, etapaDoCaminho } from './etapas';

describe('ETAPAS', () => {
  it('tem as 8 etapas em ordem', () => {
    expect(ETAPAS.map((etapa) => etapa.numero)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it('a etapa 7 é o Detector, liberado no M3.4', () => {
    expect(etapaDoCaminho('/detector')?.nome).toBe('Detector');
  });
});

describe('etapaDoCaminho', () => {
  it.each([
    ['/analise', 4],
    ['/analise/peso_kg', 4],
    ['/importar', 1],
  ])('%s é a etapa %s', (caminho, numero) => {
    expect(etapaDoCaminho(caminho)?.numero).toBe(numero);
  });

  it.each(['/', '/importarx', '/outra'])('%s não é etapa', (caminho) => {
    expect(etapaDoCaminho(caminho)).toBeUndefined();
  });
});
