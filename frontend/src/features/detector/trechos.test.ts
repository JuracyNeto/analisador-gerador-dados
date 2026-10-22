import { describe, expect, it } from 'vitest';
import { descreverLinhas, descreverTrechos, trechosDoExemplo, trechosMostrados } from './trechos';

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
    [[1234], 'Linha 1.234'],
    [Array.from({ length: 39 }, (_, i) => 1200 + i), 'Linhas 1.200 a 1.238'],
    [[999, 1500], 'Linhas 999 e 1.500'],
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

  it('números de linha com ponto de milhar, como nos exemplos da API', () => {
    expect(descreverTrechos([{ de: 1197, ate: 1241 }])).toBe('1.197–1.241');
  });
});

describe('trechosMostrados', () => {
  it('cada trecho vai da 1ª à última linha que veio da API (o arquivo pode acabar antes)', () => {
    const carregados = [
      { linhas: [{ linha: 96 }, { linha: 109 }] },
      { linhas: [{ linha: 228 }, { linha: 260 }] },
      { linhas: [] },
    ];

    expect(trechosMostrados(carregados)).toEqual([
      { de: 96, ate: 109 },
      { de: 228, ate: 260 },
    ]);
  });
});
