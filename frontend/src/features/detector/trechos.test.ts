import { describe, expect, it } from 'vitest';
import { descreverLinhas, descreverTrechos, trechosDoExemplo } from './trechos';

describe('trechosDoExemplo', () => {
  it('bloco seguido: um trecho com 3 linhas de contexto de cada lado', () => {
    const bloco = Array.from({ length: 19 }, (_, i) => 120 + i);

    expect(trechosDoExemplo(bloco)).toEqual([{ de: 117, ate: 141 }]);
  });

  it('o contexto para na linha 1', () => {
    expect(trechosDoExemplo([2, 1])).toEqual([{ de: 1, ate: 5 }]);
  });

  it('linhas distantes viram trechos separados; janelas que se tocam se juntam', () => {
    expect(trechosDoExemplo([99, 106, 160, 178])).toEqual([
      { de: 96, ate: 109 },
      { de: 157, ate: 163 },
      { de: 175, ate: 181 },
    ]);
  });
});

describe('descreverLinhas', () => {
  it.each([
    [[77], 'Linha 77'],
    [[120, 121, 122], 'Linhas 120 a 122'],
    [[44, 71], 'Linhas 44 e 71'],
    [[99, 106, 160, 178], 'Linhas 99, 106, 160 e 178'],
    [[1, 3, 5, 7, 9, 11, 13, 15, 17], 'Linhas 1, 3, 5, 7, 9, 11, 13, 15…'],
  ])('%j → %s', (linhas, texto) => {
    expect(descreverLinhas(linhas)).toBe(texto);
  });
});

describe('descreverTrechos', () => {
  it('um trecho ou vários, com "e" antes do último', () => {
    expect(descreverTrechos([{ de: 117, ate: 141 }])).toBe('117–141');
    expect(
      descreverTrechos([
        { de: 96, ate: 109 },
        { de: 157, ate: 163 },
        { de: 175, ate: 181 },
      ]),
    ).toBe('96–109, 157–163 e 175–181');
  });
});
