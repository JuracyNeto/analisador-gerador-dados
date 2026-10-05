import { describe, expect, it, vi } from 'vitest';
import { SESSAO_VAZIA, carregarSessao, comEtapaVisitada, interpretarSessao } from './persistencia';

const DATASET = { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' };

describe('interpretarSessao', () => {
  it.each([null, 'não é json', '[]', '{"dataset":{"id":"d1"}}', '{"dataset":null}'])(
    'devolve sessão vazia para %s',
    (texto) => {
      expect(interpretarSessao(texto)).toEqual(SESSAO_VAZIA);
    },
  );

  it('lê o dataset e só as etapas inteiras', () => {
    const texto = JSON.stringify({ dataset: DATASET, etapasVisitadas: [1, '2', 3.5, 4] });

    expect(interpretarSessao(texto)).toEqual({ dataset: DATASET, etapasVisitadas: [1, 4] });
  });

  it('descarta campos extras do dataset', () => {
    const texto = JSON.stringify({ dataset: { ...DATASET, senha: 'x' }, etapasVisitadas: 'x' });

    expect(interpretarSessao(texto)).toEqual({ dataset: DATASET, etapasVisitadas: [] });
  });
});

describe('comEtapaVisitada', () => {
  it('acrescenta sem repetir', () => {
    const uma = comEtapaVisitada({ dataset: DATASET, etapasVisitadas: [] }, 2);

    expect(comEtapaVisitada(uma, 2)).toBe(uma);
    expect(uma.etapasVisitadas).toEqual([2]);
  });
});

describe('carregarSessao', () => {
  it('devolve sessão vazia com o localStorage bloqueado', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('bloqueado');
    });

    expect(carregarSessao()).toEqual(SESSAO_VAZIA);
  });
});
