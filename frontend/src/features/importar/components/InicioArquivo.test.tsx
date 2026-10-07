import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { METADADOS_COM_TITULO, METADADOS_SAUDE } from '../../../testes/fixtures/datasets';
import { TEXTOS_IMPORTAR as T } from '../textos';
import InicioArquivo from './InicioArquivo';

describe('InicioArquivo', () => {
  it('mostra as primeiras linhas numeradas e o papel de cada uma', () => {
    render(<InicioArquivo metadados={METADADOS_COM_TITULO} />);

    const tabela = screen.getByRole('table', { name: T.inicio.legenda });
    const linhas = within(tabela).getAllByRole('row').slice(1);
    expect(linhas.map((linha) => linha.textContent)).toEqual([
      '1Fica de foraPesquisa de satisfação',
      '2Fica de fora',
      '3Cabeçalhonomenota',
      '4Ana8.5',
    ]);
  });

  it('não aparece para JSON', () => {
    const { container } = render(
      <InicioArquivo metadados={{ ...METADADOS_SAUDE, linha_cabecalho: null }} />,
    );

    expect(container).toBeEmptyDOMElement();
  });
});
