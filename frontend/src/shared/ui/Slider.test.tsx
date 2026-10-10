import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import Slider from './Slider';

describe('Slider', () => {
  it('mostra o valor em pt-BR com o sinal de menos e o anuncia', () => {
    render(
      <Slider
        rotulo="Correlação alvo (ρ)"
        valor={-0.35}
        aoMudar={vi.fn()}
        min={-1}
        max={1}
        passo={0.01}
      />,
    );

    const range = screen.getByRole('slider', { name: 'Correlação alvo (ρ)' });
    expect(range).toHaveAttribute('aria-valuetext', '−0,35');
    expect(screen.getByText('−0,35')).toBeInTheDocument();
    expect(screen.getByText('−1')).toBeInTheDocument();
  });

  it('mudar o range devolve o número', () => {
    const aoMudar = vi.fn();
    render(<Slider rotulo="ρ" valor={0.7} aoMudar={aoMudar} min={-1} max={1} passo={0.01} />);

    fireEvent.change(screen.getByRole('slider', { name: 'ρ' }), { target: { value: '0.5' } });

    expect(aoMudar).toHaveBeenCalledWith(0.5);
    expect(screen.getByText('0,70')).toBeInTheDocument();
  });
});
