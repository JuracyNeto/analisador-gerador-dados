import { act, fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import type { PedidoToast } from './contextoToast';
import ToastProvider from './ToastProvider';
import { useToast } from './useToast';

function Disparador({ pedido }: Readonly<{ pedido: PedidoToast }>) {
  const { mostrar } = useToast();
  return (
    <button
      type="button"
      onClick={() => {
        mostrar(pedido);
      }}
    >
      mostrar
    </button>
  );
}

function mostrarToast(pedido: PedidoToast) {
  render(
    <ToastProvider>
      <Disparador pedido={pedido} />
    </ToastProvider>,
  );
  fireEvent.click(screen.getByRole('button', { name: 'mostrar' }));
}

function avancar(ms: number) {
  act(() => {
    vi.advanceTimersByTime(ms);
  });
}

beforeEach(() => {
  vi.useFakeTimers();
});

it('sucesso aparece como status e some depois de 6 s', () => {
  mostrarToast({
    tipo: 'sucesso',
    titulo: 'Arquivo lido: 230 linhas e 8 colunas.',
    descricao: 'As etapas 2 a 8 foram liberadas.',
  });

  expect(screen.getByRole('status')).toHaveTextContent('Arquivo lido: 230 linhas e 8 colunas.');
  avancar(5999);
  expect(screen.getByRole('status')).toBeInTheDocument();
  avancar(1);
  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});

it('erro aparece como alerta; a ação roda e fecha o aviso', () => {
  const aoClicar = vi.fn();
  mostrarToast({
    tipo: 'erro',
    titulo: 'Não conseguimos aplicar a limpeza.',
    acao: { rotulo: 'Tentar de novo', aoClicar },
  });

  fireEvent.click(
    within(screen.getByRole('alert')).getByRole('button', { name: 'Tentar de novo' }),
  );

  expect(aoClicar).toHaveBeenCalledOnce();
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it('pausa enquanto o mouse está em cima', () => {
  mostrarToast({ tipo: 'sucesso', titulo: 'Limpeza aplicada: 3 linhas removidas.' });

  fireEvent.mouseEnter(screen.getByRole('status'));
  avancar(10000);
  expect(screen.getByRole('status')).toBeInTheDocument();
  fireEvent.mouseLeave(screen.getByRole('status'));
  avancar(6000);
  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});

it('o botão Fechar aviso remove na hora', () => {
  mostrarToast({ tipo: 'sucesso', titulo: 'Tipo alterado.' });

  fireEvent.click(screen.getByRole('button', { name: 'Fechar aviso' }));

  expect(screen.queryByRole('status')).not.toBeInTheDocument();
});
