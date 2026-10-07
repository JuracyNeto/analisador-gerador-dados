import { describe, expect, it } from 'vitest';
import { alternar, selecaoEfetiva } from './selecao';

describe('alternar', () => {
  it('tira o item que está e põe o que não está, sem mudar o original', () => {
    const original = new Set(['a']);

    expect([...alternar(original, 'a')]).toEqual([]);
    expect([...alternar(original, 'b')]).toEqual(['a', 'b']);
    expect([...original]).toEqual(['a']);
  });
});

describe('selecaoEfetiva', () => {
  it('mantém seções e colunas quando há análises com colunas', () => {
    expect(selecaoEfetiva({ secoes: ['tipos', 'analises'], colunas: ['peso_kg'] })).toEqual({
      secoes: ['tipos', 'analises'],
      colunas: ['peso_kg'],
    });
  });

  it('sem colunas, "analises" sai do pedido', () => {
    expect(selecaoEfetiva({ secoes: ['leitura', 'analises'], colunas: [] })).toEqual({
      secoes: ['leitura'],
      colunas: [],
    });
  });

  it('sem "analises", as colunas não vão no pedido', () => {
    expect(selecaoEfetiva({ secoes: ['leitura'], colunas: ['peso_kg'] })).toEqual({
      secoes: ['leitura'],
      colunas: [],
    });
  });

  it('nada efetivo vira null (estado vazio)', () => {
    expect(selecaoEfetiva({ secoes: [], colunas: ['peso_kg'] })).toBeNull();
    expect(selecaoEfetiva({ secoes: ['analises'], colunas: [] })).toBeNull();
  });
});
