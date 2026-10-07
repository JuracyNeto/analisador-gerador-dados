/** Colunas analisáveis do dataset, compartilhadas por Análise e Relatório. */
import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import { opcoesColunas, type TipoColuna } from './dataset';

/** Identificadores ficam fora das análises (D17). */
export function filtrarAnalisaveis(colunas: readonly TipoColuna[]): TipoColuna[] {
  return colunas.filter((coluna) => coluna.tipo !== 'identificador');
}

export function useColunasAnalisaveis(datasetId: string): UseQueryResult<TipoColuna[]> {
  return useQuery({ ...opcoesColunas(datasetId), select: filtrarAnalisaveis });
}
