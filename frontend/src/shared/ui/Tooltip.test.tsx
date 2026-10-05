import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import Tooltip from './Tooltip';

function renderizar() {
  render(
    <Tooltip texto="Disponível na versão v0.2.">
      <button type="button" aria-disabled="true">
        Bivariada
      </button>
    </Tooltip>,
  );
  return {
    alvo: screen.getByRole('button', { name: 'Bivariada' }),
    dica: screen.getByRole('tooltip', { hidden: true }),
  };
}

it('liga o texto ao alvo e abre com o mouse', async () => {
  const { alvo, dica } = renderizar();

  expect(alvo).toHaveAttribute('aria-describedby', dica.id);
  expect(dica).not.toBeVisible();
  await userEvent.hover(alvo);
  expect(dica).toBeVisible();
  expect(dica).toHaveTextContent('Disponível na versão v0.2.');
  await userEvent.unhover(alvo);
  expect(dica).not.toBeVisible();
});

it('abre com o foco do teclado e fecha com Esc', async () => {
  const { dica } = renderizar();

  await userEvent.tab();
  expect(dica).toBeVisible();
  await userEvent.keyboard('{Escape}');
  expect(dica).not.toBeVisible();
});
