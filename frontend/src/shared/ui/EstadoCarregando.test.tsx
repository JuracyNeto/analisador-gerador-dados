import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import EstadoCarregando from './EstadoCarregando';

it.each(['cards', 'tabela', 'grafico'] as const)(
  'forma %s: anuncia a mensagem e marca aria-busy',
  (forma) => {
    const { container } = render(
      <EstadoCarregando forma={forma} mensagem="Calculando as estatísticas de peso_kg…" />,
    );

    expect(screen.getByRole('status')).toHaveTextContent('Calculando as estatísticas de peso_kg…');
    expect(container.firstElementChild).toHaveAttribute('aria-busy', 'true');
  },
);

it('várias formas: desenha os esqueletos em sequência com um só status (print 4h)', () => {
  const { container } = render(
    <EstadoCarregando
      forma={['cards', 'grafico']}
      mensagem="Calculando as estatísticas de peso_kg…"
    />,
  );

  expect(screen.getAllByRole('status')).toHaveLength(1);
  expect(container.querySelector('[aria-hidden="true"]')?.childElementCount).toBe(2);
});
