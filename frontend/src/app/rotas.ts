import { type ComponentType, lazy } from 'react';
import { type RouteObject, redirect } from 'react-router';
import { ETAPAS, type Etapa } from './etapas';
import LayoutApp from './layout/LayoutApp';

const PaginaImportar = lazy(() => import('../features/importar/PaginaImportar'));
const PaginaVariaveis = lazy(() => import('../features/variaveis/PaginaVariaveis'));
const PaginaLimpeza = lazy(() => import('../features/limpeza/PaginaLimpeza'));
const PaginaAnalise = lazy(() => import('../features/analise/PaginaAnalise'));
const PaginaBivariada = lazy(() => import('../features/bivariada/PaginaBivariada'));
const PaginaRelatorio = lazy(() => import('../features/relatorio/PaginaRelatorio'));
const PaginaIndisponivel = lazy(() => import('./paginas/PaginaIndisponivel'));

/** Uma página por etapa; as futuras (D60) usam PaginaIndisponivel. */
const PAGINAS = {
  1: PaginaImportar,
  2: PaginaVariaveis,
  3: PaginaLimpeza,
  4: PaginaAnalise,
  5: PaginaBivariada,
  6: PaginaIndisponivel,
  7: PaginaIndisponivel,
  8: PaginaRelatorio,
} as const satisfies Record<Etapa['numero'], ComponentType>;

const irParaInicio = () => redirect(ETAPAS[0].caminho);

export const ROTAS: RouteObject[] = [
  {
    path: '/',
    Component: LayoutApp,
    children: [
      { index: true, loader: irParaInicio },
      ...ETAPAS.map((etapa) => ({ path: etapa.caminho, Component: PAGINAS[etapa.numero] })),
      { path: '*', loader: irParaInicio },
    ],
  },
];
