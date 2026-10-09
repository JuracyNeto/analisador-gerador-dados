import { describe, expect, it } from 'vitest';
import { filtrarAnalisaveis } from '../../shared/api/colunas';
import { colunasPesquisa } from '../../testes/fixturesAnalise';
import { colunaEscolhida, comClasses, comColuna, comTentativas, lerParametros } from './parametros';

describe('lerParametros', () => {
  it('lê coluna e classes da URL', () => {
    expect(lerParametros(new URLSearchParams('coluna=peso_kg&classes=12'))).toEqual({
      coluna: 'peso_kg',
      classes: 12,
      tentativas: null,
    });
  });

  it('sem parâmetros: nenhuma coluna e classes de Sturges', () => {
    expect(lerParametros(new URLSearchParams())).toEqual({
      coluna: null,
      classes: null,
      tentativas: null,
    });
  });

  it.each([
    ['2', 3],
    ['31', 30],
    ['abc', null],
    ['', null],
    ['7.5', null],
  ])('classes=%s vira %s', (texto, esperado) => {
    expect(lerParametros(new URLSearchParams({ classes: texto })).classes).toBe(esperado);
  });
});

describe('comColuna e comClasses', () => {
  it('trocar a coluna volta para Sturges e preserva o resto da busca', () => {
    expect(
      comColuna(new URLSearchParams('coluna=peso_kg&classes=12&x=1'), 'cidade').toString(),
    ).toBe('coluna=cidade&x=1');
  });

  it('limita o número de classes entre 3 e 30', () => {
    expect(comClasses(new URLSearchParams('coluna=peso_kg'), 40).get('classes')).toBe('30');
    expect(comClasses(new URLSearchParams('coluna=peso_kg'), 1).get('classes')).toBe('3');
  });
});

describe('colunaEscolhida', () => {
  const analisaveis = filtrarAnalisaveis(colunasPesquisa);

  it('usa a coluna da URL quando ela existe', () => {
    expect(colunaEscolhida('cidade', analisaveis)?.coluna).toBe('cidade');
  });

  it('cai na primeira coluna analisável quando a da URL não existe ou é identificador', () => {
    expect(colunaEscolhida('id', analisaveis)?.coluna).toBe('sexo');
    expect(colunaEscolhida(null, analisaveis)?.coluna).toBe('sexo');
  });

  it('devolve null quando não há colunas', () => {
    expect(colunaEscolhida('peso_kg', [])).toBeNull();
  });
});

describe('tentativas da Binomial na URL', () => {
  it('lê tentativas inteiras a partir de 1 e ignora o resto', () => {
    expect(lerParametros(new URLSearchParams('coluna=faltas&tentativas=10')).tentativas).toBe(10);
    expect(lerParametros(new URLSearchParams('tentativas=0')).tentativas).toBeNull();
    expect(lerParametros(new URLSearchParams('tentativas=2.5')).tentativas).toBeNull();
    expect(lerParametros(new URLSearchParams('tentativas=abc')).tentativas).toBeNull();
  });

  it('grava as tentativas sem mexer no resto', () => {
    expect(comTentativas(new URLSearchParams('coluna=faltas'), 20).toString()).toBe(
      'coluna=faltas&tentativas=20',
    );
  });

  it('trocar de coluna apaga classes e tentativas', () => {
    const nova = comColuna(new URLSearchParams('coluna=a&classes=5&tentativas=10'), 'b');
    expect(nova.toString()).toBe('coluna=b');
  });
});
