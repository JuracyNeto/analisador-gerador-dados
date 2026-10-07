import type { ReactNode } from 'react';
import estilos from './BarraAcoes.module.css';

export default function BarraAcoes({ children }: Readonly<{ children: ReactNode }>) {
  return <div className={estilos.barra}>{children}</div>;
}
