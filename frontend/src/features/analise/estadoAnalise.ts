import { podeTentarDeNovo } from './api';
import type { Analise, TipoColuna } from './tipos';

/** O pedaço de UseQueryResult que a tela usa (UseQueryResult é compatível por estrutura). */
export interface ConsultaSimples<T> {
  status: 'pending' | 'error' | 'success';
  data: T | undefined;
  error: unknown;
  isPlaceholderData: boolean;
  refetch: () => unknown;
}

export type EstadoAnalise =
  | { status: 'carregando-colunas' }
  | { status: 'sem-colunas' }
  | { status: 'calculando'; coluna: string }
  | { status: 'erro'; erro: unknown; tentarDeNovo: (() => void) | null }
  | { status: 'pronta'; analise: Analise; atualizando: boolean };

function estadoDeErro(consulta: ConsultaSimples<unknown>): EstadoAnalise {
  const tentarDeNovo = () => {
    void consulta.refetch();
  };
  return {
    status: 'erro',
    erro: consulta.error,
    tentarDeNovo: podeTentarDeNovo(consulta.error) ? tentarDeNovo : null,
  };
}

export function estadoDaAnalise(
  colunas: ConsultaSimples<TipoColuna[]>,
  analise: ConsultaSimples<Analise>,
  coluna: string | null,
): EstadoAnalise {
  if (colunas.status === 'error') return estadoDeErro(colunas);
  if (colunas.status === 'pending') return { status: 'carregando-colunas' };
  if (coluna === null) return { status: 'sem-colunas' };
  if (analise.status === 'error') return estadoDeErro(analise);
  if (analise.data === undefined) return { status: 'calculando', coluna };
  return { status: 'pronta', analise: analise.data, atualizando: analise.isPlaceholderData };
}
