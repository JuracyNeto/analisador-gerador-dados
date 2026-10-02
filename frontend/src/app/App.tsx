import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Suspense, useState } from 'react';
import { RouterProvider } from 'react-router';
import { roteador } from './rotas';

export default function App() {
  const [clienteConsultas] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={clienteConsultas}>
      <Suspense fallback={<p role="status">Carregando…</p>}>
        <RouterProvider router={roteador} />
      </Suspense>
    </QueryClientProvider>
  );
}
