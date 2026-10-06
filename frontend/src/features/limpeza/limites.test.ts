import { describe, expect, it } from 'vitest';
import { serializarLimites, validarLimite } from './limites';

describe('validarLimite', () => {
  it('aceita vírgula decimal e um lado só', () => {
    expect(validarLimite({ min: '1,20', max: '' })).toEqual({
      limites: { min: 1.2, max: null },
      erroMin: null,
      erroMax: null,
    });
  });

  it('vazio não é erro nem limite', () => {
    expect(validarLimite({ min: '', max: ' ' })).toEqual({
      limites: null,
      erroMin: null,
      erroMax: null,
    });
  });

  it('texto que não é número avisa no campo', () => {
    expect(validarLimite({ min: 'abc', max: '10' }).erroMin).toBe(
      'Use só números, com vírgula para decimais (ex.: 1,72).',
    );
  });

  it('mínimo maior ou igual ao máximo avisa com o máximo formatado', () => {
    expect(validarLimite({ min: '120', max: '110' })).toEqual({
      limites: null,
      erroMin: 'O mínimo precisa ser menor que o máximo (110). Ajuste um dos dois.',
      erroMax: null,
    });
  });
});

describe('serializarLimites', () => {
  it('JSON estável (colunas em ordem) só com limites válidos', () => {
    expect(
      serializarLimites({
        peso_kg: { min: '10', max: '5' },
        idade: { min: '1', max: '110' },
        altura_m: { min: '1,2', max: '' },
      }),
    ).toBe('{"altura_m":{"min":1.2,"max":null},"idade":{"min":1,"max":110}}');
    expect(serializarLimites({})).toBe('');
  });
});
