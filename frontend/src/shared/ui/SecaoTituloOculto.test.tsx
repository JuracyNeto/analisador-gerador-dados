import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import SecaoTituloOculto from './SecaoTituloOculto';

describe('SecaoTituloOculto', () => {
  it('é uma seção nomeada por um h2 que só o leitor de tela lê', () => {
    render(
      <SecaoTituloOculto titulo="Resumo dos problemas">
        <h3>Faltantes</h3>
      </SecaoTituloOculto>,
    );

    const secao = screen.getByRole('region', { name: 'Resumo dos problemas' });
    const titulo = screen.getByRole('heading', { level: 2, name: 'Resumo dos problemas' });
    expect(secao).toContainElement(titulo);
    expect(titulo).toHaveClass('visualmente-oculto');
    expect(secao).toContainElement(screen.getByRole('heading', { level: 3, name: 'Faltantes' }));
  });
});
