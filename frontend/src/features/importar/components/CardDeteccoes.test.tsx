import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { METADADOS_SAUDE } from '../../../testes/fixtures/datasets';
import CardDeteccoes from './CardDeteccoes';

describe('CardDeteccoes', () => {
  it('cada detecção é um Select com o motivo', async () => {
    const aoCorrigir = vi.fn();
    render(<CardDeteccoes metadados={METADADOS_SAUDE} opcoes={{}} aoCorrigir={aoCorrigir} />);

    expect(
      screen.getByText(
        'Lemos 230 linhas e 8 colunas. Se algo estiver diferente do seu arquivo, corrija abaixo.',
      ),
    ).toBeInTheDocument();
    const separador = screen.getByRole('combobox', { name: 'Separador' });
    expect(separador).toHaveValue(';');
    expect(screen.getByText('Aparece 7 vezes em todas as linhas.')).toBeInTheDocument();

    await userEvent.selectOptions(separador, ',');
    expect(aoCorrigir).toHaveBeenCalledWith('separador', ',');
  });

  it('formato é sempre só leitura', () => {
    render(<CardDeteccoes metadados={METADADOS_SAUDE} opcoes={{}} aoCorrigir={vi.fn()} />);

    expect(screen.queryByRole('combobox', { name: 'Formato' })).not.toBeInTheDocument();
    expect(screen.getByText('Texto (TXT)')).toBeInTheDocument();
  });
});
