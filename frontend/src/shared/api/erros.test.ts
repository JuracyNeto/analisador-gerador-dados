import { describe, expect, it } from 'vitest';
import { ErroApi } from './cliente';
import { ehDatasetNaoEncontrado, textoDoErro } from './erros';

const SESSAO_EXPIRADA = new ErroApi(404, {
  codigo: 'DATASET_NAO_ENCONTRADO',
  mensagem: 'Sua sessão expirou.',
  sugestao: 'Envie o arquivo novamente.',
});

describe('ehDatasetNaoEncontrado', () => {
  it('reconhece o código DATASET_NAO_ENCONTRADO', () => {
    expect(ehDatasetNaoEncontrado(SESSAO_EXPIRADA)).toBe(true);
  });

  it.each([
    new ErroApi(404, { codigo: 'COLUNA_NAO_ENCONTRADA', mensagem: 'x', sugestao: 'y' }),
    new Error('Sua sessão expirou.'),
    'DATASET_NAO_ENCONTRADO',
    null,
  ])('ignora %s', (erro) => {
    expect(ehDatasetNaoEncontrado(erro)).toBe(false);
  });
});

describe('textoDoErro', () => {
  it('usa mensagem e sugestão da API', () => {
    expect(textoDoErro(SESSAO_EXPIRADA)).toEqual({
      mensagem: 'Sua sessão expirou.',
      sugestao: 'Envie o arquivo novamente.',
    });
  });

  it('completa a sugestão vazia com o texto genérico', () => {
    const erro = new ErroApi(400, { codigo: 'X', mensagem: 'O arquivo está vazio.', sugestao: '' });

    expect(textoDoErro(erro)).toEqual({
      mensagem: 'O arquivo está vazio.',
      sugestao: 'Tente de novo. Se continuar, recarregue a página.',
    });
  });

  it.each([new Error('TypeError interno'), 'texto', undefined])(
    'usa texto genérico para %s',
    (erro) => {
      expect(textoDoErro(erro)).toEqual({
        mensagem: 'Algo deu errado do nosso lado.',
        sugestao: 'Tente de novo. Se continuar, recarregue a página.',
      });
    },
  );
});
