import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { COLUNAS_SAUDE, criarColuna } from '../../../testes/fixtures/datasets';
import EditorOrdem from './EditorOrdem';

const ESCOLARIDADE = COLUNAS_SAUDE[5] ?? criarColuna({ coluna: 'escolaridade', tipo: 'ordinal' });
const TRANSFERENCIA = { dataTransfer: { setData: vi.fn(), effectAllowed: 'none' } };

function item(nome: string): HTMLElement {
  const li = screen.getByText(nome).closest('li');
  if (li === null) throw new Error(`item ${nome} não encontrado`);
  return li;
}

describe('EditorOrdem', () => {
  it('lista as categorias com posição, contagem e a escala', () => {
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={vi.fn()} />);

    expect(
      screen.getByRole('list', { name: 'Ordem das categorias de escolaridade' }),
    ).toBeInTheDocument();
    expect(screen.getByText('96 linhas')).toBeInTheDocument();
    expect(screen.getByText('fundamental < médio < superior < pós')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Subir fundamental' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Descer pós' })).toBeDisabled();
  });

  it('↓ na alça focada desce o item e anuncia a nova posição', async () => {
    const aoReordenar = vi.fn();
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={aoReordenar} />);

    screen.getByRole('button', { name: 'Mover fundamental' }).focus();
    await userEvent.keyboard('{ArrowDown}');

    expect(aoReordenar).toHaveBeenCalledWith(['médio', 'fundamental', 'superior', 'pós']);
    expect(screen.getByText('fundamental agora está na posição 2 de 4.')).toBeInTheDocument();
  });

  it('botão Subir sobe o item', async () => {
    const aoReordenar = vi.fn();
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={aoReordenar} />);

    await userEvent.click(screen.getByRole('button', { name: 'Subir pós' }));

    expect(aoReordenar).toHaveBeenCalledWith(['fundamental', 'médio', 'pós', 'superior']);
  });

  it('arrastar e soltar move para a posição do alvo', () => {
    const aoReordenar = vi.fn();
    render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={aoReordenar} />);

    fireEvent.dragStart(item('pós'), TRANSFERENCIA);
    expect(screen.getByText('Movendo…')).toBeInTheDocument();
    fireEvent.dragOver(item('fundamental'));
    fireEvent.drop(item('fundamental'));

    expect(aoReordenar).toHaveBeenCalledWith(['pós', 'fundamental', 'médio', 'superior']);
  });

  it('depois que a nova ordem chega, o foco continua no item movido', async () => {
    const { rerender } = render(<EditorOrdem coluna={ESCOLARIDADE} aoReordenar={vi.fn()} />);
    screen.getByRole('button', { name: 'Mover fundamental' }).focus();
    await userEvent.keyboard('{ArrowDown}');

    rerender(
      <EditorOrdem
        coluna={{ ...ESCOLARIDADE, categorias_ordem: ['médio', 'fundamental', 'superior', 'pós'] }}
        aoReordenar={vi.fn()}
      />,
    );

    expect(screen.getByRole('button', { name: 'Mover fundamental' })).toHaveFocus();
  });
});
