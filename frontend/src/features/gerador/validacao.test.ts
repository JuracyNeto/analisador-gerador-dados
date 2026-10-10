import { describe, expect, it } from 'vitest';
import { TEXTOS_GERADOR } from './textos';
import {
  errosDe,
  lerChance,
  lerDesvio,
  lerNumero,
  lerQuantidade,
  lerQuantidadePares,
  lerSemente,
} from './validacao';

const E = TEXTOS_GERADOR.erros;

describe('leituras', () => {
  it.each([
    ['500', { ok: true, valor: 500 }],
    ['1.000.000', { ok: true, valor: 1_000_000 }],
    ['0', { ok: false, erro: E.quantidade }],
    ['2,5', { ok: false, erro: E.quantidade }],
    ['1.000.001', { ok: false, erro: E.quantidade }],
  ])('quantidade "%s"', (texto, esperado) => {
    expect(lerQuantidade(texto)).toEqual(esperado);
  });

  it('pares precisam de pelo menos 3', () => {
    expect(lerQuantidadePares('2')).toEqual({ ok: false, erro: E.quantidadePares });
    expect(lerQuantidadePares('3')).toEqual({ ok: true, valor: 3 });
  });

  it.each([
    ['', { ok: true, valor: null }],
    ['42', { ok: true, valor: 42 }],
    ['-1', { ok: false, erro: E.semente }],
    ['4294967296', { ok: false, erro: E.semente }],
  ])('semente "%s"', (texto, esperado) => {
    expect(lerSemente(texto)).toEqual(esperado);
  });

  it('número, desvio e chance', () => {
    expect(lerNumero('−0,5')).toEqual({ ok: true, valor: -0.5 });
    expect(lerNumero('abc')).toEqual({ ok: false, erro: E.numero });
    expect(lerDesvio('0')).toEqual({ ok: false, erro: E.desvio });
    expect(lerDesvio('11,2')).toEqual({ ok: true, valor: 11.2 });
    expect(lerChance('1,2')).toEqual({ ok: false, erro: E.chance });
    expect(lerChance('0,3')).toEqual({ ok: true, valor: 0.3 });
  });

  it('errosDe junta só as leituras que falharam', () => {
    expect(
      errosDe([
        ['a', lerNumero('1')],
        ['b', lerNumero('x')],
      ]),
    ).toEqual({ b: E.numero });
  });
});
