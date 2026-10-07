import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { COLUNAS_SAUDE } from '../../../testes/fixtures/datasets';
import ResumoTipos from './ResumoTipos';

describe('ResumoTipos', () => {
  it('lista a quantidade por tipo com plural', () => {
    render(<ResumoTipos colunas={COLUNAS_SAUDE} />);

    const itens = screen.getAllByRole('listitem').map((item) => item.textContent);
    expect(itens).toEqual(['2 contínuas', '1 discreta', '2 ordinais', '1 nominal', '1 binária']);
  });
});
