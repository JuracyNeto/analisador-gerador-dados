import { describe, expect, it } from 'vitest';
import { COLUNAS_SAUDE } from '../../testes/fixtures/datasets';
import { aplicarAlteracao, contarPorTipo, juntarExemplos, moverItem } from './regras';

describe('contarPorTipo', () => {
  it('conta na ordem do resumo, sem zeros e sem identificador', () => {
    expect(contarPorTipo(COLUNAS_SAUDE)).toEqual([
      { tipo: 'continua', quantidade: 2 },
      { tipo: 'discreta', quantidade: 1 },
      { tipo: 'ordinal', quantidade: 2 },
      { tipo: 'nominal', quantidade: 1 },
      { tipo: 'binaria', quantidade: 1 },
    ]);
  });
});

describe('juntarExemplos', () => {
  it('usa vírgula entre textos e ponto e vírgula entre números com vírgula decimal', () => {
    expect(juntarExemplos(['F', 'M'])).toBe('F, M');
    expect(juntarExemplos(['1,62', '1,78', '1,58'])).toBe('1,62; 1,78; 1,58');
  });

  it('mostra no máximo 4', () => {
    expect(juntarExemplos(['1', '2', '3', '4', '5'])).toBe('1, 2, 3, 4');
  });
});

describe('moverItem', () => {
  const lista = ['ruim', 'regular', 'bom', 'ótimo'];

  it('move para baixo e para cima sem mudar a lista original', () => {
    expect(moverItem(lista, 0, 1)).toEqual(['regular', 'ruim', 'bom', 'ótimo']);
    expect(moverItem(lista, 3, 0)).toEqual(['ótimo', 'ruim', 'regular', 'bom']);
    expect(lista).toEqual(['ruim', 'regular', 'bom', 'ótimo']);
  });

  it('devolve null quando não há o que mover', () => {
    expect(moverItem(lista, 0, -1)).toBeNull();
    expect(moverItem(lista, 3, 4)).toBeNull();
    expect(moverItem(lista, 2, 2)).toBeNull();
    expect(moverItem(lista, 9, 0)).toBeNull();
  });
});

describe('aplicarAlteracao', () => {
  it('troca o tipo, marca como manual e mantém as demais colunas', () => {
    const novas = aplicarAlteracao(COLUNAS_SAUDE, 'cidade', { tipo: 'ordinal' });

    expect(novas?.find((c) => c.coluna === 'cidade')).toMatchObject({
      tipo: 'ordinal',
      origem: 'manual',
    });
    expect(novas?.find((c) => c.coluna === 'idade')).toBe(COLUNAS_SAUDE[2]);
  });

  it('nova ordem de categorias substitui a anterior', () => {
    const novas = aplicarAlteracao(COLUNAS_SAUDE, 'satisfacao', {
      tipo: 'ordinal',
      categorias_ordem: ['ótimo', 'bom', 'regular', 'ruim'],
    });

    expect(novas?.find((c) => c.coluna === 'satisfacao')?.categorias_ordem).toEqual([
      'ótimo',
      'bom',
      'regular',
      'ruim',
    ]);
  });

  it('sem cache, nada a fazer', () => {
    expect(aplicarAlteracao(undefined, 'x', { tipo: 'nominal' })).toBeUndefined();
  });
});
