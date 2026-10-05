import { describe, expect, it } from 'vitest';
import { ETAPAS } from '../etapas';
import { type ContextoEtapas, dicaDaEtapa, estadoDaEtapa } from './estadoEtapa';

const [IMPORTAR, VARIAVEIS, LIMPEZA] = ETAPAS;
const BIVARIADA = ETAPAS[4];

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
      estadoDaEtapa(BIVARIADA, contexto({ atual: 5, temDataset: true, visitadas: new Set([5]) })),
    ).toBe('bloqueada');
  });
});

describe('dicaDaEtapa', () => {
  it.each([
    [IMPORTAR, false, null],
    [BIVARIADA, false, 'Disponível na versão v0.2.'],
    [IMPORTAR, true, 'Importar'],
    [BIVARIADA, true, 'Bivariada. Disponível na versão v0.2.'],
  ] as const)('%o recolhida=%s → %s', (etapa, recolhida, esperado) => {
    expect(dicaDaEtapa(etapa, recolhida)).toBe(esperado);
  });
});
