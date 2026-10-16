import { describe, expect, it } from 'vitest';
import { alternar, secaoDisponivel, selecaoEfetiva } from './selecao';

describe('alternar', () => {
  it('tira o item que está e põe o que não está, sem mudar o original', () => {
    const original = new Set(['a']);

    expect([...alternar(original, 'a')]).toEqual([]);
    expect([...alternar(original, 'b')]).toEqual(['a', 'b']);
    expect([...original]).toEqual(['a']);
  });
});

describe('secaoDisponivel', () => {
  it('sem geração na sessão, só a seção Gerador fica de fora', () => {
    expect(secaoDisponivel('gerador', false)).toBe(false);
    expect(secaoDisponivel('gerador', true)).toBe(true);
    expect(secaoDisponivel('detector', false)).toBe(true);
  });
});

describe('selecaoEfetiva', () => {
  it('mantém seções e colunas quando há análises com colunas', () => {
    expect(
      selecaoEfetiva({ secoes: ['tipos', 'analises'], colunas: ['peso_kg'], gerado: null }),
    ).toEqual({ secoes: ['tipos', 'analises'], colunas: ['peso_kg'], gerado: null });
  });

  it('sem colunas, "analises" sai do pedido', () => {
    expect(selecaoEfetiva({ secoes: ['leitura', 'analises'], colunas: [], gerado: null })).toEqual({
      secoes: ['leitura'],
      colunas: [],
      gerado: null,
    });
  });

  it('sem "analises", as colunas não vão no pedido', () => {
    expect(selecaoEfetiva({ secoes: ['leitura'], colunas: ['peso_kg'], gerado: null })).toEqual({
      secoes: ['leitura'],
      colunas: [],
      gerado: null,
    });
  });

  it('só com "distribuicoes", as colunas continuam no pedido', () => {
    expect(
      selecaoEfetiva({ secoes: ['distribuicoes'], colunas: ['peso_kg'], gerado: null }),
    ).toEqual({ secoes: ['distribuicoes'], colunas: ['peso_kg'], gerado: null });
  });

  it('sem colunas, "analises" e "distribuicoes" saem do pedido', () => {
    expect(
      selecaoEfetiva({
        secoes: ['analises', 'distribuicoes', 'bivariada'],
        colunas: [],
        gerado: null,
      }),
    ).toEqual({ secoes: ['bivariada'], colunas: [], gerado: null });
  });

  it('"bivariada" sozinha não leva colunas', () => {
    expect(selecaoEfetiva({ secoes: ['bivariada'], colunas: ['peso_kg'], gerado: null })).toEqual({
      secoes: ['bivariada'],
      colunas: [],
      gerado: null,
    });
  });

  it('com geração, "gerador" fica e leva o id da geração', () => {
    expect(
      selecaoEfetiva({ secoes: ['gerador', 'detector'], colunas: ['peso_kg'], gerado: 'g-1' }),
    ).toEqual({ secoes: ['gerador', 'detector'], colunas: [], gerado: 'g-1' });
  });

  it('sem geração, "gerador" sai do pedido', () => {
    expect(selecaoEfetiva({ secoes: ['gerador', 'detector'], colunas: [], gerado: null })).toEqual({
      secoes: ['detector'],
      colunas: [],
      gerado: null,
    });
  });

  it('com "gerador" desmarcado, a geração não vai no pedido', () => {
    expect(selecaoEfetiva({ secoes: ['detector'], colunas: [], gerado: 'g-1' })).toEqual({
      secoes: ['detector'],
      colunas: [],
      gerado: null,
    });
  });

  it('nada efetivo vira null (estado vazio)', () => {
    expect(selecaoEfetiva({ secoes: [], colunas: ['peso_kg'], gerado: null })).toBeNull();
    expect(
      selecaoEfetiva({ secoes: ['analises', 'distribuicoes'], colunas: [], gerado: null }),
    ).toBeNull();
    expect(selecaoEfetiva({ secoes: ['gerador'], colunas: [], gerado: null })).toBeNull();
  });
});
