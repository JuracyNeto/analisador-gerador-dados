import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { DATASET_TESTE, renderizarComProvedores } from '../../testes/renderizar';
import ExigeDataset from './ExigeDataset';

describe('ExigeDataset', () => {
  it('sem dataset, orienta e leva para Importar', async () => {
    const { usuario } = renderizarComProvedores(
      <Routes>
        <Route path="/limpeza" element={<ExigeDataset>{(id) => <p>{id}</p>}</ExigeDataset>} />
        <Route path="/importar" element={<p>Tela de importar</p>} />
      </Routes>,
      { rota: '/limpeza' },
    );

    expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Ir para Importar' }));
    expect(screen.getByText('Tela de importar')).toBeInTheDocument();
  });

  it('com dataset, entrega o id para o conteúdo', async () => {
    renderizarComProvedores(<ExigeDataset>{(id) => <p>Dataset {id}</p>}</ExigeDataset>, {
      dataset: DATASET_TESTE,
    });

    expect(await screen.findByText('Dataset ds-1')).toBeInTheDocument();
  });
});
