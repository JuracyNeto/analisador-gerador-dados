import { useQuery } from '@tanstack/react-query';
import { screen, waitFor } from '@testing-library/react';
import { Outlet } from 'react-router';
import { expect, it } from 'vitest';
import { ErroApi } from '../../shared/api/cliente';
import { renderizarComRotas } from '../../testes/renderizar';
import { useSessaoExpirada } from './useSessaoExpirada';

function PaginaQueFalha({ codigo }: Readonly<{ codigo: string }>) {
  useQuery({
    queryKey: ['teste', codigo],
    queryFn: () =>
      Promise.reject(
        new ErroApi(404, {
          codigo,
          mensagem: 'Sua sessão expirou.',
          sugestao: 'Envie o arquivo novamente.',
        }),
      ),
  });
  return <p>Análise</p>;
}

function Vigia() {
  useSessaoExpirada();
  return <Outlet />;
}

function renderizar(codigo: string) {
  localStorage.setItem(
    'sessao',
    JSON.stringify({
      dataset: { id: 'd1', nomeArquivo: 'pesquisa_saude.txt' },
      etapasVisitadas: [1, 2],
    }),
  );
  return renderizarComRotas(
    [
      {
        path: '/',
        element: <Vigia />,
        children: [
          { path: 'analise', element: <PaginaQueFalha codigo={codigo} /> },
          { path: 'importar', element: <p>Importar</p> },
        ],
      },
    ],
    '/analise',
  );
}

it('DATASET_NAO_ENCONTRADO encerra a sessão, avisa e volta para Importar', async () => {
  renderizar('DATASET_NAO_ENCONTRADO');

  expect(await screen.findByText('Importar')).toBeInTheDocument();
  expect(screen.getByRole('alert')).toHaveTextContent('Sua sessão expirou.');
  const salvo: unknown = JSON.parse(localStorage.getItem('sessao') ?? 'null');
  expect(salvo).toEqual({ dataset: null, etapasVisitadas: [] });
});

it('outros erros não mexem na sessão', async () => {
  const { clienteConsultas } = renderizar('COLUNA_NAO_ENCONTRADA');

  await waitFor(() => {
    expect(clienteConsultas.getQueryState(['teste', 'COLUNA_NAO_ENCONTRADA'])?.status).toBe(
      'error',
    );
  });
  expect(screen.getByText('Análise')).toBeInTheDocument();
  expect(localStorage.getItem('sessao')).toContain('pesquisa_saude.txt');
});
