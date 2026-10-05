import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { type RouteObject, RouterProvider, createMemoryRouter } from 'react-router';
import SessaoProvider from '../shared/sessao/SessaoProvider';
import TemaProvider from '../shared/tema/TemaProvider';
import ToastProvider from '../shared/ui/ToastProvider';

export function renderizarComRotas(rotas: RouteObject[], rotaInicial = '/') {
  const roteador = createMemoryRouter(rotas, { initialEntries: [rotaInicial] });
  const clienteConsultas = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const resultado = render(
    <QueryClientProvider client={clienteConsultas}>
      <TemaProvider>
        <SessaoProvider>
          <ToastProvider>
            <RouterProvider router={roteador} />
          </ToastProvider>
        </SessaoProvider>
      </TemaProvider>
    </QueryClientProvider>,
  );
  return { ...resultado, roteador, clienteConsultas };
}

export function renderizarComProvedores(elemento: ReactElement) {
  return renderizarComRotas([{ path: '*', element: elemento }]);
}
