import { screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';
import { renderizarComRotas } from '../testes/renderizar';
import { ROTAS } from './rotas';

it.each(['/', '/caminho-que-nao-existe'])('%s leva para Importar', async (caminho) => {
  renderizarComRotas(ROTAS, caminho);

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Importar arquivo' }),
  ).toBeInTheDocument();
});

it('etapa futura abre a página que diz quando ela chega', async () => {
  renderizarComRotas(ROTAS, '/bivariada');

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Análise bivariada' }),
  ).toBeInTheDocument();
  expect(
    within(screen.getByRole('main')).getByText('Disponível na versão v0.2.'),
  ).toBeInTheDocument();
});
