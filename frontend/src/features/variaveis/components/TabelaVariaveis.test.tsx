import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { COLUNAS_SAUDE, criarColuna } from '../../../testes/fixtures/datasets';
import TabelaVariaveis from './TabelaVariaveis';

describe('TabelaVariaveis', () => {
  it('mostra tipo, motivo, válidos/faltantes e exemplos de cada coluna', () => {
    render(<TabelaVariaveis colunas={COLUNAS_SAUDE} aoAlterarTipo={vi.fn()} />);

    const linha = screen.getByRole('row', { name: /peso_kg/ });
    expect(within(linha).getByText('Contínua')).toBeInTheDocument();
    expect(within(linha).getByText('Números com casas decimais.')).toBeInTheDocument();
    expect(within(linha).getByText('58,2; 79,6; 63,0')).toBeInTheDocument();
    expect(within(linha).getByRole('combobox', { name: 'Tipo de peso_kg' })).toHaveValue(
      'continua',
    );
  });

  it('corrigir o tipo chama aoAlterarTipo com coluna e tipo', async () => {
    const aoAlterarTipo = vi.fn();
    render(<TabelaVariaveis colunas={COLUNAS_SAUDE} aoAlterarTipo={aoAlterarTipo} />);

    await userEvent.selectOptions(
      screen.getByRole('combobox', { name: 'Tipo de cidade' }),
      'ordinal',
    );

    expect(aoAlterarTipo).toHaveBeenCalledWith('cidade', 'ordinal');
  });

  it('tipo escolhido pelo usuário aparece como corrigido', () => {
    render(
      <TabelaVariaveis
        colunas={[criarColuna({ coluna: 'cidade', tipo: 'ordinal', origem: 'manual' })]}
        aoAlterarTipo={vi.fn()}
      />,
    );

    expect(screen.getByText('corrigido')).toBeInTheDocument();
  });
});
