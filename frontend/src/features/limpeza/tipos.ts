import type { components } from '../../shared/api/schema';

type Esquemas = components['schemas'];

export type Diagnostico = Esquemas['Diagnostico'];
export type AcaoLimpeza = Esquemas['AcaoLimpeza'];
export type TipoAcao = AcaoLimpeza['acao'];
export type Problema = AcaoLimpeza['problema'];
export type PedidoLimpeza = Esquemas['PedidoLimpeza'];
export type ResultadoLimpeza = Esquemas['ResultadoLimpeza'];
export type EntradaLog = Esquemas['EntradaLog'];
export type Limites = Esquemas['Limites'];
export type ValoresSugeridos = Esquemas['ValoresSugeridos'];
export type ForaDeFaixaColuna = Esquemas['ForaDeFaixaColuna'];
export type InconsistenciaColuna = Esquemas['InconsistenciaColuna'];
export type GrupoGrafias = Esquemas['GrupoGrafias'];
export type Ocorrencia = Esquemas['Ocorrencia'];

export interface OpcaoAcao {
  valor: TipoAcao;
  rotulo: string;
}

/** Uma linha de seção: rótulo (coluna/grupo), descrição, Select de ação e o pedido sem a ação. */
export interface LinhaProblema {
  chave: string;
  rotulo: string;
  descricao: string;
  detalhe: string | null;
  opcoes: readonly OpcaoAcao[];
  acaoBase: Omit<AcaoLimpeza, 'acao'>;
}

export interface SecaoDiagnostico {
  id: Problema;
  titulo: string;
  subtitulo: string;
  cabecalhos: readonly [string, string];
  linhas: readonly LinhaProblema[];
}

export type EscolhasLimpeza = Readonly<Record<string, TipoAcao>>;
