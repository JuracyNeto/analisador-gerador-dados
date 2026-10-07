import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import TemaProvider from '../tema/TemaProvider';
import { useTema } from '../tema/useTema';
import Grafico from './Grafico';

const { montagens } = vi.hoisted(() => ({ montagens: vi.fn() }));

// Sem JSX no factory: o vi.mock é içado antes dos imports.
vi.mock('./GraficoPlotly', async () => {
  const { createElement, useEffect } = await import('react');
  function GraficoPlotlyFalso() {
    useEffect(() => {
      montagens();
    }, []);
    return createElement('div', { 'data-testid': 'grafico-plotly' });
  }
  return { default: GraficoPlotlyFalso };
});

function BotaoEscuro() {
  const { definirTema } = useTema();
  return (
    <button
      type="button"
      onClick={() => {
        definirTema('escuro');
      }}
    >
      escuro
    </button>
  );
}

function renderizar() {
  render(
    <TemaProvider>
      <BotaoEscuro />
      <Grafico
        titulo="Distribuição de peso_kg (n = 227)"
        resumo="A maior parte das pessoas pesa entre 60 e 80 kg."
        figura={{ data: [], layout: {} }}
      />
    </TemaProvider>,
  );
}

it('tem título, resumo e carrega o Plotly sob demanda', async () => {
  renderizar();

  const figura = screen.getByRole('figure', { name: 'Distribuição de peso_kg (n = 227)' });
  expect(figura).toHaveAccessibleDescription('A maior parte das pessoas pesa entre 60 e 80 kg.');
  expect(await screen.findByTestId('grafico-plotly')).toBeInTheDocument();
});

it('remonta o gráfico quando o tema muda', async () => {
  montagens.mockClear();
  renderizar();
  await screen.findByTestId('grafico-plotly');
  expect(montagens).toHaveBeenCalledTimes(1);

  await userEvent.click(screen.getByRole('button', { name: 'escuro' }));

  await waitFor(() => {
    expect(montagens).toHaveBeenCalledTimes(2);
  });
});
