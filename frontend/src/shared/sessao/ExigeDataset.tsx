import type { ReactNode } from 'react';
import SemDataset from './SemDataset';
import { useSessao } from './useSessao';

interface PropsExigeDataset {
  children: (datasetId: string) => ReactNode;
}

/** Entrega o id do dataset da sessão ao conteúdo; sem dataset, mostra `SemDataset`. */
export default function ExigeDataset({ children }: Readonly<PropsExigeDataset>) {
  const sessao = useSessao();
  return sessao.dataset === null ? <SemDataset /> : <>{children(sessao.dataset.id)}</>;
}
