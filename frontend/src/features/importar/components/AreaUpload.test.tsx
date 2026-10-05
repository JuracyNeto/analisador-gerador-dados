import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import AreaUpload from './AreaUpload';

const ARQUIVO = new File(['a;b'], 'pesquisa_saude.txt', { type: 'text/plain' });
const TITULO = 'Arraste e solte seu arquivo aqui';

function renderizar(props: Partial<Parameters<typeof AreaUpload>[0]> = {}) {
  const aoEscolher = vi.fn();
  render(
    <AreaUpload
      enviando={false}
      nomeEnviando="pesquisa_saude.txt"
      comErro={false}
      aoEscolher={aoEscolher}
      {...props}
    />,
  );
  return { aoEscolher, area: screen.getByText(TITULO).closest('[data-estado]') };
}

describe('AreaUpload', () => {
  it('mostra o limite de 50 MB e os formatos aceitos', () => {
    renderizar();

    expect(
      screen.getByText('ou escolha no computador. Tamanho máximo: 50 MB.'),
    ).toBeInTheDocument();
    expect(screen.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      '.txt',
      '.csv',
      '.tsv',
      '.xlsx',
      '.json',
    ]);
  });

  it('entrega o arquivo escolhido no seletor', async () => {
    const { aoEscolher } = renderizar();

    await userEvent.upload(screen.getByLabelText('Arquivo de dados'), ARQUIVO);

    expect(aoEscolher).toHaveBeenCalledWith(ARQUIVO);
  });

  it('pelo teclado, Enter no botão abre o seletor de arquivo', async () => {
    const clique = vi.spyOn(HTMLInputElement.prototype, 'click');
    renderizar();

    await userEvent.tab();
    await userEvent.keyboard('{Enter}');

    expect(screen.getByRole('button', { name: /Escolher arquivo/ })).toHaveFocus();
    expect(clique).toHaveBeenCalled();
  });

  it('arrastar por cima muda o texto e soltar entrega o arquivo', () => {
    const { aoEscolher, area } = renderizar();
    if (area === null) throw new Error('área não encontrada');

    fireEvent.dragOver(area);
    expect(area).toHaveAttribute('data-estado', 'arrastando');
    expect(screen.getByText('Solte para enviar')).toBeInTheDocument();

    fireEvent.drop(area, { dataTransfer: { files: [ARQUIVO] } });
    expect(aoEscolher).toHaveBeenCalledWith(ARQUIVO);
  });

  it('enviando mostra progresso e desabilita o botão', () => {
    renderizar({ enviando: true });

    expect(screen.getByRole('progressbar', { name: 'Envio em andamento' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Enviando pesquisa_saude.txt/ })).toBeDisabled();
  });

  it('erro deixa a área no estado de erro', () => {
    const { area } = renderizar({ comErro: true });
    expect(area).toHaveAttribute('data-estado', 'erro');
  });
});
