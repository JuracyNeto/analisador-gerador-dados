import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactElement } from 'react';
import { expect, it } from 'vitest';
import { DATASET_TESTE, renderizarComRotas } from '../../testes/renderizar';
import Cabecalho from './Cabecalho';

function renderizar(cabecalho: ReactElement, dataset: typeof DATASET_TESTE | null = null) {
  renderizarComRotas(
    [
      { path: '/', element: cabecalho },
      { path: '/importar', element: <p>Tela de importar</p> },
    ],
    '/',
    { dataset },
  );
}

it('sem arquivo mostra o aviso e não oferece troca', () => {
  renderizar(<Cabecalho />);

  expect(screen.getByText('Nenhum arquivo importado')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Trocar arquivo' })).not.toBeInTheDocument();
});

it('com arquivo mostra nome e tamanho; "Trocar arquivo" encerra a sessão e leva para Importar', async () => {
  renderizar(
    <Cabecalho nomeArquivo="pesquisa_saude.txt" nLinhas={230} nColunas={8} />,
    DATASET_TESTE,
  );

  expect(screen.getByText('pesquisa_saude.txt')).toBeInTheDocument();
  expect(screen.getByText('230 linhas × 8 colunas')).toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Trocar arquivo' }));
  expect(await screen.findByText('Tela de importar')).toBeInTheDocument();
  // Sem sessão, Importar mostra a área de envio (1b) em vez do arquivo atual (1a).
  expect(JSON.parse(localStorage.getItem('sessao') ?? '{}')).toMatchObject({ dataset: null });
});

it('usa singular e separador de milhar', () => {
  renderizar(<Cabecalho nomeArquivo="grande.csv" nLinhas={1234} nColunas={1} />);

  expect(screen.getByText('1.234 linhas × 1 coluna')).toBeInTheDocument();
});

it('alterna o tema por clique e por setas', async () => {
  renderizar(<Cabecalho />);
  const grupo = screen.getByRole('radiogroup', { name: 'Tema' });

  await userEvent.click(within(grupo).getByRole('radio', { name: 'Tema escuro' }));
  expect(document.documentElement).toHaveAttribute('data-tema', 'escuro');
  expect(within(grupo).getByRole('radio', { name: 'Tema escuro' })).toHaveAttribute(
    'aria-checked',
    'true',
  );

  await userEvent.keyboard('{ArrowLeft}');
  expect(document.documentElement).toHaveAttribute('data-tema', 'claro');
  expect(within(grupo).getByRole('radio', { name: 'Tema claro' })).toHaveFocus();
});
