import { describe, expect, it } from 'vitest';
import { ETAPAS } from '../etapas';
import { type ContextoEtapas, dicaDaEtapa, estadoDaEtapa } from './estadoEtapa';

const [IMPORTAR, VARIAVEIS, LIMPEZA] = ETAPAS;
const GERADOR = ETAPAS[5];

function contexto(parcial: Partial<ContextoEtapas>): ContextoEtapas {
  return { atual: null, temDataset: false, visitadas: new Set(), ...parcial };
}

describe('estadoDaEtapa', () => {
  it('sem dataset só Importar abre', () => {
    expect(estadoDaEtapa(IMPORTAR, contexto({}))).toBe('disponivel');
    expect(estadoDaEtapa(IMPORTAR, contexto({ atual: 1 }))).toBe('atual');
    expect(estadoDaEtapa(VARIAVEIS, contexto({ atual: 1 }))).toBe('bloqueada');
  });

  it('com dataset: visitada vira concluída, a atual vence', () => {
    const comDados = contexto({ atual: 3, temDataset: true, visitadas: new Set([1, 3]) });

    expect(estadoDaEtapa(IMPORTAR, comDados)).toBe('concluida');
    expect(estadoDaEtapa(VARIAVEIS, comDados)).toBe('disponivel');
    expect(estadoDaEtapa(LIMPEZA, comDados)).toBe('atual');
  });

  it('etapa futura fica bloqueada mesmo com dataset e na própria rota', () => {
    expect(
      estadoDaEtapa(GERADOR, contexto({ atual: 6, temDataset: true, visitadas: new Set([6]) })),
    ).toBe('bloqueada');
  });
});

describe('dicaDaEtapa', () => {
  it.each([
    [IMPORTAR, false, null],
    [GERADOR, false, 'Disponível na versão v0.3.'],
    [IMPORTAR, true, 'Importar'],
    [GERADOR, true, 'Gerador. Disponível na versão v0.3.'],
  ] as const)('%o recolhida=%s → %s', (etapa, recolhida, esperado) => {
    expect(dicaDaEtapa(etapa, recolhida)).toBe(esperado);
  });
});
