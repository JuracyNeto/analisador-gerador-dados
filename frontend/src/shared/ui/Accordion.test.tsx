import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import Accordion from './Accordion';

describe('Accordion', () => {
  it('começa recolhido e só monta o conteúdo quando abre', async () => {
    const usuario = userEvent.setup();
    render(
      <Accordion titulo="Detalhes técnicos">
        <p>Teste binomial</p>
      </Accordion>,
    );
    const gatilho = screen.getByRole('button', { name: 'Detalhes técnicos' });

    expect(gatilho).toHaveAttribute('aria-expanded', 'false');
    expect(gatilho).toHaveTextContent('chevron_right');
    expect(screen.queryByText('Teste binomial')).not.toBeInTheDocument();

    await usuario.click(gatilho);

    expect(gatilho).toHaveAttribute('aria-expanded', 'true');
    expect(gatilho).toHaveTextContent('expand_more');
    const conteudo = screen.getByText('Teste binomial').parentElement;
    expect(gatilho).toHaveAttribute('aria-controls', conteudo?.id);
  });

  it('pode começar aberto e mostra o complemento ao lado do título', async () => {
    const usuario = userEvent.setup();
    render(
      <Accordion titulo="Regras não verificadas" complemento="2 regras, com motivo" abertoInicial>
        <p>Lei de Benford</p>
      </Accordion>,
    );

    expect(screen.getByText('Lei de Benford')).toBeVisible();
    expect(screen.getByText('2 regras, com motivo')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: /Regras não verificadas/ }));
    expect(screen.queryByText('Lei de Benford')).not.toBeInTheDocument();
  });
});
