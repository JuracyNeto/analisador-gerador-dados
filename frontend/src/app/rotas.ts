import { lazy } from 'react';
import { createBrowserRouter } from 'react-router';

const PaginaInicio = lazy(() => import('../features/inicio/PaginaInicio'));

export const roteador = createBrowserRouter([{ path: '/', Component: PaginaInicio }]);
