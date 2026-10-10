import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];

export type Bivariada = Esquemas['Bivariada'];
export type Previsao = Esquemas['Previsao'];
export type MatrizCorrelacao = Esquemas['MatrizCorrelacao'];
export type Figura = Esquemas['Figura'];
export type TipoColuna = Esquemas['TipoColuna'];

/** Coluna X (explica) e coluna Y (é explicada). */
export interface Par {
  x: string;
  y: string;
}
