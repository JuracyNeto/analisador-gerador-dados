import { screen, waitFor } from '@testing-library/react';
import { expect, it } from 'vitest';
import { Link } from 'react-router';
import { renderizarComProvedores, renderizarComRotas } from '../../testes/renderizar';
import PaginaEtapa from './PaginaEtapa';

function pagina() {
  return (
    <PaginaEtapa
      etapa={2}
      titulo="Variáveis"
      ajuda="Classificamos cada coluna pelo que ela contém."
    >
      <p>conteúdo da etapa</p>
    </PaginaEtapa>
  );
}

it('mostra "Etapa N de 8", o título como h1, a ajuda e o conteúdo', async () => {
  renderizarComProvedores(pagina());

  expect(await screen.findByRole('heading', { level: 1, name: 'Variáveis' })).toBeInTheDocument();
  expect(screen.getByText('Etapa 2 de 8')).toBeInTheDocument();
  expect(screen.getByText('Classificamos cada coluna pelo que ela contém.')).toBeInTheDocument();
  expect(screen.getByText('conteúdo da etapa')).toBeInTheDocument();
  expect(document.title).toBe('Variáveis · Analisador e Gerador de Dados');
});

it('marca a etapa como visitada na sessão', async () => {
  localStorage.setItem(
    'sessao',
    JSON.stringify({ dataset: { id: 'd1', nomeArquivo: 'a.csv' }, etapasVisitadas: [1] }),
  );

  renderizarComProvedores(pagina());

  await waitFor(() => {
    expect(localStorage.getItem('sessao')).toContain('"etapasVisitadas":[1,2]');
  });
});

/** Cada etapa do app é um componente próprio: trocar de rota monta a página de novo. */
function EtapaImportar() {
  return (
    <PaginaEtapa etapa={1} titulo="Importar arquivo" ajuda="Envie sua tabela.">
      <Link to="/variaveis">Ir para Variáveis</Link>
    </PaginaEtapa>
  );
}

function EtapaVariaveis() {
  return pagina();
}

const ROTAS_FOCO = [
  { path: '/importar', element: <EtapaImportar /> },
  { path: '/variaveis', element: <EtapaVariaveis /> },
];

it('na primeira carga, o foco não vai para o título', async () => {
  renderizarComRotas(ROTAS_FOCO, '/importar');

  const titulo = await screen.findByRole('heading', { level: 1, name: 'Importar arquivo' });
  expect(titulo).not.toHaveFocus();
});

it('ao trocar de etapa, o foco vai para o título (o leitor de tela anuncia a etapa)', async () => {
  const { usuario } = renderizarComRotas(ROTAS_FOCO, '/importar');

  await usuario.click(await screen.findByRole('link', { name: 'Ir para Variáveis' }));

  const titulo = await screen.findByRole('heading', { level: 1, name: 'Variáveis' });
  expect(titulo).toHaveFocus();
  expect(titulo).toHaveAttribute('tabindex', '-1');
});
