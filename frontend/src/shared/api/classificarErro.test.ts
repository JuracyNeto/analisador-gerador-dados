import { describe, expect, it } from 'vitest';
import { ErroApi } from './cliente';
import { deveTentarDeNovo, ehErroDeEntrada } from './classificarErro';

const corpo = { codigo: 'X', mensagem: 'm', sugestao: 's' };

describe('classificarErro', () => {
  it('erro 4xx é de entrada e não se repete', () => {
    const erro = new ErroApi(404, corpo);
    expect(ehErroDeEntrada(erro)).toBe(true);
    expect(deveTentarDeNovo(0, erro)).toBe(false);
  });

  it('sem conexão (status 0) e 5xx tentam de novo até 2 vezes', () => {
    expect(deveTentarDeNovo(0, new ErroApi(0, corpo))).toBe(true);
    expect(deveTentarDeNovo(1, new ErroApi(500, corpo))).toBe(true);
    expect(deveTentarDeNovo(2, new ErroApi(500, corpo))).toBe(false);
  });

  it('erro que não veio da API não é de entrada', () => {
    expect(ehErroDeEntrada(new Error('x'))).toBe(false);
  });
});
