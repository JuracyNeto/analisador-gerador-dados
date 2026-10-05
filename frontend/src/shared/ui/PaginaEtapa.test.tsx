import { screen, waitFor } from '@testing-library/react';
import { expect, it } from 'vitest';
import { renderizarComProvedores } from '../../testes/renderizar';
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
