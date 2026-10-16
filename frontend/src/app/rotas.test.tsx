import { screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { renderizarComRotas } from '../testes/renderizar';
import { ROTAS } from './rotas';

it.each(['/', '/caminho-que-nao-existe'])('%s leva para Importar', async (caminho) => {
  renderizarComRotas(ROTAS, caminho);

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Importar arquivo' }),
  ).toBeInTheDocument();
});

it('/detector abre a etapa 7', async () => {
  renderizarComRotas(ROTAS, '/detector');

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Detector de dados artificiais' }),
  ).toBeInTheDocument();
  expect(screen.queryByText(/Disponível na versão/)).not.toBeInTheDocument();
});

it('/gerador abre a etapa 6', async () => {
  renderizarComRotas(ROTAS, '/gerador');

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Gerador de dados' }),
  ).toBeInTheDocument();
  expect(screen.getByRole('tab', { name: 'Univariado' })).toBeInTheDocument();
});

it('/bivariada abre a etapa 5', async () => {
  renderizarComRotas(ROTAS, '/bivariada');

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Análise bivariada' }),
  ).toBeInTheDocument();
});
