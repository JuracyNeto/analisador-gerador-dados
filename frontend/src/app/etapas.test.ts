import { describe, expect, it } from 'vitest';
import { ETAPAS, ehEtapaFutura, etapaDoCaminho } from './etapas';

describe('ETAPAS', () => {
  it('tem as 8 etapas em ordem', () => {
    expect(ETAPAS.map((etapa) => etapa.numero)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it('só 6 e 7 são futuras no M2 (Bivariada liberada)', () => {
    expect(ETAPAS.filter(ehEtapaFutura).map((etapa) => etapa.numero)).toEqual([6, 7]);
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
