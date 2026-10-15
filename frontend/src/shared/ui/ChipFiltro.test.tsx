import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import ChipFiltro from './ChipFiltro';

function ChipControlado() {
  const [marcado, setMarcado] = useState(true);
  return (
    <ChipFiltro
      rotulo="Suspeita alta (2)"
      marcado={marcado}
      cor="--sev-alta"
      aoAlternar={() => {
        setMarcado((anterior) => !anterior);
      }}
    />
  );
}

describe('ChipFiltro', () => {
  it('é um checkbox com o estado em aria-checked e o check quando marcado', () => {
    render(<ChipControlado />);

    const chip = screen.getByRole('checkbox', { name: 'Suspeita alta (2)' });
    expect(chip).toHaveAttribute('aria-checked', 'true');
    expect(chip).toHaveTextContent('check');
    expect(chip).toHaveStyle({ color: 'var(--sev-alta)' });
  });

  it('clique, espaço e Enter alternam', async () => {
    const usuario = userEvent.setup();
    render(<ChipControlado />);
    const chip = screen.getByRole('checkbox', { name: 'Suspeita alta (2)' });

    await usuario.click(chip);
    expect(chip).toHaveAttribute('aria-checked', 'false');
    expect(chip).not.toHaveTextContent('check');

    await usuario.keyboard(' ');
    expect(chip).toHaveAttribute('aria-checked', 'true');

    await usuario.keyboard('{Enter}');
    expect(chip).toHaveAttribute('aria-checked', 'false');
  });
});
