import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { filtrarNumericas } from '../../../shared/api/colunas';
import { colunasBivariada } from '../../../testes/fixtures/bivariada';
import { TEXTOS_BIVARIADA } from '../textos';
import SeletoresPar from './SeletoresPar';

const S = TEXTOS_BIVARIADA.seletores;
const NUMERICAS = filtrarNumericas(colunasBivariada);
const PAR = { x: 'altura_m', y: 'peso_kg' };

function renderizar() {
  const aoMudar = vi.fn();
  render(<SeletoresPar colunas={NUMERICAS} par={PAR} aoMudar={aoMudar} />);
  return { aoMudar, usuario: userEvent.setup() };
}

describe('SeletoresPar', () => {
  it('lista só as numéricas e desabilita do outro lado a coluna escolhida', () => {
    renderizar();

    const x = screen.getByLabelText(S.x);
    const y = screen.getByLabelText(S.y);
    expect(
      within(x)
        .getAllByRole('option')
        .map((o) => o.getAttribute('value')),
    ).toEqual(['idade', 'altura_m', 'peso_kg']);
    expect(x.querySelector('option[value="peso_kg"]')).toBeDisabled();
    expect(y.querySelector('option[value="altura_m"]')).toBeDisabled();
  });

  it('mudar X mantém Y', async () => {
    const { aoMudar, usuario } = renderizar();

    await usuario.selectOptions(screen.getByLabelText(S.x), 'idade');

    expect(aoMudar).toHaveBeenCalledWith({ x: 'idade', y: 'peso_kg' });
  });

  it('"Trocar X e Y" inverte o par', async () => {
    const { aoMudar, usuario } = renderizar();

    await usuario.click(screen.getByRole('button', { name: S.trocar }));

    expect(aoMudar).toHaveBeenCalledWith({ x: 'peso_kg', y: 'altura_m' });
  });
});
