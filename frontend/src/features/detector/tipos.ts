import type { components } from '../../shared/api/schema';
import type { Severidade } from '../../shared/ui/severidades';

type Esquemas = components['schemas'];

export type Aviso = Esquemas['AvisoDetector'];
export type ResultadoDetector = Esquemas['ResultadoDetector'];
export type ResumoDetector = Esquemas['ResumoDetector'];
export type RegraNaoAplicada = Esquemas['RegraNaoAplicada'];
export type DetalhesAviso = Esquemas['DetalhesAviso'];
export type LinhaDados = Esquemas['LinhaDados'];
export type { Severidade };

/** Como a lista de alertas é agrupada (Segmented "Agrupar por"). */
export type Agrupamento = 'coluna' | 'regra';

/** Filtros da tela 7, guardados na URL (D140). */
export interface FiltrosDetector {
  severidades: ReadonlySet<Severidade>;
  agrupar: Agrupamento;
}
