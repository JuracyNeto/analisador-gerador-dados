import { screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { chamadasPara, simularApi } from '../../../testes/api';
import { avisoR4, avisoR5, avisoR7, linhasDados } from '../../../testes/fixtures/detector';
import { simularDownload } from '../../../testes/downloadFalso';
import { DATASET_TESTE, renderizarComProvedores } from '../../../testes/renderizar';
import type { Aviso } from '../tipos';
import DrawerLinhas from './DrawerLinhas';

const BASE = `/datasets/${DATASET_TESTE.id}`;

function renderizar(aviso: Aviso, linhas = linhasDados(117, 125)) {
  const api = simularApi([{ caminho: `${BASE}/linhas`, corpo: linhas }]);
  const aoFechar = vi.fn();
  const resultado = renderizarComProvedores(
    <DrawerLinhas datasetId={DATASET_TESTE.id} aviso={aviso} aoFechar={aoFechar} />,
  );
  return { ...resultado, api, aoFechar };
}

describe('DrawerLinhas', () => {
  it('mostra as linhas do exemplo com contexto e as destacadas (7b)', async () => {
    const { api } = renderizar(avisoR4);

    const dialogo = screen.getByRole('dialog', { name: 'Linhas 120 a 122 · peso_kg' });
    expect(within(dialogo).getByText('Atenção')).toBeInTheDocument();
    expect(within(dialogo).getByText('3 linhas destacadas.')).toBeInTheDocument();
    const tabela = await within(dialogo).findByRole('table');
    expect(within(tabela).getAllByRole('row')).toHaveLength(10);
    expect(within(tabela).getAllByText('(destacada)')).toHaveLength(3);
    expect(
      within(tabela).getByRole('rowheader', { name: /^120\s?\(destacada\)$/ }),
    ).toBeInTheDocument();
    expect(within(tabela).getByRole('columnheader', { name: 'peso_kg' })).toHaveClass(
      /colunaAfetada/,
    );
    expect(await within(dialogo).findByText('Linhas 117–125')).toBeInTheDocument();
    expect(chamadasPara(api, 'GET', `${BASE}/linhas`)[0]?.url).toContain('de=117&ate=125');
  });

  it('exemplo com parte das linhas do alerta: diz quantas são ao todo (D172)', () => {
    const exemplo = { linhas: [1, 160], valores: ['89', '94'], texto: '', total_linhas: 45 };

    renderizar({ ...avisoR7, exemplo }, linhasDados(1, 4));

    expect(
      screen.getByText('Destacamos as 2 primeiras das 45 linhas do alerta.'),
    ).toBeInTheDocument();
  });

  it('números de linha com ponto de milhar no título e no rodapé; na tabela, como no arquivo', async () => {
    const linhas = Array.from({ length: 3 }, (_, i) => 1200 + i);
    const exemplo = { linhas, valores: ['70', '75', '80'], texto: '', total_linhas: 3 };

    renderizar({ ...avisoR4, exemplo }, linhasDados(1197, 1205));

    expect(screen.getByRole('dialog', { name: 'Linhas 1.200 a 1.202 · peso_kg' })).toBeVisible();
    const tabela = await screen.findByRole('table');
    expect(within(tabela).getByRole('rowheader', { name: '1197' })).toBeInTheDocument();
    expect(screen.getByText('Linhas 1.197–1.205')).toBeInTheDocument();
  });

  it('linhas distantes viram trechos separados por "…"', async () => {
    const { api } = renderizar(avisoR7, linhasDados(1, 4));

    expect(screen.getByRole('dialog', { name: 'Linhas 1 e 160 · idade' })).toBeInTheDocument();
    expect(await screen.findByText('…')).toBeInTheDocument();
    expect(chamadasPara(api, 'GET', `${BASE}/linhas`).map((chamada) => chamada.url)).toEqual([
      expect.stringContaining('de=1&ate=4'),
      expect.stringContaining('de=157&ate=163'),
    ]);
  });

  it('linhas inteiras (R5): título sem coluna', () => {
    renderizar(avisoR5, linhasDados(41, 50));

    expect(screen.getByRole('dialog', { name: 'Linhas 44 a 47' })).toBeInTheDocument();
  });

  it('"Exportar estas linhas" baixa o CSV com o nome da regra e da coluna', async () => {
    const { nomesBaixados } = simularDownload();
    const { usuario } = renderizar(avisoR4);
    await screen.findByRole('table');

    await usuario.click(screen.getByRole('button', { name: 'Exportar estas linhas' }));

    expect(nomesBaixados).toEqual(['linhas-R4-peso_kg.csv']);
  });

  it('o botão Fechar avisa a página', async () => {
    const { usuario, aoFechar } = renderizar(avisoR4);

    await usuario.click(screen.getByRole('button', { name: 'Fechar' }));

    expect(aoFechar).toHaveBeenCalledOnce();
  });
});
