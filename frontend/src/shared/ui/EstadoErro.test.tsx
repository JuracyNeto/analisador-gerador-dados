import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { ErroApi } from '../api/cliente';
import EstadoErro from './EstadoErro';

it('mostra mensagem e sugestão da API e permite tentar de novo', async () => {
  const aoTentarDeNovo = vi.fn();
  const erro = new ErroApi(0, {
    codigo: 'SEM_CONEXAO',
    mensagem: 'Não conseguimos falar com o servidor.',
    sugestao: 'Verifique se o backend está rodando e tente novamente.',
  });
  render(<EstadoErro erro={erro} aoTentarDeNovo={aoTentarDeNovo} />);

  const alerta = screen.getByRole('alert');
  expect(alerta).toHaveTextContent('Não conseguimos falar com o servidor.');
  expect(alerta).toHaveTextContent('Verifique se o backend está rodando e tente novamente.');
  await userEvent.click(screen.getByRole('button', { name: 'Tentar de novo' }));
  expect(aoTentarDeNovo).toHaveBeenCalledOnce();
});

it('usa texto genérico para erro que não veio da API e não mostra botão sem callback', () => {
  render(<EstadoErro erro={new Error('falha interna')} />);

  expect(screen.getByRole('alert')).toHaveTextContent('Algo deu errado do nosso lado.');
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
