import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import CaixaSelecao from './CaixaSelecao';

it('alterna pelo rótulo', async () => {
  const aoMudar = vi.fn();
  render(<CaixaSelecao rotulo="Leitura do arquivo" marcada={false} aoMudar={aoMudar} />);

  await userEvent.click(screen.getByText('Leitura do arquivo'));

  expect(aoMudar).toHaveBeenCalledWith(true);
  expect(screen.getByRole('checkbox', { name: 'Leitura do arquivo' })).not.toBeChecked();
});

it('desabilitada não muda', async () => {
  const aoMudar = vi.fn();
  render(<CaixaSelecao rotulo="Forma e distribuição" marcada desabilitada aoMudar={aoMudar} />);

  const caixa = screen.getByRole('checkbox', { name: 'Forma e distribuição' });
  await userEvent.click(caixa);

  expect(caixa).toBeDisabled();
  expect(caixa).toBeChecked();
  expect(aoMudar).not.toHaveBeenCalled();
});
