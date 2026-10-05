import { type Etapa, ehEtapaFutura } from '../etapas';
import { TEXTOS_APP } from '../textos';

export type EstadoEtapa = 'concluida' | 'atual' | 'disponivel' | 'bloqueada';

export interface ContextoEtapas {
  atual: number | null;
  temDataset: boolean;
  visitadas: ReadonlySet<number>;
}

const ETAPA_IMPORTAR = 1;

/** componentes.md §BarraEtapas + D60: futuras sempre bloqueadas; sem dataset só a etapa 1 abre. */
export function estadoDaEtapa(etapa: Etapa, contexto: ContextoEtapas): EstadoEtapa {
  if (ehEtapaFutura(etapa)) return 'bloqueada';
  if (etapa.numero === contexto.atual) return 'atual';
  if (!contexto.temDataset) return etapa.numero === ETAPA_IMPORTAR ? 'disponivel' : 'bloqueada';
  return contexto.visitadas.has(etapa.numero) ? 'concluida' : 'disponivel';
}

/** Texto do tooltip: motivo das futuras; na barra recolhida, o nome (+ motivo). */
export function dicaDaEtapa(etapa: Etapa, recolhida: boolean): string | null {
  const motivo = ehEtapaFutura(etapa) ? TEXTOS_APP.disponivelNaVersao(etapa.disponivelEm) : null;
  if (!recolhida) return motivo;
  return motivo === null ? etapa.nome : `${etapa.nome}. ${motivo}`;
}
