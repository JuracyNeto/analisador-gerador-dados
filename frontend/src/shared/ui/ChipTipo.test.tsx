import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import ChipTipo from './ChipTipo';

describe('ChipTipo', () => {
  it('mostra o rótulo curto e o nome completo no tooltip', async () => {
    const usuario = userEvent.setup();
    render(<ChipTipo tipo="continua" curto />);

    await usuario.hover(screen.getByText('Contínua'));

    expect(await screen.findByRole('tooltip')).toHaveTextContent('Quantitativa contínua');
  });

  it('usa o rótulo completo por padrão', () => {
    render(<ChipTipo tipo="nominal" />);
    expect(screen.getByText('Qualitativa nominal')).toBeInTheDocument();
  });

  it('marca o tipo corrigido pelo usuário com um selo', () => {
    render(<ChipTipo tipo="ordinal" curto corrigido />);
    expect(screen.getByText('corrigido')).toBeInTheDocument();
  });

  it('expõe o tipo em data-tipo (identificador ganha borda tracejada no CSS)', () => {
    render(<ChipTipo tipo="identificador" curto />);
    expect(screen.getByText('Identificador').closest('[data-tipo]')).toHaveAttribute(
      'data-tipo',
      'identificador',
    );
  });
});
