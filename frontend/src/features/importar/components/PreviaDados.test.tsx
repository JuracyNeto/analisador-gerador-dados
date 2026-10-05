import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LINHAS_SAUDE } from '../../../testes/fixtures/datasets';
import PreviaDados from './PreviaDados';

describe('PreviaDados', () => {
  it('mostra as colunas do arquivo, números em pt-BR e faltante como —', () => {
    render(<PreviaDados linhas={LINHAS_SAUDE} totalLinhas={230} />);

    expect(screen.getByText('3 primeiras linhas de 230')).toBeInTheDocument();
    const tabela = screen.getByRole('table', { name: 'Prévia dos dados importados' });
    expect(
      within(tabela)
        .getAllByRole('columnheader')
        .map((c) => c.textContent),
    ).toEqual([
      'id',
      'sexo',
      'idade',
      'altura_m',
      'peso_kg',
      'escolaridade',
      'cidade',
      'satisfacao',
    ]);
    expect(within(tabela).getByText('1,62')).toBeInTheDocument();
    expect(within(tabela).getByText('—')).toBeInTheDocument();
  });
});
