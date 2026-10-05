import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import Select from './Select';

type Decimal = 'virgula' | 'ponto' | 'outro';

const OPCOES = [
  { valor: 'virgula', rotulo: 'Vírgula ( , )' },
  { valor: 'ponto', rotulo: 'Ponto ( . )' },
  { valor: 'outro', rotulo: 'Outro', desabilitada: true },
] as const;

it('associa rótulo e ajuda e devolve o valor escolhido', async () => {
  const aoMudar = vi.fn();
  render(
    <Select<Decimal>
      rotulo="Decimal"
      valor="virgula"
      opcoes={OPCOES}
      aoMudar={aoMudar}
      ajuda="Valores como 1,72 e 68,4."
    />,
  );

  const campo = screen.getByRole('combobox', { name: 'Decimal' });
  expect(campo).toHaveValue('virgula');
  expect(campo).toHaveAccessibleDescription('Valores como 1,72 e 68,4.');
  await userEvent.selectOptions(campo, 'ponto');
  expect(aoMudar).toHaveBeenCalledWith('ponto');
  expect(screen.getByRole('option', { name: 'Outro' })).toBeDisabled();
});

it('rótulo oculto continua dando nome ao campo', () => {
  render(
    <Select<Decimal>
      rotulo="Coluna"
      rotuloOculto
      valor="ponto"
      opcoes={OPCOES}
      aoMudar={vi.fn()}
    />,
  );

  expect(screen.getByRole('combobox', { name: 'Coluna' })).toBeInTheDocument();
});
