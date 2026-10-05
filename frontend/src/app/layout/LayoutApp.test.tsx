import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import { simularMatchMedia } from '../../testes/matchMedia';
import { renderizarComRotas } from '../../testes/renderizar';
import LayoutApp from './LayoutApp';

const ROTAS_TESTE = [
  {
    path: '/',
    element: <LayoutApp />,
    children: [{ path: 'importar', element: <p>Página de importar</p> }],
  },
];

it('monta barra, cabeçalho e conteúdo no <main>', async () => {
  simularMatchMedia(['(min-width: 1280px)']);

  renderizarComRotas(ROTAS_TESTE, '/importar');

  expect(await screen.findByText('Página de importar')).toBeInTheDocument();
  expect(screen.getByRole('main')).toContainElement(screen.getByText('Página de importar'));
  expect(screen.getByRole('navigation', { name: 'Etapas da análise' })).toBeInTheDocument();
  expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Pular para o conteúdo' })).toHaveAttribute(
    'href',
    '#conteudo',
  );
  expect(screen.getByRole('button', { name: 'Recolher barra' })).toHaveAttribute(
    'aria-expanded',
    'true',
  );
});

it('mostra o nome do arquivo da sessão no cabeçalho', async () => {
  localStorage.setItem(
    'sessao',
    JSON.stringify({
      dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' },
      etapasVisitadas: [],
    }),
  );

  renderizarComRotas(ROTAS_TESTE, '/importar');

  expect(await screen.findByText('pesquisa_saude.txt')).toBeInTheDocument();
});

it('em tela média a barra começa recolhida, abre sobreposta e fecha com Esc', async () => {
  renderizarComRotas(ROTAS_TESTE, '/importar');

  await userEvent.click(await screen.findByRole('button', { name: 'Expandir barra' }));
  expect(screen.getByRole('button', { name: 'Fechar a barra de etapas' })).toBeInTheDocument();

  await userEvent.keyboard('{Escape}');
  expect(screen.getByRole('button', { name: 'Expandir barra' })).toBeInTheDocument();
  expect(
    screen.queryByRole('button', { name: 'Fechar a barra de etapas' }),
  ).not.toBeInTheDocument();
});
