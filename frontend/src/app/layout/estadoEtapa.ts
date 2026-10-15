import type { Etapa } from '../etapas';

export type EstadoEtapa = 'concluida' | 'atual' | 'disponivel' | 'bloqueada';

export interface ContextoEtapas {
  atual: number | null;
  temDataset: boolean;
  visitadas: ReadonlySet<number>;
}

const ETAPA_IMPORTAR = 1;

/** componentes.md §BarraEtapas: sem dataset só a etapa 1 abre. */
export function estadoDaEtapa(etapa: Etapa, contexto: ContextoEtapas): EstadoEtapa {
  if (etapa.numero === contexto.atual) return 'atual';
  if (!contexto.temDataset) return etapa.numero === ETAPA_IMPORTAR ? 'disponivel' : 'bloqueada';
  return contexto.visitadas.has(etapa.numero) ? 'concluida' : 'disponivel';
}

/** Texto do tooltip: só na barra recolhida, com o nome da etapa. */
export function dicaDaEtapa(etapa: Etapa, recolhida: boolean): string | null {
  return recolhida ? etapa.nome : null;
}
