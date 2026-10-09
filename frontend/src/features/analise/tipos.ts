import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];

export type Analise = Esquemas['Analise'];
export type TabelaFrequencia = Esquemas['TabelaFrequencia'];
export type LinhaFrequencia = Esquemas['LinhaFrequencia'];
export type Medida = Esquemas['Medida'];
export type Moda = Esquemas['Moda'];
export type Separatrizes = Esquemas['Separatrizes'];
export type ValorSeparatriz = Esquemas['ValorSeparatriz'];
export type Dispersao = Esquemas['Dispersao'];
export type Forma = Esquemas['Forma'];
export type Ajuste = Esquemas['Ajuste'];
export type TesteAderencia = Esquemas['TesteAderencia'];
export type Parametro = Esquemas['Parametro'];
export type Figura = Esquemas['Figura'];
export type Formula = Esquemas['Formula'];
export type Posicao = Esquemas['Posicao'];
export type TipoColuna = Esquemas['TipoColuna'];
export type TipoVariavel = Esquemas['TipoVariavel'];
export type TipoSeparatriz = Posicao['tipo'];

/** Abas da tela 4 no M1 (a aba "Forma e distribuição" fica oculta até o M2, D60). */
export type IdAba = 'frequencias' | 'tendencia' | 'separatrizes' | 'dispersao' | 'graficos';

/** Props comuns de todos os painéis de aba (tabela de despacho em ConteudoAnalise). */
export interface PropsPainel {
  analise: Analise;
  datasetId: string;
  atualizando: boolean;
  classes: number | null;
  aoMudarClasses: (k: number) => void;
  tentativas: number | null;
  aoMudarTentativas: (n: number) => void;
}
