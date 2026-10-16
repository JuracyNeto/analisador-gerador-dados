import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, renderHook, type RenderHookResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { type ReactElement, type ReactNode, useEffect, useRef } from 'react';
import { MemoryRouter, type RouteObject, RouterProvider, createMemoryRouter } from 'react-router';
import SessaoProvider from '../shared/sessao/SessaoProvider';
import type { GeradoSessao } from '../shared/sessao/tipos';
import { useSessao } from '../shared/sessao/useSessao';
import TemaProvider from '../shared/tema/TemaProvider';
import ToastProvider from '../shared/ui/ToastProvider';

export type DatasetSessao = NonNullable<ReturnType<typeof useSessao>['dataset']>;

export const DATASET_TESTE: DatasetSessao = { id: 'ds-1', nomeArquivo: 'pesquisa_saude.txt' };

export interface OpcoesRenderizar {
  rota?: string;
  dataset?: DatasetSessao | null;
  ultimoGerado?: GeradoSessao | null;
  cliente?: QueryClient;
}

/** QueryClient novo por teste: sem retentativa e sem coleta de lixo no meio do teste. */
export function criarClienteTeste(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
}

interface PropsDefinirSessao {
  dataset: DatasetSessao | null;
  ultimoGerado: GeradoSessao | null;
}

/**
 * Põe o dataset (e a última geração) na sessão após a 1ª renderização; o formato do
 * localStorage é detalhe do M1.1.
 */
function DefinirSessao({ dataset, ultimoGerado }: Readonly<PropsDefinirSessao>) {
  const sessao = useSessao();
  const definido = useRef(false);
  useEffect(() => {
    if (definido.current || dataset === null) return;
    definido.current = true;
    sessao.definirDataset(dataset);
    if (ultimoGerado !== null) sessao.definirUltimoGerado(ultimoGerado);
  }, [dataset, ultimoGerado, sessao]);
  return null;
}

interface PropsProvedores extends PropsDefinirSessao {
  cliente: QueryClient;
  children: ReactNode;
}

/** Provedores reais, na mesma ordem do App.tsx. */
function Provedores({ cliente, dataset, ultimoGerado, children }: Readonly<PropsProvedores>) {
  return (
    <QueryClientProvider client={cliente}>
      <TemaProvider>
        <SessaoProvider>
          <ToastProvider>
            <DefinirSessao dataset={dataset} ultimoGerado={ultimoGerado} />
            {children}
          </ToastProvider>
        </SessaoProvider>
      </TemaProvider>
    </QueryClientProvider>
  );
}

export function renderizarComRotas(
  rotas: RouteObject[],
  rotaInicial = '/',
  opcoes: Omit<OpcoesRenderizar, 'rota'> = {},
) {
  const roteador = createMemoryRouter(rotas, { initialEntries: [rotaInicial] });
  const clienteConsultas = opcoes.cliente ?? criarClienteTeste();
  const usuario = userEvent.setup();
  const resultado = render(
    <Provedores
      cliente={clienteConsultas}
      dataset={opcoes.dataset ?? null}
      ultimoGerado={opcoes.ultimoGerado ?? null}
    >
      <RouterProvider router={roteador} />
    </Provedores>,
  );
  return { ...resultado, roteador, clienteConsultas, cliente: clienteConsultas, usuario };
}

/** Um elemento numa rota coringa; `<Routes>` dentro dele também funcionam. */
export function renderizarComProvedores(elemento: ReactElement, opcoes: OpcoesRenderizar = {}) {
  const { rota = '/', ...resto } = opcoes;
  return renderizarComRotas([{ path: '*', element: elemento }], rota, resto);
}

export function renderizarHook<R>(hook: () => R, opcoes: OpcoesRenderizar = {}) {
  const { rota = '/', dataset = null, ultimoGerado = null } = opcoes;
  const cliente = opcoes.cliente ?? criarClienteTeste();
  const usuario = userEvent.setup();
  function Envoltorio({ children }: Readonly<{ children: ReactNode }>) {
    return (
      <Provedores cliente={cliente} dataset={dataset} ultimoGerado={ultimoGerado}>
        <MemoryRouter initialEntries={[rota]}>{children}</MemoryRouter>
      </Provedores>
    );
  }
  const resultado: RenderHookResult<R, unknown> = renderHook(hook, { wrapper: Envoltorio });
  return { ...resultado, cliente, usuario };
}
