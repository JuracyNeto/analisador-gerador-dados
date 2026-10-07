import { useQuery } from '@tanstack/react-query';
import { screen, waitFor } from '@testing-library/react';
import { Outlet, Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { ErroApi, requisitar } from '../../shared/api/cliente';
import { simularApi } from '../../testes/api';
import {
  DATASET_TESTE,
  renderizarComProvedores,
  renderizarComRotas,
} from '../../testes/renderizar';
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

const SESSAO_EXPIRADA = {
  codigo: 'DATASET_NAO_ENCONTRADO',
  mensagem: 'Sua sessão expirou.',
  sugestao: 'Envie o arquivo novamente.',
};

function ComVigia() {
  useSessaoExpirada();
  return null;
}

function DuasConsultasQueFalham() {
  useQuery({
    queryKey: ['datasets', 'ds-1', 'colunas'],
    queryFn: () => requisitar('/datasets/ds-1/colunas'),
  });
  useQuery({
    queryKey: ['datasets', 'ds-1', 'primeira-pagina'],
    queryFn: () => requisitar('/datasets/ds-1'),
  });
  return <p>Tela de variáveis</p>;
}

describe('useSessaoExpirada com várias consultas', () => {
  it('encerra a sessão, avisa uma vez e volta para Importar', async () => {
    simularApi([
      { caminho: '/datasets/ds-1/colunas', status: 404, corpo: SESSAO_EXPIRADA },
      { caminho: '/datasets/ds-1', status: 404, corpo: SESSAO_EXPIRADA },
    ]);

    renderizarComProvedores(
      <>
        <ComVigia />
        <Routes>
          <Route path="/variaveis" element={<DuasConsultasQueFalham />} />
          <Route path="/importar" element={<p>Tela de importar</p>} />
        </Routes>
      </>,
      { rota: '/variaveis', dataset: DATASET_TESTE },
    );

    expect(await screen.findByText('Tela de importar')).toBeInTheDocument();
    expect(screen.getAllByText('Sua sessão expirou.')).toHaveLength(1);
  });
});
