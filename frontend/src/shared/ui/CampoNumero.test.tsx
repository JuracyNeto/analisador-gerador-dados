import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { expect, it } from 'vitest';
import CampoNumero from './CampoNumero';

function CampoControlado({ erro, ajuda }: Readonly<{ erro?: string; ajuda?: string }>) {
  const [valor, setValor] = useState('');
  return (
    <CampoNumero
      rotulo="Valor de peso_kg"
      valor={valor}
      aoMudar={setValor}
      erro={erro}
      ajuda={ajuda}
    />
  );
}

it('aceita vírgula decimal e abre o teclado numérico', async () => {
  render(<CampoControlado ajuda="Use vírgula para decimais." />);

  const campo = screen.getByRole('textbox', { name: 'Valor de peso_kg' });
  await userEvent.type(campo, '1,72');
  expect(campo).toHaveValue('1,72');
  expect(campo).toHaveAttribute('inputmode', 'decimal');
  expect(campo).toHaveAccessibleDescription('Use vírgula para decimais.');
  expect(campo).not.toHaveAttribute('aria-invalid');
});

it('mostra o erro ligado ao campo', () => {
  render(<CampoControlado erro="Digite um número. Use vírgula para decimais, como 1,72." />);

  const campo = screen.getByRole('textbox', { name: 'Valor de peso_kg' });
  expect(campo).toHaveAttribute('aria-invalid', 'true');
  expect(campo).toHaveAccessibleDescription(
    'Digite um número. Use vírgula para decimais, como 1,72.',
  );
});
