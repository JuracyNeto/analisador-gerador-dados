import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import BadgeSeveridade from './BadgeSeveridade';

describe('BadgeSeveridade', () => {
  it.each([
    ['alta', 'report', 'Suspeita alta'],
    ['atencao', 'warning', 'Atenção'],
    ['info', 'info', 'Informativo'],
  ] as const)('%s tem ícone e palavra, não só cor', (severidade, icone, palavra) => {
    render(<BadgeSeveridade severidade={severidade} />);

    const badge = screen.getByText(palavra);
    expect(badge).toHaveAttribute('data-severidade', severidade);
    expect(badge).toHaveTextContent(icone);
    expect(badge).toHaveStyle({ color: `var(--sev-${severidade})` });
  });

  it('no drawer usa o tamanho menor', () => {
    render(<BadgeSeveridade severidade="atencao" tamanho="sm" />);

    expect(screen.getByText('Atenção')).toHaveAttribute('data-tamanho', 'sm');
  });
});
