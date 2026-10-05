import { screen } from '@testing-library/react';
import { act } from 'react';
import { describe, expect, it } from 'vitest';
import { renderizarHook } from '../../testes/renderizar';
import { ErroApi } from '../api/cliente';
import { useAvisarErro } from './useAvisarErro';

describe('useAvisarErro', () => {
  it('mostra mensagem e sugestão da API num toast', async () => {
    const { result } = renderizarHook(() => useAvisarErro());

    act(() => {
      result.current(
        new ErroApi(400, {
          codigo: 'TIPO_INCOMPATIVEL',
          mensagem: 'Esta coluna tem textos; não pode ser numérica.',
          sugestao: 'Escolha um tipo qualitativo.',
        }),
      );
    });

    expect(
      await screen.findByText('Esta coluna tem textos; não pode ser numérica.'),
    ).toBeInTheDocument();
  });

  it('deixa a sessão expirada para o useSessaoExpirada', () => {
    const { result } = renderizarHook(() => useAvisarErro());

    act(() => {
      result.current(
        new ErroApi(404, {
          codigo: 'DATASET_NAO_ENCONTRADO',
          mensagem: 'Sua sessão expirou.',
          sugestao: 'Envie o arquivo novamente.',
        }),
      );
    });

    expect(screen.queryByText('Sua sessão expirou.')).not.toBeInTheDocument();
  });
});
