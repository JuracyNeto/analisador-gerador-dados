import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import Icone from './Icone';

it('é decorativo quando não tem rótulo', () => {
  const { container } = render(<Icone nome="check" />);

  expect(container.firstElementChild).toHaveAttribute('aria-hidden', 'true');
  expect(screen.queryByRole('img')).not.toBeInTheDocument();
});

it('vira imagem com nome acessível quando recebe rótulo', () => {
  render(<Icone nome="lock" rotulo="Bloqueada" />);

  expect(screen.getByRole('img', { name: 'Bloqueada' })).toHaveTextContent('lock');
});
