import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { RouterProvider } from 'react-router';
import { deveTentarDeNovo } from '../shared/api/classificarErro';
import SessaoProvider from '../shared/sessao/SessaoProvider';
import TemaProvider from '../shared/tema/TemaProvider';
import ToastProvider from '../shared/ui/ToastProvider';
import { roteador } from './roteador';

export default function App() {
  const [clienteConsultas] = useState(
    () => new QueryClient({ defaultOptions: { queries: { retry: deveTentarDeNovo } } }),
  );

  return (
    <QueryClientProvider client={clienteConsultas}>
      <TemaProvider>
        <SessaoProvider>
          <ToastProvider>
            <RouterProvider router={roteador} />
          </ToastProvider>
        </SessaoProvider>
      </TemaProvider>
    </QueryClientProvider>
  );
}
