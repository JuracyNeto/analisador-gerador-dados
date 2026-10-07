import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import TemaProvider from './TemaProvider';
import { useTema } from './useTema';

function Alternador() {
  const { tema, definirTema } = useTema();
  return (
    <button
      type="button"
      onClick={() => {
        definirTema(tema === 'claro' ? 'escuro' : 'claro');
      }}
    >
      {tema}
    </button>
  );
}

it('começa no tema já aplicado ao documento', () => {
  document.documentElement.dataset.tema = 'escuro';

  render(
    <TemaProvider>
      <Alternador />
    </TemaProvider>,
  );

  expect(screen.getByRole('button')).toHaveTextContent('escuro');
});

it('troca o tema, aplica no <html> e salva a escolha', async () => {
  render(
    <TemaProvider>
      <Alternador />
    </TemaProvider>,
  );

  await userEvent.click(screen.getByRole('button', { name: 'claro' }));

  expect(screen.getByRole('button')).toHaveTextContent('escuro');
  expect(document.documentElement).toHaveAttribute('data-tema', 'escuro');
  expect(localStorage.getItem('tema')).toBe('escuro');
});
