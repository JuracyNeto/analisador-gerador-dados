import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';
import SessaoProvider from './SessaoProvider';
import { useSessao } from './useSessao';

function Painel() {
  const { dataset, definirDataset, encerrar, etapasVisitadas, marcarVisitada } = useSessao();
  return (
    <div>
      <p>{dataset ? dataset.nomeArquivo : 'sem arquivo'}</p>
      <p>visitadas: {[...etapasVisitadas].join(',')}</p>
      <button
        type="button"
        onClick={() => {
          definirDataset({ id: 'd2', nomeArquivo: 'notas_turma.csv' });
        }}
      >
        importar
      </button>
      <button
        type="button"
        onClick={() => {
          marcarVisitada(3);
        }}
      >
        visitar 3
      </button>
      <button type="button" onClick={encerrar}>
        encerrar
      </button>
    </div>
  );
}

function renderizar() {
  render(
    <SessaoProvider>
      <Painel />
    </SessaoProvider>,
  );
}

function sessaoSalva(): unknown {
  return JSON.parse(localStorage.getItem('sessao') ?? 'null');
}

it('começa vazia', () => {
  renderizar();

  expect(screen.getByText('sem arquivo')).toBeInTheDocument();
});

it('restaura a sessão salva', () => {
  localStorage.setItem(
    'sessao',
    JSON.stringify({
      dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' },
      etapasVisitadas: [1, 2],
    }),
  );

  renderizar();

  expect(screen.getByText('pesquisa_saude.txt')).toBeInTheDocument();
  expect(screen.getByText('visitadas: 1,2')).toBeInTheDocument();
});

it('trocar de dataset zera as etapas visitadas e salva', async () => {
  localStorage.setItem(
    'sessao',
    JSON.stringify({
      dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' },
      etapasVisitadas: [1, 2],
    }),
  );
  renderizar();

  await userEvent.click(screen.getByRole('button', { name: 'importar' }));
  await userEvent.click(screen.getByRole('button', { name: 'visitar 3' }));

  expect(screen.getByText('notas_turma.csv')).toBeInTheDocument();
  expect(sessaoSalva()).toEqual({
    dataset: { id: 'd2', nomeArquivo: 'notas_turma.csv' },
    etapasVisitadas: [3],
  });
});

it('encerrar limpa a sessão', async () => {
  renderizar();
  await userEvent.click(screen.getByRole('button', { name: 'importar' }));

  await userEvent.click(screen.getByRole('button', { name: 'encerrar' }));

  expect(screen.getByText('sem arquivo')).toBeInTheDocument();
  expect(sessaoSalva()).toEqual({ dataset: null, etapasVisitadas: [] });
});
